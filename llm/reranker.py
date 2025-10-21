import logging
from typing import List
from sentence_transformers.cross_encoder import CrossEncoder
from .schemas import Document  # Import the new schema

logger = logging.getLogger(__name__)

class ModelReranker:
    """
    A model-based reranker using a CrossEncoder.
    This is not LLM-based and runs locally on the server's CPU/GPU.
    We use 'cross-encoder/ms-marco-MiniLM-L6-v2' as a strong, fast default.
    """
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L6-v2'):
        """
        Initializes the CrossEncoder model.
        """
        try:
            self.model = CrossEncoder(model_name, max_length=512)
            logger.info(f"Successfully loaded reranker model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load reranker model {model_name}: {e}")
            raise
    
    def rerank_documents(self, query: str, documents: List[Document], top_n: int) -> List[Document]:
        """
        Reranks a list of documents based on relevance to the query.
        
        Args:
            query: The user's search query.
            documents: A list of Document objects.
            top_n: The number of documents to return.
            
        Returns:
            A reranked list of Document objects.
        """
        if not documents:
            return []
            
        # Create pairs of [query, document_content] for the model
        model_inputs = [[query, doc.content] for doc in documents]
        
        # Compute relevance scores
        logger.info(f"Scoring {len(model_inputs)} document pairs...")
        scores = self.model.predict(model_inputs, show_progress_bar=False)
        
        # Combine documents with their scores
        scored_documents = list(zip(scores, documents))
        
        # Sort documents by score in descending order (highest score is most relevant)
        scored_documents.sort(key=lambda x: x[0], reverse=True)
        
        # Extract the top N documents (or all if top_n > len(docs))
        final_top_n = min(top_n, len(scored_documents))
        reranked_docs = [doc for score, doc in scored_documents[:final_top_n]]
        
        return reranked_docs