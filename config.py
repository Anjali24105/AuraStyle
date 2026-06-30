import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aurastyle-super-secret-key-13579')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1', 't']
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')

    # MongoDB connection settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.environ.get('DB_NAME', 'aurastyle_db')
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'products')

    # CLIP Model Configuration
    # We use OpenAI's ViT-B/32 CLIP model (512-dimensional embeddings)
    CLIP_MODEL_NAME = os.environ.get('CLIP_MODEL_NAME', 'openai/clip-vit-base-patch32')
    
    # Device configuration: use GPU if available, else fallback to CPU
    import torch
    DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

    # Project Root
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # Media and Upload Paths
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'products')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

    # Application settings
    TOP_K_RESULTS = 10
