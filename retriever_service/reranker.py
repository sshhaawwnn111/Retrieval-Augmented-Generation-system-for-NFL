import logging
from typing import List
from sentence_transformers.cross_encoder import CrossEncoder
from schemas import Document
<<<<<<< HEAD
=======
import torch
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86

logger = logging.getLogger(__name__)


class ModelReranker:
<<<<<<< HEAD
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L6-v2'):
        try:
            self.model = CrossEncoder(model_name, max_length=512)
=======
    def __init__(self, model_name: str = 'zeroentropy/zerank-1-small'):
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            dtype = torch.float16 if device == 'cuda' else torch.float32
            logger.info(f"Using device: {device}, dtype: {dtype}")
            self.model = CrossEncoder(
                model_name,
                max_length=512,
                device=device,
                trust_remote_code=True,
                # UPDATE: Add low_cpu_mem_usage=False to fix meta tensor error
                model_kwargs={
                    "dtype": dtype,
                    "low_cpu_mem_usage": False
                }
            )
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86
            logger.info(f"Loaded reranker model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load reranker model {model_name}: {e}")
            raise

    def rerank_documents(self, query: str, documents: List[Document], top_n: int) -> List[Document]:
        if not documents:
            return []

        model_inputs = [[query, doc.content] for doc in documents]

        logger.info(f"Scoring {len(model_inputs)} document pairs...")
<<<<<<< HEAD
        scores = self.model.predict(model_inputs, show_progress_bar=False)
=======
        with torch.inference_mode():
            scores = self.model.predict(
                model_inputs, 
                batch_size=4, 
                show_progress_bar=False
            )
>>>>>>> b14e10054d8bd29630a2781e550f4bef0d841c86

        scored_documents = list(zip(scores, documents))
        scored_documents.sort(key=lambda x: x[0], reverse=True)

        final_top_n = min(top_n, len(scored_documents))
        return [doc for score, doc in scored_documents[:final_top_n]]
