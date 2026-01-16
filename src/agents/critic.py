# src/agents/critic.py
from src.agents.llm_manager import LLMManager
import json

class CriticAgent:
    def __init__(self):
        self.llm = LLMManager()

    def evaluate_extraction(self, transcript: str, extracted: list, gold_standard: list = None) -> dict:
        """
        Evaluates action item extraction quality.
        In practice, gold_standard comes from human review.
        """
        prompt = f"""
        Evaluate the quality of these extracted action items from a meeting.

        TRANSCRIPT EXCERPT:
        {transcript[:1000]}

        EXTRACTED ITEMS:
        {json.dumps(extracted, indent=2)}

        Rubric (1-5):
        1. Completeness: Are all real action items captured?
        2. Accuracy: Are owners and tasks correctly assigned?
        3. Clarity: Is the task description unambiguous?

        Return JSON: {{"completeness": 4, "accuracy": 5, "clarity": 3, "feedback": "..."}}
        """
        response = self.llm.generate(prompt, task_type="critique")
        return json.loads(response["response"])