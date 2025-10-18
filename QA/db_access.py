import faiss
import numpy as np
import pickle

class VectorDB:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.dcts = []

    def add(self, vectors: np.ndarray, dct: dict[str, str]):
        """
        Добавляет вектор(ы) в индекс.
        
        Args:
            vectors: np.ndarray формы (n, dim) или (dim,) — для одного вектора
            texts: текст(ы), соответствующие векторам (опционально)
        """
        # Приводим к 2D
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)
        
        # Проверка размерности
        if vectors.shape[1] != self.dim:
            raise ValueError(f"Ожидалась размерность {self.dim}, получено {vectors.shape[1]}")

        self.dcts.append(dct)
        # Добавляем в индекс
        self.index.add(vectors)
        
        

    def search(self, query_vector: np.ndarray, k: int = 1):
        """
        Возвращает (оценки, индексы, [тексты]), если тексты сохранены.
        """
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        scores, indices = self.index.search(query_vector, k)
        indices = indices[0]  # убираем батч-размерность
        scores = scores[0]
        
        retrieved_texts = [self.dcts[i] for i in indices]
        return scores, indices, retrieved_texts

    def save(self, index_path: str, texts_path: str):
        """Сохраняет индекс и тексты."""
        faiss.write_index(self.index, index_path)
        with open(texts_path, 'wb') as f:
            pickle.dump(self.dcts, f)

    def load(self, index_path: str, texts_path: str):
        """Загружает индекс и тексты."""
        self.index = faiss.read_index(index_path)
        with open(texts_path, 'rb') as f:
            self.dcts = pickle.load(f)