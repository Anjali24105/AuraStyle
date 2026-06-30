import os
import logging
import numpy as np
from flask import Flask, render_template, request, jsonify
from config import Config
from utils.database import db_manager
from utils.embedder import (
    get_text_embedding,
    get_image_embedding,
    find_top_matches
)

# Configure logging format and level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    """Serves the primary Single Page Application (SPA) dashboard."""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error loading homepage template: {e}")
        return "Internal Server Error: Missing interface template.", 500

@app.route('/api/products', methods=['GET'])
def get_products():
    """Retrieves all products from MongoDB and returns them as a JSON array."""
    try:
        collection = db_manager.get_collection()
        # Find all products; exclude embedding arrays to keep payload light for bulk fetching
        products_cursor = collection.find({}, {"embedding": 0})
        
        products_list = []
        for doc in products_cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization
            products_list.append(doc)
            
        return jsonify(products_list), 200
    except Exception as e:
        logger.error(f"Failed to retrieve products from database: {e}")
        return jsonify({"error": "Failed to fetch products from the database."}), 500

@app.route('/api/search', methods=['POST'])
def search_products():
    """Performs multimodal similarity search on fashion catalog.
    
    Expects multi-part form data containing:
    - text: Optional string query (can be regular search or speech-to-text transcript).
    - image: Optional image file stream upload.
    - text_weight: Optional float value representing query influence ratio (default: 0.5).
    - image_weight: Optional float value representing image influence ratio (default: 0.5).
    
    If both text and image are supplied, the embeddings are combined and normalized.
    """
    try:
        # 1. Parse incoming parameters
        text_query = request.form.get('text', '').strip()
        image_file = request.files.get('image')
        
        # Read search weights with safe fallbacks
        try:
            w_text = float(request.form.get('text_weight', 0.5))
            w_image = float(request.form.get('image_weight', 0.5))
        except ValueError:
            w_text, w_image = 0.5, 0.5

        if not text_query and not image_file:
            return jsonify({"error": "Provide at least a text query or an uploaded image to search."}), 400

        text_emb = []
        image_emb = []

        # 2. Extract embeddings
        if text_query:
            logger.info(f"Generating embedding for text query: '{text_query}'")
            text_emb = get_text_embedding(text_query)

        if image_file:
            logger.info(f"Generating embedding for uploaded image: '{image_file.filename}'")
            image_emb = get_image_embedding(image_file.stream)

        # 3. Combine embeddings if both exist, otherwise use the single active vector
        query_embedding = []
        if text_emb and image_emb:
            logger.info(f"Combining text ({w_text}) and image ({w_image}) embeddings...")
            combined = w_text * np.array(text_emb) + w_image * np.array(image_emb)
            # Re-normalize combined vector onto hypersphere
            norm = np.linalg.norm(combined)
            if norm > 0:
                combined = combined / norm
            query_embedding = combined.tolist()
        elif text_emb:
            query_embedding = text_emb
        elif image_emb:
            query_embedding = image_emb
        else:
            return jsonify({"error": "Unable to generate search embeddings from query inputs."}), 500

        # 4. Fetch all catalog items with valid embeddings from MongoDB
        collection = db_manager.get_collection()
        products = list(collection.find({"embedding": {"$ne": None}}))
        
        if not products:
            logger.warning("No products found in the database with pre-computed embeddings. Run reindexing.")
            return jsonify({
                "message": "No products are indexed yet. Please run the administrative reindexing routine.",
                "products": []
            }), 200

        # 5. Compute cosine similarities and extract top-k matches with hybrid ranking
        results = find_top_matches(
            query_embedding=query_embedding,
            products=products,
            top_k=Config.TOP_K_RESULTS,
            query_text_embedding=text_emb,
            query_text=text_query
        )
        logger.info(f"Successfully matched and returned top {len(results)} matches.")
        
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Multimodal search error: {e}", exc_info=True)
        return jsonify({"error": "An internal error occurred during the search processing."}), 500

@app.route('/api/admin/reindex', methods=['POST'])
def reindex_products():
    """Administrative endpoint to compute/recompute CLIP embeddings for catalog items.
    
    Reads all products in the database and evaluates their local image files.
    """
    try:
        collection = db_manager.get_collection()
        products = list(collection.find({}))
        
        if not products:
            return jsonify({"message": "No products found in the database to index."}), 200
            
        logger.info(f"Beginning index rebuilding for {len(products)} products...")
        reindexed_count = 0
        skipped_count = 0

        # Create output directories if missing
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            logger.info(f"Created products folder directory at: {Config.UPLOAD_FOLDER}")

        for prod in products:
            image_filename = prod.get("image_filename")
            prod_name = prod.get("name", "Unnamed Product")
            
            if not image_filename:
                logger.warning(f"Product '{prod_name}' lacks an image_filename. Skipping.")
                skipped_count += 1
                continue
                
            local_image_path = os.path.join(Config.UPLOAD_FOLDER, image_filename)
            
            if not os.path.exists(local_image_path):
                logger.warning(f"Product image file not found at local path: {local_image_path}. Skipping.")
                skipped_count += 1
                continue
                
            try:
                # Generate CLIP image embedding
                embedding = get_image_embedding(local_image_path)
                
                # Generate CLIP text metadata embedding
                metadata_text = f"A {prod.get('category', '')} named {prod.get('name', '')}. {prod.get('description', '')} Tags: {', '.join(prod.get('tags', []))}"
                text_embedding = get_text_embedding(metadata_text)
                
                collection.update_one(
                    {"_id": prod["_id"]},
                    {"$set": {
                        "embedding": embedding,
                        "text_embedding": text_embedding
                    }}
                )
                reindexed_count += 1
            except Exception as item_err:
                logger.error(f"Failed to generate embedding for '{prod_name}': {item_err}")
                skipped_count += 1
                
        logger.info(f"Reindexing execution finished. Indexed: {reindexed_count}, Skipped: {skipped_count}")
        return jsonify({
            "status": "success",
            "message": "Reindexing process completed.",
            "indexed_count": reindexed_count,
            "skipped_count": skipped_count
        }), 200
        
    except Exception as e:
        logger.error(f"Critical error during administrative reindexing: {e}")
        return jsonify({"error": "Failed to complete reindexing due to an internal server error."}), 500

if __name__ == '__main__':
    # Start the development server
    logger.info("Starting AuraStyle backend services...")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
