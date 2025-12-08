import re
import json
from typing import List, Dict, Tuple, Any
import asyncio

class CitationVerifierLLM:
    """
    Verify claims using the SAME LLM interface as InjuryAgent (VLLMClient).
    """
    def __init__(self, llm):
        self.llm = llm    

    def normalize(self, raw: str) -> str:
        return (
            raw.replace("[", "")
               .replace("]", "")
               .replace(" ", "_")
        )

    def parse_citations(self, raw: str) -> List[str]:
        """
        Parse '[doc_1, doc_2]' into ['doc_1', 'doc_2']
        """
        s = raw.replace("[", "").replace("]", "")
        # Split by comma or space, filter empty
        return [p.strip() for p in re.split(r'[,\s]+', s) if p.strip()]

    def _clean_claim_text(self, text: str) -> str:
        """
        Remove conversational filler and prefixes to normalize claims for deduplication.
        """
        # Remove Markdown bolding
        text = text.replace("**", "")
        # Remove prefixes like "Output Report:", "Final Report:"
        text = re.sub(r"^(Output|Final|Corrected|Input)\s*Report:?", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^(Here is|This is) the .*?:", "", text, flags=re.IGNORECASE)
        # Remove numbering
        text = re.sub(r"^\d+\.\s*", "", text)
        return text.strip(" -:,\n")

    def build_lookup(self, documents: List[Dict[str, Any]]) -> Dict[str, str]:
        table = {}
        for d in documents:
            # Ensure we match the ID format used in parse_citations
            cid = d["citation"].replace("[", "").replace("]", "").strip()
            
            table[cid] = d["context_text"]
        return table

    def extract_claims(self, text: str) -> List[Tuple[List[str], str]]:
        pattern = r"(.*?)(?:\\cite\{(\[.*?])\})"
        matches = re.findall(pattern, text)

        cleaned = []
        seen = set()

        for sentence, raw_citation in matches:
            # Parse citations list
            citation_ids = self.parse_citations(raw_citation)
            if not citation_ids:
                continue

            # Clean claim text for deduplication
            core_text = self._clean_claim_text(sentence)
            
            if len(core_text) < 5:
                continue

            # Deduplicate based on core text
            if core_text not in seen:
                seen.add(core_text)
                cleaned.append((citation_ids, core_text))
                
        return cleaned

    async def judge_with_llm(self, claim: str, evidence: str) -> str:
        verification_prompt = f"""
            You are an evidence verification model.

            Task: Determine whether the CLAIM is supported by the EVIDENCE.

            Return only: supported, neutral, not supported.

            CLAIM:
            {claim}

            EVIDENCE:
            {evidence}
            """

        result = await self.llm.generate_text(
            prompt=verification_prompt,
            system_prompt="You are a strict citation verification model.",
            temperature=0.0,
            max_tokens=64,
            stop_sequences=[]
        )

        answer = result.strip().lower()

        # FIX: More robust parsing logic
        # Check "not supported" first because it contains the word "supported"
        if "not supported" in answer:
            return "not supported"
        if "supported" in answer:
            return "supported"
        if "neutral" in answer:
            return "neutral"

        # Fallback
        return "neutral"

    async def verify(self, documents_json: dict, generated_text: str):
        documents = documents_json["documents"]
        lookup = self.build_lookup(documents)
        pairs = self.extract_claims(generated_text)

        # Prepare tasks for parallel execution
        tasks = []
        task_metadata = []

        for citation_ids, claim in pairs:
            # Gather evidence from ALL citations
            evidence_parts = []
            
            for cid in citation_ids:
                if cid in lookup:
                    evidence_parts.append(lookup[cid])
            
            combined_evidence = "\n".join(evidence_parts)
            
            if not combined_evidence:
                # Handle missing evidence immediately without LLM
                task_metadata.append({
                    "claim": claim,
                    "citation_id": ",".join(citation_ids),
                    "evidence": None,
                    "classification": "not supported (missing evidence)",
                    "is_task": False
                })
            else:
                # Schedule LLM check
                tasks.append(self.judge_with_llm(claim, combined_evidence))
                task_metadata.append({
                    "claim": claim,
                    "citation_id": ",".join(citation_ids),
                    "evidence": combined_evidence,
                    "is_task": True
                })

        # Run all LLM checks in parallel
        llm_results = await asyncio.gather(*tasks)
        
        # Reassemble results in order
        results = []
        llm_result_idx = 0
        
        for meta in task_metadata:
            if meta["is_task"]:
                classification = llm_results[llm_result_idx]
                llm_result_idx += 1
                results.append({
                    "claim": meta["claim"],
                    "citation_id": meta["citation_id"],
                    "evidence": meta["evidence"],
                    "classification": classification
                })
            else:
                results.append({
                    "claim": meta["claim"],
                    "citation_id": meta["citation_id"],
                    "evidence": meta["evidence"],
                    "classification": meta["classification"]
                })

        return results

    async def edit_report(
        self,
        generated_text: str,
        verification_results: List[Dict[str, Any]],
        documents_json: Dict[str, Any],
    ) -> str:
        """
        Args:
            generated_text: original report
            verification_results: output of CitationVerifierLLM.verify()
            documents_json: retrieved evidence set

        Returns:
            Cleaned, corrected report generated in ONE LLM call.
        """

        prompt = f"""
            You are a professional NFL injury report editor.

            Your task: rewrite the entire report so that every sentence is
            fully supported by evidence from the retrieved documents.

            Input Report: {generated_text}

            Verification Results: {json.dumps(verification_results, indent=2)}

            Retrieved Documents: {json.dumps(documents_json['documents'], indent=2)}

            RULES FOR REWRITING THE REPORT:

            1. Supported claims  
            - Keep the sentence mostly unchanged.  
            - Keep citations intact.

            2. Neutral claims  
            - Rewrite to reflect uncertainty (e.g., "unclear", "not fully specified").  
            - Stay strictly within evidence.

            3. Not supported claims  
            - Remove the sentence entirely.

            4. Missing evidence 
            - Remove the claim or rewrite using only available data.

            5. Final output must be a polished, flowing narrative report.
            - DO NOT include headers like "Output Report", "Final Report", or "Corrected Report".
            - DO NOT include conversational filler like "Here is the report".
            - Return ONLY the report body.

            6. Every factual statement must cite an evidence key using the exact format: \cite{{[doc_id]}}

            Return the corrected report text.
        """

        result = await self.llm.generate_text(
            prompt=prompt,
            system_prompt="You are an expert NFL medical + data report editor.",
            temperature=0.2,
            max_tokens=2000,
        )

        return result