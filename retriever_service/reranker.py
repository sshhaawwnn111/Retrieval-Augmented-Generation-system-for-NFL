import logging
from typing import List
from sentence_transformers.cross_encoder import CrossEncoder
from schemas import Document
import torch

logger = logging.getLogger(__name__)


class ModelReranker:
    def __init__(self, model_name: str = 'zeroentropy/zerank-1-small'):
        try:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {device}")
            self.model = CrossEncoder(model_name, max_length=512, device=device, trust_remote_code=True)
            logger.info(f"Loaded reranker model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load reranker model {model_name}: {e}")
            raise

    def rerank_documents(self, query: str, documents: List[Document], top_n: int) -> List[Document]:
        if not documents:
            return []

        model_inputs = [[query, doc.content] for doc in documents]

        logger.info(f"Scoring {len(model_inputs)} document pairs...")
        scores = self.model.predict(model_inputs, show_progress_bar=False)

        scored_documents = list(zip(scores, documents))
        scored_documents.sort(key=lambda x: x[0], reverse=True)

        final_top_n = min(top_n, len(scored_documents))
        return [doc for score, doc in scored_documents[:final_top_n]]
