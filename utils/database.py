import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import Config

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages the MongoDB connection and product catalog collection operations."""
    
    def __init__(self):
        self.uri = Config.MONGO_URI
        self.db_name = Config.DB_NAME
        self.collection_name = Config.COLLECTION_NAME
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        """Establishes connection to the MongoDB instance."""
        if self.client is None:
            try:
                # Set a connection timeout of 5 seconds to prevent stalling
                self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
                # Run ismaster command to verify connection is alive
                self.client.admin.command('ismaster')
                self.db = self.client[self.db_name]
                self.collection = self.db[self.collection_name]
                logger.info(f"Successfully connected to MongoDB database '{self.db_name}'")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB server at {self.uri}: {e}")
                self.client = None
                self.db = None
                self.collection = None
                raise e
            except Exception as e:
                logger.error(f"An unexpected database connection error occurred: {e}")
                self.client = None
                self.db = None
                self.collection = None
                raise e
        return self.collection

    def get_collection(self):
        """Returns the collection instance, establishing connection if necessary."""
        if self.collection is None:
            return self.connect()
        return self.collection

    def close(self):
        """Closes the MongoDB connection client."""
        if self.client:
            self.client.close()
            logger.info("MongoDB client connection closed.")
            self.client = None
            self.db = None
            self.collection = None

# Global DatabaseManager instance for imports
db_manager = DatabaseManager()
