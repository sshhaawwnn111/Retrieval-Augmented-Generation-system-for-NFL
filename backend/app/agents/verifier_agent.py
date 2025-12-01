import re
import json
from typing import List, Dict, Tuple, Any

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

    def build_lookup(self, documents: List[Dict[str, Any]]) -> Dict[str, str]:
        table = {}
        for d in documents:
            cid = self.normalize(d["citation"])
            table[cid] = (
                f"{d['player_name']}: {d['headline']} on {d['date']} "
                f"(Status: {d['injury_status']}, Detail: {d['injury_detail']})"
            )
        return table

    def extract_claims(self, text: str) -> List[Tuple[str, str]]:
        pattern = r"(.*?)(?:\\cite\{(\[.*?])\})"
        matches = re.findall(pattern, text)

        cleaned = []
        for sentence, raw_citation in matches:
            cleaned_sentence = sentence.strip(" -\n")
            citation_id = self.normalize(raw_citation)
            cleaned.append((citation_id, cleaned_sentence))
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

        if answer == "supported":
            return "supported"
        if "not" in answer:
            return "not supported"
        if "neutral" in answer:
            return "neutral"

        return "neutral"

    async def verify(self, documents_json: dict, generated_text: str):
        documents = documents_json["documents"]
        lookup = self.build_lookup(documents)
        pairs = self.extract_claims(generated_text)

        results = []

        for citation_id, claim in pairs:
            evidence = lookup.get(citation_id)

            if evidence is None:
                results.append({
                    "claim": claim,
                    "citation_id": citation_id,
                    "evidence": None,
                    "classification": "not supported (missing evidence)"
                })
                continue

            classification = await self.judge_with_llm(claim, evidence)

            results.append({
                "claim": claim,
                "citation_id": citation_id,
                "evidence": evidence,
                "classification": classification
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

            5. Final output must be a polished, flowing narrative report, not bullet points, not JSON.

            6. Every factual statement must cite an evidence key using the exact format: \cite{{[ref_x doc_y row_z]}}

            Return the corrected report text.
        """

        result = await self.llm.generate_text(
            prompt=prompt,
            system_prompt="You are an expert NFL medical + data report editor.",
            temperature=0.2,
            max_tokens=2000,
        )

        return result