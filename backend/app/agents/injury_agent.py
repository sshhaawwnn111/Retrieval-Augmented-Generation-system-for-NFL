from app.agents.prompts.injury_prompt import INJURY_PROMPT
import asyncio
import logging
logger = logging.getLogger(__name__)

class InjuryAgent:
    def __init__(self, llm, retriever_client):
        self.llm = llm  # This is VLLMClient
        self.retriever_client = retriever_client  # This is RetrieverClient

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
        Format retrieved documents into context string for LLM
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
        documents = await self.retrieve_context(query, k=k, top_n=top_n)
        
        if not documents:
            logger.warning(f"No documents found for query: {query}")
            return None
        
        return await self.analyze_injury_from_documents(query, documents)

    async def summarize_to_one_sentence(self, player_name: str, analysis_text: str) -> str:
        """
        Summarize the injury analysis into one concise sentence per player.
        Uses the LLM to condense the analysis into a concise statement.
        """
        summarization_prompt = f"""
        Summarize the following injury analysis for {player_name} into one concise sentence.
        The summary should clearly state their current injury status, recovery outlook,
        and whether they are expected to play in the given week.

        Injury Analysis:
        {analysis_text}
        """

        result = await self.llm.generate_text(
            prompt=summarization_prompt,
            system_prompt="You are a professional NFL injury analyst.",
            temperature=0.3,
            max_tokens=512
        )
        return f"{player_name}: {result.content.strip()}"
    
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
            
            # Summarize to one sentence
            summary = await self.summarize_to_one_sentence(player, analysis.content)
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
