import os
import chromadb
from chromadb.config import Settings
import config
from logger import logger

class FaceDatabase:
    def __init__(self):
        """
        Initializes the ChromaDB client and gets/creates the face collection.
        Uses local persistent storage as defined in config.
        """
        db_path = config.CHROMA_DB_DIR
        if not os.path.exists(db_path):
            os.makedirs(db_path)
            
        logger.info(f"Initializing Vector Database at {db_path}...")
        
        self.client = chromadb.PersistentClient(path=db_path)
        
        # We use Cosine distance because we are storing embeddings from Facenet512
        # which performs best with cosine similarity.
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"Connected to collection: {config.COLLECTION_NAME}. Total faces stored: {self.collection.count()}")

    def add_face(self, user_id: str, embedding: list[float], metadata: dict = None):
        """
        Adds a single face embedding to the vector database.
        
        Args:
            user_id: Unique identifier for the person (e.g., employee ID)
            embedding: The 512-dimensional vector from Facenet512
            metadata: Optional dictionary with extra data (e.g., name, joined_date)
        """
        try:
            if metadata is None:
                metadata = {}
                
            self.collection.upsert(
                documents=["face_embedding"], # Chroma requires a document string, we just use a placeholder
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[user_id]
            )
            logger.info(f"Successfully added/updated face for user: {user_id}")
            return True, f"User {user_id} registered successfully."
        except Exception as e:
            logger.error(f"Failed to add face for {user_id}: {str(e)}")
            return False, f"Database error: {str(e)}"

    def search_face(self, embedding: list[float], threshold: float = None):
        """
        Searches the database for the closest matching face embedding.
        
        Args:
            embedding: The target face embedding to search for
            threshold: Maximum allowed distance (defaults to config.MATCH_THRESHOLD)
            
        Returns:
            Dictionary with match status, user_id, and distance
        """
        if threshold is None:
            threshold = config.MATCH_THRESHOLD
            
        # If DB is empty, return no match immediately
        if self.collection.count() == 0:
            return {"verified": False, "match": None, "distance": "N/A", "error": "Database is empty"}

        try:
            # Query the closest 1 match
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=1
            )
            
            # Extract results safely
            if not results['ids'] or not results['ids'][0]:
                return {"verified": False, "match": None, "distance": "N/A", "error": "No matches found"}
                
            best_match_id = results['ids'][0][0]
            best_distance = results['distances'][0][0]
            metadata = results['metadatas'][0][0] if results['metadatas'] and results['metadatas'][0] else {}
            
            # Check if it meets the strictly required threshold
            if best_distance <= threshold:
                logger.info(f"Match found! User: {best_match_id}, Distance: {best_distance:.4f}")
                return {
                    "verified": True, 
                    "match": best_match_id, 
                    "distance": float(best_distance),
                    "metadata": metadata
                }
            else:
                logger.info(f"No match. Closest was {best_match_id} but distance {best_distance:.4f} > {threshold}")
                return {
                    "verified": False, 
                    "match": None, 
                    "distance": float(best_distance),
                    "closest_id": best_match_id, # Helpful for debugging
                    "error": "Face does not match any registered user"
                }
                
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {"verified": False, "match": None, "distance": "Error", "error": str(e)}

# Singleton instance instance to be used across the app
db = FaceDatabase()
