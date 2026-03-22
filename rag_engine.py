import os
import numpy as np
from sentence_transformers import SentenceTransformer
from functools import lru_cache


model = SentenceTransformer('all-MiniLM-L6-v2')

class RAGEngine:
    def __init__(self, docs_path="docs/"):
        self.documents = []
        self.embeddings = []
        self._load_docs(docs_path)

    def _load_docs(self, path):
        """Loads and embeds all .md files from the docs folder."""
        if not os.path.exists(path):
            os.makedirs(path)
            return

        for file in os.listdir(path):
            if file.endswith(".md"):
                with open(os.path.join(path, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 10]
                    for chunk in chunks:
                        self.documents.append({"text": chunk, "source": file})
        
        if self.documents:
            texts = [doc["text"] for doc in self.documents]
            self.embeddings = model.encode(texts, convert_to_tensor=False)

    @lru_cache(maxsize=128)
    def _get_cached_embedding(self, query):
        """Caches the vector calculation for repeated user queries."""
        return model.encode([query])

    def retrieve(self, query, k=2):
        """Finds the most relevant snippets from local docs."""
        if not self.documents:
            return []
            
        query_vec = self._get_cached_embedding(query)
        similarities = np.dot(self.embeddings, query_vec.T).flatten()
        top_indices = np.argsort(similarities)[-k:][::-1]
        return [self.documents[i] for i in top_indices]