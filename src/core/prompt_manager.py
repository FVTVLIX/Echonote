# src/core/prompt_manager.py
import json
import os

class PromptManager:
    def __init__(self, storage_path: str = "prompts.json"):
        self.storage_path = storage_path
        self.prompts = self._load_prompts()

    def _load_prompts(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {}

    def _save_prompts(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.prompts, f, indent=2)

    def get_latest_version(self, task_name: str) -> tuple:
        """
        Returns (prompt_text, metadata)
        """
        if task_name in self.prompts:
            latest = self.prompts[task_name][-1]
            return latest["prompt"], latest["meta"]
        return None, None

    def add_prompt(self, prompt_text: str, task_name: str, meta: dict = None):
        if task_name not in self.prompts:
            self.prompts[task_name] = []
        
        version_entry = {
            "version": len(self.prompts[task_name]) + 1,
            "prompt": prompt_text,
            "meta": meta or {"author": "system", "description": "Initial version"}
        }
        self.prompts[task_name].append(version_entry)
        self._save_prompts()
