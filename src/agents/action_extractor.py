# src/agents/action_extractor.py
from src.agents.llm_manager import LLMManager
from src.core.prompt_manager import PromptManager
import json, re

class ActionExtractor:
    def __init__(self):
        self.llm = LLMManager()
        self.prompt_manager = PromptManager()
        self.base_prompt = """
        Extract all action items from the meeting transcript.
        An action item has: task, owner (speaker ID), due date (if mentioned), priority.
        
        Transcript:
        {transcript}
        
        Return JSON list: [{{"task": "...", "owner": "Speaker 1", "due": "YYYY-MM-DD", "priority": "high/medium/low"}}]
        If no due date, leave as null.
        """

    def extract(self, transcript: str) -> list:
        # Retrieve latest version of prompt
        prompt, meta = self.prompt_manager.get_latest_version("action_extraction")
        if not prompt:
            prompt = self.base_prompt
            self.prompt_manager.add_prompt(prompt, "action_extraction")

        final_prompt = prompt.format(transcript=transcript)
        response = self.llm.generate(final_prompt, task_type="action_extraction")
        
        try:
            return json.loads(response["response"])
        except:
            # Fallback: parse with regex
            return self._fallback_parse(response["response"])

    def _fallback_parse(self, text: str) -> list:
        # Simple heuristic parser
        items = []
        lines = text.split('\n')
        for line in lines:
            if "Speaker" in line and ("will" in line or "task" in line):
                items.append({
                    "task": line.strip(),
                    "owner": re.search(r"Speaker \d+", line).group(),
                    "due": None,
                    "priority": "medium"
                })
        return items