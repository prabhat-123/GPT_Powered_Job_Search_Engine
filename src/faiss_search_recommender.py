import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class SearchRecommender:
    def __init__(self, model_name, faiss_index_path):
        self.model_name = model_name
        self.faiss_index_path = faiss_index_path
        self.model = SentenceTransformer(self.model_name)
        self.fais_index = faiss.read_index(self.faiss_index_path)

    def recommend_faiss_index(self, query):
        query_vector = self.model.encode(query)
        query_vector = np.array(query_vector).reshape(1, -1).astype('float32')
        k = 100 
        distances, indices = self.fais_index.search(query_vector, k)
        neighbor_ids = indices[0]
        return neighbor_ids.tolist()
    



