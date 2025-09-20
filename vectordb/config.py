import os
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

class VectorDBConfig:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-3-small"
        )
        
        self.collection = self.client.get_or_create_collection(
            name="products",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
    
    def reset_collection(self):
        """Reset the collection if needed"""
        try:
            self.client.delete_collection("products")
            self.collection = self.client.create_collection(
                name="products",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Error resetting collection: {e}")
    
    def get_collection(self):
        return self.collection
    
    def get_client(self):
        return self.client

vector_db = VectorDBConfig()
