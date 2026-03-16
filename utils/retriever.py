import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class LegalKnowledgeRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = []
        self.index = None
        self.dimension = self.model.get_sentence_embedding_dimension()
        
    def load_knowledge_base(self, data_dir="data/knowledge_base"):
        if not os.path.exists(data_dir):
            return
        
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.knowledge_base.extend(data)
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

    def build_index(self):
        if not self.knowledge_base:
            return
            
        texts = [f"{item.get('topic', '')}: {item.get('content', '')}" for item in self.knowledge_base]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)

    def get_relevant_guidelines(self, clause_text: str, top_k: int = 3):
        pass

# Global instance
_retriever = None

def get_relevant_guidelines(clause_text: str, top_k: int = 3):
    global _retriever
    if _retriever is None:
        _retriever = LegalKnowledgeRetriever()
        _retriever.load_knowledge_base()
        _retriever.build_index()
    return _retriever.get_relevant_guidelines(clause_text, top_k)
