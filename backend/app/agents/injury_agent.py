from app.agents.prompts.injury_prompt import INJURY_PROMPT
from app.agents.verifier_agent import CitationVerifierLLM
import asyncio
import logging
logger = logging.getLogger(__name__)

class InjuryAgent:
    def __init__(self, llm, retriever_client, verifier=None):
        self.llm = llm  # This is VLLMClient
        self.retriever_client = retriever_client  # This is RetrieverClient
        self.verifier = verifier or CitationVerifierLLM(llm)

    async def retrieve_context(self, query: str, k: int = 10, top_n: int = 5):
        """
        Centralized retrieval method used by all agents.
        Can be customized here if needed for specific use cases.
        """
        try:
            documents = await self.retriever_client.retrieve_and_rerank(
                query=query,
                k=k,
                top_n=top_n
            )
            return documents
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    def format_context_from_documents(self, documents: list) -> str:
        """
        Format retrieved documents into context string for LLM.
        Ensures citations are wrapped in brackets to match Verifier expectations.
        """
        if not documents:
            return "No recent news updates available."
        
        context_text = ""
        for doc in documents:
            date = doc.get('date', 'Unknown date')
            headline = doc.get('headline', 'No headline')
            context = doc.get('context_text', '')
            citation = doc.get('citation', '')
            
            context_text += f"[{date}] {headline}\n{context}\n"
            
            if citation:
                context_text += f"Source: {citation}\n"
                
            context_text += "\n"
        
        return context_text.strip()

    async def analyze_injury_from_documents(self, query: str, documents: list):
        """
        Analyze injury given pre-retrieved documents
        """
        # Format documents into context
        context_text = self.format_context_from_documents(documents)

        # Build prompt using the template
        prompt_text = INJURY_PROMPT.format(
            query=query,
            context=context_text
        )

        # Generate analysis with LLM
        result = await self.llm.generate_text(
            prompt=prompt_text,
            system_prompt="You are a professional NFL injury analyst. Provide concise analysis in 2-3 short paragraphs.",
            temperature=0.3,
            max_tokens=256,
            stop_sequences=[
                "\n\n\n",           # Stop at 3+ newlines
                "**Comparable Cases**",  # Stop before unnecessary sections
                "In conclusion",    # Stop before repetitive conclusions
            ]
        )
        
        return result

    async def analyze_injury(self, query: str, k: int = 10, top_n: int = 5):
        """
        Complete injury analysis workflow: retrieve + analyze
        """
        # 1. Retrieve Documents
        documents = await self.retrieve_context(query, k=k, top_n=top_n)
        
        if not documents:
            logger.warning(f"No documents found for query: {query}")
            return None
        
        # 2. Generate Analysis (now with citations)
        analysis_text = await self.analyze_injury_from_documents(query, documents)

        verification_results = []
        max_retries = 1  # Allow one correction pass
        
        # 3. Verification & Correction Loop
        for attempt in range(max_retries + 1):
            try:
                # Verify current text
                verification_results = await self.verifier.verify(
                    documents_json={"documents": documents},
                    generated_text=analysis_text
                )
                
                # Check for unsupported claims
                failed_checks = [v for v in verification_results if v['classification'] != 'supported']
                
                # If perfect or we are out of retries, stop
                if not failed_checks:
                    if attempt > 0:
                        logger.info(f"Correction successful on attempt {attempt}")
                    break
                
                if attempt < max_retries:
                    logger.warning(f"Verification found {len(failed_checks)} issues. Running auto-correction (Attempt {attempt+1}/{max_retries})...")
                    
                    # 4. Auto-Correct using Verifier's edit_report
                    # edit_report returns the text string directly
                    analysis_text = await self.verifier.edit_report(
                        generated_text=analysis_text,
                        verification_results=verification_results,
                        documents_json={"documents": documents}
                    )
            
            except Exception as e:
                logger.error(f"Verification/Correction cycle failed: {e}")
                # If correction fails, we break and return what we have
                break

        return {
            "content": analysis_text,
            "verification": verification_results,
            "retrieved_documents": documents
        }

    async def summarize_to_one_sentence(self, player_name: str, analysis_text: str) -> str:
        """
        Summarize the injury analysis into one concise sentence per player.
        Uses the LLM to condense the analysis into a concise statement.
        """
        summarization_prompt = f"""
### INSTRUCTIONS ###
Summarize the injury analysis below for {player_name} into EXACTLY ONE concise sentence.

### REQUIREMENTS ###
1. **Content**: Clearly state current injury status, recovery outlook, and play availability.
2. **Citations**: You MUST preserve the citation tags (e.g. \cite{{[doc_id]}}) found in the source text. Place them immediately after the claims they support.
3. **Format**: 
   - Start directly with the summary. 
   - Do NOT repeat the prompt.
   - Do NOT generate a bibliography or reference list.

### SOURCE ANALYSIS ###
{analysis_text}

### ONE SENTENCE SUMMARY ###
"""

        result_text = await self.llm.generate_text(
            prompt=summarization_prompt,
            system_prompt="You are a strict editor. Summarize text concisely without adding external references.",
            temperature=0.1,
            max_tokens=150
        )
        return f"{player_name}: {result_text.strip()}"
    
    async def _analyze_single_player(self, player: str, week_number: int) -> str:
        """
        Analyze injury status for a single player.
        Extracted for parallel processing.
        """
        query = f"{player} injury status week {week_number}"
        try:
            # Retrieve and analyze
            analysis = await self.analyze_injury(query)

            if not analysis:
                logger.warning(f"No analysis generated for {player}")
                return f"{player}: No recent injury data available"

            analysis_text = analysis["content"]
            # Summarize to one sentence
            summary = await self.summarize_to_one_sentence(player, analysis_text)
            return summary
            
        except Exception as e:
            logger.error(f"Error analyzing {player}: {e}")
            return f"{player}: Data unavailable ({str(e)})"
        
    async def generate_team_injury_report(self, players: list[str], week_number: int) -> str:
        """
        Generate injury report for a list of players.
        PROCESSES ALL PLAYERS IN PARALLEL for maximum throughput.
        
        Args:
            players: List of player names to analyze
            week_number: Week number for the analysis
            
        Returns:
            Multi-line string with one sentence per player
        """
        logger.info(f"Starting parallel injury analysis for {len(players)} players")
        
        # Create tasks for all players - they run concurrently
        tasks = [
            self._analyze_single_player(player, week_number)
            for player in players
        ]
        
        # Wait for all analyses to complete
        player_summaries = await asyncio.gather(*tasks)
        
        # Combine into one report
        report_text = "\n".join(player_summaries)
        logger.info(f"Completed parallel injury analysis for week {week_number}")
        
        return report_text
