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
        if not transcript or not isinstance(transcript, str):
            return []

        # Retrieve latest version of prompt
        prompt, meta = self.prompt_manager.get_latest_version("action_extraction")
        if not prompt:
            prompt = self.base_prompt
            self.prompt_manager.add_prompt(prompt, "action_extraction")

        final_prompt = prompt.format(transcript=transcript)
        response = self.llm.generate(final_prompt, task_type="action_extraction")
        raw_content = response.get("response", "[]")
        
        try:
            data = json.loads(raw_content)
            if isinstance(data, list):
                return self._validate_items(data)
            elif isinstance(data, dict):
                # Sometimes LLMs wrap the list in a dict
                for val in data.values():
                    if isinstance(val, list):
                        return self._validate_items(val)
                return [self._validate_dict_item(data)]
            else:
                return self._fallback_parse(raw_content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown blocks
            json_match = re.search(r'```json\n(.*?)\n```', raw_content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    if isinstance(data, list):
                        return self._validate_items(data)
                except json.JSONDecodeError:
                    pass
            return self._fallback_parse(raw_content)

    def _validate_items(self, items: list) -> list:
        validated = []
        for item in items:
            if isinstance(item, dict):
                validated.append(self._validate_dict_item(item))
            elif isinstance(item, str):
                validated.append({
                    "task": item,
                    "owner": "Unknown",
                    "due": None,
                    "priority": "medium"
                })
        return validated

    def _validate_dict_item(self, item: dict) -> dict:
        return {
            "task": str(item.get("task", "Unknown task")),
            "owner": str(item.get("owner", "Speaker 1")),
            "due": item.get("due"),
            "priority": str(item.get("priority", "medium"))
        }

    def _fallback_parse(self, text: str) -> list:
        # Simple heuristic parser
        items = []
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Look for lines that look like speaker actions
            speaker_match = re.search(r"(Speaker \d+).*(will|needs to|to) (.*)", line, re.IGNORECASE)
            if speaker_match:
                items.append({
                    "task": speaker_match.group(3).strip(),
                    "owner": speaker_match.group(1),
                    "due": None,
                    "priority": "medium"
                })
            elif line.startswith("-") or line.startswith("*"):
                # Bullet points
                items.append({
                    "task": line.lstrip("-* ").strip(),
                    "owner": "Speaker 1",
                    "due": None,
                    "priority": "medium"
                })
        return items