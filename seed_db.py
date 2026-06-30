import logging
from datetime import datetime
from utils.database import db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample fashion dataset (20 products)
SAMPLE_PRODUCTS = [
    # Category: Tops
    {
        "name": "Classic White Linen Button-Up",
        "description": "A breathable and lightweight white linen shirt perfect for casual summer wear or smart-casual layering.",
        "category": "Tops",
        "price": 59.99,
        "rating": 4.5,
        "image_filename": "classic_white_linen.jpg",
        "image_path": "/static/images/products/classic_white_linen.jpg",
        "tags": ["white", "shirt", "linen", "casual", "summer", "classic"]
    },
    {
        "name": "Vintage Graphic Tee",
        "description": "Soft cotton graphic tee with a distressed retro-style print, relaxed fit and crewneck collar.",
        "category": "Tops",
        "price": 28.50,
        "rating": 4.2,
        "image_filename": "vintage_graphic_tee.jpg",
        "image_path": "/static/images/products/vintage_graphic_tee.jpg",
        "tags": ["shirt", "t-shirt", "cotton", "casual", "vintage", "graphic"]
    },
    {
        "name": "Silk Floral Blouse",
        "description": "Elegantly draped mulberry silk blouse featuring an intricate floral pattern and subtle ruffle details.",
        "category": "Tops",
        "price": 89.00,
        "rating": 4.7,
        "image_filename": "silk_floral_blouse.jpg",
        "image_path": "/static/images/products/silk_floral_blouse.jpg",
        "tags": ["blouse", "silk", "floral", "elegant", "office", "colorful"]
    },
    
    # Category: Dresses
    {
        "name": "Emerald Velvet Evening Gown",
        "description": "A luxury emerald green velvet evening dress with a dramatic high slit, sweetheart neckline, and open back design.",
        "category": "Dresses",
        "price": 189.99,
        "rating": 4.9,
        "image_filename": "emerald_velvet_gown.jpg",
        "image_path": "/static/images/products/emerald_velvet_gown.jpg",
        "tags": ["dress", "velvet", "emerald", "green", "evening", "formal", "luxury"]
    },
    {
        "name": "Bohemian Floral Maxi Dress",
        "description": "Flowy tiered maxi dress with a colorful bohemian pattern, balloon sleeves, and drawstring waist tie.",
        "category": "Dresses",
        "price": 74.99,
        "rating": 4.6,
        "image_filename": "boho_maxi_dress.jpg",
        "image_path": "/static/images/products/boho_maxi_dress.jpg",
        "tags": ["dress", "maxi", "bohemian", "floral", "spring", "casual"]
    },
    {
        "name": "Little Black Dress",
        "description": "A classic form-fitting black sheath dress with a clean square neckline, suitable for cocktail events and dinners.",
        "category": "Dresses",
        "price": 95.00,
        "rating": 4.8,
        "image_filename": "little_black_dress.jpg",
        "image_path": "/static/images/products/little_black_dress.jpg",
        "tags": ["dress", "black", "sheath", "cocktail", "classic", "minimalist"]
    },

    # Category: Bottoms
    {
        "name": "High-Waisted Distressed Skinny Jeans",
        "description": "Stretchy high-waisted denim jeans featuring light-wash fading and subtle distressed rips at the knees.",
        "category": "Bottoms",
        "price": 65.00,
        "rating": 4.4,
        "image_filename": "high_waist_skinny_jeans.jpg",
        "image_path": "/static/images/products/high_waist_skinny_jeans.jpg",
        "tags": ["jeans", "denim", "high-waisted", "skinny", "blue", "casual"]
    },
    {
        "name": "Tailored Beige Pleated Chinos",
        "description": "Smart pleated cotton trousers in a versatile beige hue, boasting a modern tapered leg and buttoned rear pockets.",
        "category": "Bottoms",
        "price": 79.99,
        "rating": 4.3,
        "image_filename": "beige_pleated_chinos.jpg",
        "image_path": "/static/images/products/beige_pleated_chinos.jpg",
        "tags": ["pants", "chinos", "trousers", "beige", "tailored", "office"]
    },
    {
        "name": "Activewear Performance Leggings",
        "description": "High-performance moisture-wicking compression leggings in black, with side pockets for smartphone storage.",
        "category": "Bottoms",
        "price": 45.00,
        "rating": 4.7,
        "image_filename": "activewear_leggings.jpg",
        "image_path": "/static/images/products/activewear_leggings.jpg",
        "tags": ["pants", "leggings", "activewear", "black", "compression", "gym"]
    },

    # Category: Outerwear
    {
        "name": "Distressed Denim Jacket",
        "description": "Classic wash structured denim jacket with button chest pockets and adjustable waist tabs.",
        "category": "Outerwear",
        "price": 85.00,
        "rating": 4.5,
        "image_filename": "distressed_denim_jacket.jpg",
        "image_path": "/static/images/products/distressed_denim_jacket.jpg",
        "tags": ["jacket", "denim", "blue", "outerwear", "casual"]
    },
    {
        "name": "Classic Double-Breasted Trench Coat",
        "description": "A rain-resistant double-breasted khaki trench coat with adjustable waist belt and elegant tortoiseshell buttons.",
        "category": "Outerwear",
        "price": 149.50,
        "rating": 4.8,
        "image_filename": "classic_trench_coat.jpg",
        "image_path": "/static/images/products/classic_trench_coat.jpg",
        "tags": ["coat", "trench", "khaki", "outerwear", "raincoat", "classic"]
    },
    {
        "name": "Sleek Black Leather Biker Jacket",
        "description": "Heavyweight asymmetrical zip genuine leather jacket with silver hardware detailing for a bold look.",
        "category": "Outerwear",
        "price": 249.99,
        "rating": 4.9,
        "image_filename": "leather_biker_jacket.jpg",
        "image_path": "/static/images/products/leather_biker_jacket.jpg",
        "tags": ["jacket", "leather", "black", "biker", "outerwear", "premium"]
    },

    # Category: Footwear
    {
        "name": "Minimalist White Leather Sneakers",
        "description": "Clean silhouette white leather low-top sneakers featuring a padded collar and reinforced rubber soles.",
        "category": "Footwear",
        "price": 110.00,
        "rating": 4.6,
        "image_filename": "minimalist_white_sneakers.jpg",
        "image_path": "/static/images/products/minimalist_white_sneakers.jpg",
        "tags": ["shoes", "sneakers", "white", "leather", "minimalist", "footwear"]
    },
    {
        "name": "Italian Leather Derby Shoes",
        "description": "Premium hand-burnished brown leather Derby dress shoes with dynamic stitching and wooden stacked heel.",
        "category": "Footwear",
        "price": 175.00,
        "rating": 4.7,
        "image_filename": "italian_leather_derbys.jpg",
        "image_path": "/static/images/products/italian_leather_derbys.jpg",
        "tags": ["shoes", "derby", "leather", "brown", "dress-shoes", "formal"]
    },
    {
        "name": "Suede Ankle Boots",
        "description": "Tan colored soft suede ankle boots featuring a sturdy block heel and easy slip-on elastic side gussets.",
        "category": "Footwear",
        "price": 125.00,
        "rating": 4.4,
        "image_filename": "suede_ankle_boots.jpg",
        "image_path": "/static/images/products/suede_ankle_boots.jpg",
        "tags": ["shoes", "boots", "suede", "tan", "autumn", "footwear"]
    },

    # Category: Accessories
    {
        "name": "Classic Aviator Sunglasses",
        "description": "Gold-frame aviator sunglasses featuring polarized green lenses and 100% UV protection rating.",
        "category": "Accessories",
        "price": 45.00,
        "rating": 4.3,
        "image_filename": "aviator_sunglasses.jpg",
        "image_path": "/static/images/products/aviator_sunglasses.jpg",
        "tags": ["sunglasses", "aviator", "gold", "summer", "eyewear", "accessory"]
    },
    {
        "name": "Minimalist Quartz Wristwatch",
        "description": "Slim rose-gold wristwatch with a white dial face, quartz movement, and premium gray leather strap.",
        "category": "Accessories",
        "price": 135.00,
        "rating": 4.6,
        "image_filename": "quartz_wristwatch.jpg",
        "image_path": "/static/images/products/quartz_wristwatch.jpg",
        "tags": ["watch", "wristwatch", "rose-gold", "leather", "timepiece", "accessory"]
    },
    {
        "name": "Structured Saffiano Leather Tote Bag",
        "description": "A spacious black Saffiano leather tote bag featuring a zipped divider compartment and gold logo hardware.",
        "category": "Accessories",
        "price": 195.00,
        "rating": 4.8,
        "image_filename": "saffiano_tote_bag.jpg",
        "image_path": "/static/images/products/saffiano_tote_bag.jpg",
        "tags": ["bag", "tote", "leather", "black", "handbag", "accessory"]
    },
    {
        "name": "Cozy Cable-Knit Wool Beanie",
        "description": "Thickly ribbed gray wool beanie made of soft merino fibers, featuring a folded cuff for extra warmth.",
        "category": "Accessories",
        "price": 25.00,
        "rating": 4.5,
        "image_filename": "cable_knit_beanie.jpg",
        "image_path": "/static/images/products/cable_knit_beanie.jpg",
        "tags": ["hat", "beanie", "wool", "gray", "knit", "winter", "accessory"]
    },
    {
        "name": "Italian Silk Pocket Square",
        "description": "A luxurious dark blue silk pocket square with gold polka dot patterns, made and hand-rolled in Italy.",
        "category": "Accessories",
        "price": 35.00,
        "rating": 4.2,
        "image_filename": "silk_pocket_square.jpg",
        "image_path": "/static/images/products/silk_pocket_square.jpg",
        "tags": ["pocket-square", "silk", "blue", "gold", "suit", "formal", "accessory"]
    }
]

def seed_database():
    """Drops existing products, and seeds the MongoDB database with initial metadata."""
    try:
        # Fetch the MongoDB collection
        collection = db_manager.get_collection()
        
        # Clear existing catalog to start fresh
        logger.info("Clearing existing products in database...")
        deleted_result = collection.delete_many({})
        logger.info(f"Cleared {deleted_result.deleted_count} old products.")

        # Prepare documents with additional fields like creation date and placeholder embeddings
        documents = []
        for index, item in enumerate(SAMPLE_PRODUCTS):
            doc = item.copy()
            doc["embedding"] = None  # Embeddings to be generated by CLIP in subsequent phases
            doc["created_at"] = datetime.utcnow()
            documents.append(doc)

        # Bulk insert
        logger.info(f"Inserting {len(documents)} sample fashion products...")
        inserted_result = collection.insert_many(documents)
        logger.info(f"Database seeded successfully. Inserted IDs: {len(inserted_result.inserted_ids)}")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
    finally:
        db_manager.close()

if __name__ == "__main__":
    logger.info("Initializing AuraStyle Database Seeding Script...")
    seed_database()
