import logging
import asyncio
from app.agents.prompts.news_prompt import NEWS_PROMPT

logger = logging.getLogger(__name__)

class NewsAgent:
    def __init__(self, llm, retriever_client):
        self.llm = llm
        self.retriever_client = retriever_client

    async def retrieve_context(self, query: str, k: int = 10, top_n: int = 5):
        try:
            docs = await self.retriever_client.retrieve_and_rerank(
                query=query,
                k=k,
                top_n=top_n
            )
            return docs
        except Exception as e:
            logger.error(f"NewsAgent retrieval error: {e}")
            return []

    def format_context_from_documents(self, documents: list) -> str:
        if not documents:
            return "No relevant off-field news found."

        text = ""
        for doc in documents:
            date = doc.get("date", "Unknown date")
            headline = doc.get("headline", "")
            content = doc.get("context_text", "")
            citation = doc.get("citation", "")

            text += f"[{date}] {headline}\n{content}\n"
            if citation:
                text += f"Source: {citation}\n"
            text += "\n"

        return text.strip()

    async def analyze_news_from_documents(self, query: str, documents: list):
        context_text = self.format_context_from_documents(documents)

        prompt_text = NEWS_PROMPT.format(
            query=query,
            context=context_text
        )

        result = await self.llm.generate_text(
            prompt=prompt_text,
            system_prompt=(
                "You are a professional NFL news analyst specializing in off-field matters. "
                "Respond cautiously, factually, and avoid speculation."
            ),
            temperature=0.2,
            max_tokens=512,
            stop_sequences=["\n\n\n"]
        )

        return result

    async def analyze_news(self, query: str, k: int = 10, top_n: int = 5):
        documents = await self.retrieve_context(query, k=k, top_n=top_n)

        if not documents:
            logger.warning(f"No off-field news documents found for query: {query}")
            return None

        return await self.analyze_news_from_documents(query, documents)

    async def summarize_to_one_sentence(self, subject: str, analysis_text: str):
        prompt = f"""
        Summarize the following off-field analysis for {subject} into one concise,
        factual sentence. Avoid speculation or legal conclusions.

        Analysis:
        {analysis_text}
        """

        result = await self.llm.generate_text(
            prompt=prompt,
            system_prompt="You are an NFL conduct and news analyst.",
            temperature=0.5,
            max_tokens=200
        )

        return f"{subject}: {result.content.strip()}"

    async def _analyze_single_subject(self, subject: str):
        query = f"{subject} off-field news and updates"

        try:
            analysis = await self.analyze_news(query)
            if not analysis:
                return f"{subject}: No recent off-field information available"

            summary = await self.summarize_to_one_sentence(subject, analysis.content)
            return summary

        except Exception as e:
            logger.error(f"Error analyzing off-field news for {subject}: {e}")
            return f"{subject}: Data unavailable ({str(e)})"

    async def generate_news_report(self, subjects: list[str]):
        logger.info(f"Starting parallel off-field news analysis for {len(subjects)} subjects")

        tasks = [self._analyze_single_subject(s) for s in subjects]
        results = await asyncio.gather(*tasks)

        logger.info("Completed off-field news analysis")
        return "\n".join(results)
