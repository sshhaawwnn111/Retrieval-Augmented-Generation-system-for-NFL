import logging
import asyncio
from app.agents.prompts.waiver_prompt import WAIVER_PROMPT
from app.agents.verifier_agent import CitationVerifierLLM

logger = logging.getLogger(__name__)

class WaiverAgent:
    def __init__(self, llm, retriever_client, verifier=None):
        self.llm = llm
        self.retriever_client = retriever_client
        self.verifier = verifier or CitationVerifierLLM(llm)

    async def retrieve_context(self, query: str, k: int = 10, top_n: int = 5):
        try:
            docs = await self.retriever_client.retrieve_and_rerank(
                query=query,
                k=k,
                top_n=top_n
            )
            return docs
        except Exception as e:
            logger.error(f"WaiverAgent retrieval error: {e}")
            return []

    def format_context_from_documents(self, documents: list) -> str:
        if not documents:
            return "No recent waiver or contract news available."

        text = ""
        for doc in documents:
            date = doc.get("date", "Unknown date")
            headline = doc.get("headline", "No headline")
            context = doc.get("context_text", "")
            citation = doc.get("citation", "")

            text += f"[{date}] {headline}\n{context}\n"
            if citation:
                text += f"Source: {citation}\n"
            text += "\n"

        return text.strip()

    async def analyze_waiver_from_documents(self, query: str, documents: list):
        context_text = self.format_context_from_documents(documents)

        prompt_text = WAIVER_PROMPT.format(
            query=query,
            context=context_text
        )

        result = await self.llm.generate_text(
            prompt=prompt_text,
            system_prompt=(
                "You are an expert NFL roster and contract analyst. "
                "Provide a clear, structured waiver and contract evaluation."
            ),
            temperature=0.3,
            max_tokens=512,
            stop_sequences=["\n\n\n", "In conclusion"]
        )

        return result

    async def analyze_waiver(self, query: str, k: int = 10, top_n: int = 5):
        documents = await self.retrieve_context(query, k=k, top_n=top_n)

        if not documents:
            logger.warning(f"No waiver documents found for query: {query}")
            return None

        analysis_text = await self.analyze_waiver_from_documents(query, documents)

        verification_results = []
        max_retries = 1

        for attempt in range(max_retries + 1):
            try:
                verification_results = await self.verifier.verify(
                    documents_json={"documents": documents},
                    generated_text=analysis_text
                )

                if not verification_results:
                    logger.info("No citation found.")
                    break

                failed_checks = [v for v in verification_results if v['classification'] != 'supported']

                if not failed_checks:
                    logger.info(f"Correction successful on attempt {attempt+1}/{max_retries}")
                    break

                if attempt < max_retries:
                    logger.warning(f"Verification found {len(failed_checks)} issues. Running auto-correction (Attempt {attempt+1}/{max_retries})...")
                    analysis_text = await self.verifier.edit_report(
                        generated_text=analysis_text,
                        verification_results=verification_results,
                        documents_json={"documents": documents}
                    )

            except Exception as e:
                logger.error(f"Verification/Correction cycle failed: {e}")
                break

        return {
            "content": analysis_text,
            "verification": verification_results,
            "retrieved_documents": documents
        }

    async def summarize_to_one_sentence(self, subject: str, analysis_text: str):
        prompt = f"""
        Summarize the following waiver analysis for {subject} into one concise sentence.
        
        Analysis:
        {analysis_text}
        """

        result = await self.llm.generate_text(
            prompt=prompt,
            system_prompt="You are an expert NFL contract and roster analyst.",
            temperature=0.7,
            max_tokens=200
        )

        return f"{subject}: {result.content.strip()}"

    async def _analyze_single_subject(self, subject: str):
        query = f"{subject} waiver status and contract situation"

        try:
            analysis = await self.analyze_waiver(query)
            if not analysis:
                return f"{subject}: No recent waiver information available"

            summary = await self.summarize_to_one_sentence(subject, analysis.content)
            return summary

        except Exception as e:
            logger.error(f"Error analyzing waiver for {subject}: {e}")
            return f"{subject}: Data unavailable ({str(e)})"

    async def generate_waiver_report(self, subjects: list[str]):
        logger.info(f"Starting parallel waiver analysis for {len(subjects)} subjects")

        tasks = [self._analyze_single_subject(s) for s in subjects]
        results = await asyncio.gather(*tasks)

        logger.info("Completed waiver analysis")
        return "\n".join(results)
