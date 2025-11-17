from app.agents.prompts.injury_prompt import INJURY_PROMPT
from schemas import Document

class InjuryAgent:
    def __init__(self, llm, db, retriever, reranker):
        self.llm = llm            # VLLMClient
        self.db = db              # DatabaseConnection (optional)
        self.retriever = retriever  # PGVectorRetriever
        self.reranker = reranker    # ModelReranker

    async def analyze_injury(self, query: str):
        """
        Full pipeline:
        1. Retriever embeds + fetches candidates
        2. Reranker scores them
        3. LLM analyzes using top context
        """

        # Step 1 — Retrieve semantic candidates from Postgres
        raw_docs = self.retriever.search(query, k=10)

        # Convert raw docs to Document objects expected by reranker
        docs = []
        for d in raw_docs:
            docs.append(
                Document(
                    id=str(d["doc_id"]),
                    content=d["context_text"]
                )
            )

        # Step 2 — Rerank to get best 5
        top_docs = self.reranker.rerank_documents(query, docs, top_n=5)

        # Build the final context
        if not top_docs:
            context_text = "No relevant injury news available."
        else:
            context_text = "\n".join([doc.content for doc in top_docs])

        # Step 3 — Build final prompt
        prompt_text = INJURY_PROMPT.format(
            query=query,
            context=context_text
        )

        # Step 4 — LLM analysis
        result = await self.llm.generate_text(
            prompt=prompt_text,
            system_prompt="You are a professional NFL injury analyst.",
            temperature=0.3,
            max_tokens=512
        )

        return result.content.strip()
