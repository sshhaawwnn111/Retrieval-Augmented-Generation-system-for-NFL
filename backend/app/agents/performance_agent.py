import logging
import asyncio
from app.agents.prompts.performance_prompt import PERFORMANCE_PROMPT

logger = logging.getLogger(__name__)


class PerformanceAgent:
    """
    PerformanceAgent mirrors the structure of InjuryAgent exactly.
    It retrieves context via RetrieverClient, formats it, builds an
    LLM prompt using PERFORMANCE_PROMPT, and generates analysis.
    """

    def __init__(self, llm, retriever_client):
        self.llm = llm               # VLLMClient
        self.retriever_client = retriever_client   # RetrieverClient

    async def retrieve_context(self, query: str, k: int = 10, top_n: int = 5):
        """
        Centralized retrieval identical to InjuryAgent.
        Retrieves + reranks documents using RetrieverClient.
        """
        try:
            docs = await self.retriever_client.retrieve_and_rerank(
                query=query,
                k=k,
                top_n=top_n
            )
            return docs
        except Exception as e:
            logger.error(f"PerformanceAgent retrieval error: {e}")
            return []

    def format_context_from_documents(self, documents: list) -> str:
        """
        Mirrors InjuryAgent: turn retrieved docs into a readable context block.
        """
        if not documents:
            return "No recent team or player performance data available."

        context_text = ""
        for doc in documents:
            date = doc.get("date", "Unknown date")
            headline = doc.get("headline", "No headline")
            context = doc.get("context_text", "")
            citation = doc.get("citation", "")

            context_text += f"[{date}] {headline}\n{context}\n"
            if citation:
                context_text += f"Source: {citation}\n"
            context_text += "\n"

        return context_text.strip()

    async def analyze_performance_from_documents(self, query: str, documents: list):
        """
        Same pattern as analyze_injury_from_documents().
        Formats docs, builds prompt, feeds to LLM.
        """
        context_text = self.format_context_from_documents(documents)

        prompt_text = PERFORMANCE_PROMPT.format(
            query=query,
            context=context_text
        )

        result = await self.llm.generate_text(
            prompt=prompt_text,
            system_prompt=(
                "You are a professional NFL performance analyst. "
                "Provide a clear, structured analysis of team and player performance."
            ),
            temperature=0.3,
            max_tokens=512,
            stop_sequences=[
                "\n\n\n",
                "In conclusion"
            ]
        )

        return result

    async def analyze_performance(self, query: str, k: int = 10, top_n: int = 5):
        """
        Full workflow: retrieve → analyze, identical to InjuryAgent.
        """
        documents = await self.retrieve_context(query, k=k, top_n=top_n)

        if not documents:
            logger.warning(f"No performance documents found for query: {query}")
            return None

        return await self.analyze_performance_from_documents(query, documents)

    async def summarize_to_one_sentence(self, subject: str, analysis_text: str) -> str:
        """
        Optional summarizer: same structure as the injury summarizer.
        Produces a one-sentence summary per team or player.
        """
        summarization_prompt = f"""
        Summarize the following performance analysis for {subject} into one clear sentence.
        Capture overall effectiveness, standout metrics, and key takeaways.

        Performance Analysis:
        {analysis_text}
        """

        result = await self.llm.generate_text(
            prompt=summarization_prompt,
            system_prompt="You are a professional NFL performance analyst.",
            temperature=0.7,
            max_tokens=256
        )

        return f"{subject}: {result.content.strip()}"

    async def _analyze_single_subject(self, subject: str, week_number: int):
        """
        Parallel-safe single-subject (player or team unit) performance evaluation.
        Mirrors _analyze_single_player() structure exactly.
        """
        query = f"{subject} performance week {week_number}"

        try:
            analysis = await self.analyze_performance(query)

            if not analysis:
                return f"{subject}: No recent performance data available"

            summary = await self.summarize_to_one_sentence(subject, analysis.content)
            return summary

        except Exception as e:
            logger.error(f"Error analyzing performance for {subject}: {e}")
            return f"{subject}: Data unavailable ({str(e)})"

    async def generate_performance_report(self, subjects: list[str], week_number: int) -> str:
        """
        Parallel multi-entity performance reporting.
        Mirrors generate_player_report().
        """
        logger.info(f"Starting parallel performance analysis for {len(subjects)} subjects")

        tasks = [
            self._analyze_single_subject(subj, week_number)
            for subj in subjects
        ]

        results = await asyncio.gather(*tasks)

        report = "\n".join(results)

        logger.info(f"Completed performance analysis for week {week_number}")

        return report
