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
            cleaned.append((cleaned_sentence, citation_id))
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

        answer = result.content.strip().lower()

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

        for claim, citation_id in pairs:
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
