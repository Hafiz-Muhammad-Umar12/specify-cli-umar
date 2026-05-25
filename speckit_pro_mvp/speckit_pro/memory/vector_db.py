import os
import json
from typing import List, Dict, Any

class MemoryLayer:
    """
    Memory Layer using ChromaDB to store and retrieve past specifications.
    Allows for few-shot learning and architectural consistency.
    """
    def __init__(self, db_path: str = "./speckit_memory"):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name="past_specs",
                metadata={"description": "Storage for validated SpecKit Pro specifications"}
            )
            self.enabled = True
        except ImportError:
            print("[MEMORY] ChromaDB not installed. Memory layer disabled.")
            self.enabled = False

    def store_spec(self, spec: Dict[str, Any], success: bool = True):
        """Stores a validated spec in the vector database."""
        if not self.enabled: return
        
        spec_id = spec.get("title", "unknown").lower().replace(" ", "_")
        # Add timestamp to allow multiple versions/attempts
        import time
        spec_id = f"{spec_id}_{int(time.time())}"
        
        content = json.dumps(spec)
        
        self.collection.add(
            documents=[content],
            ids=[spec_id],
            metadatas=[{"title": spec.get("title", "unknown"), "success": success}]
        )

    def retrieve_similar(self, query: str, n_results: int = 1) -> str:
        """Retrieves similar past projects to use as context."""
        if not self.enabled: return ""

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents'] or not results['documents'][0]:
            return ""
            
        context = "\n--- SIMILAR PAST PROJECT CONTEXT ---\n"
        for doc in results['documents'][0]:
            context += doc + "\n"
        return context
