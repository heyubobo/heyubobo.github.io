import faiss
import numpy as np

class VectorMemory:
    def __init__(self, dim=1536):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, vector, text):
        vector = np.array([vector], dtype=np.float32)
        self.index.add(vector)
        self.texts.append(text)

    def search(self, vector, k=5):
        if len(self.texts) == 0:
            return []

        vector = np.array([vector], dtype=np.float32)
        D, I = self.index.search(vector, k)

        results = []
        for i in I[0]:
            if 0 <= i < len(self.texts):
                results.append(self.texts[i])

        return results