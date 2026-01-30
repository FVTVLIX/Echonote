# src/agents/summarizer.py
from src.agents.llm_manager import LLMManager
import json

class SummarizerAgent:
    def __init__(self):
        self.llm = LLMManager()

    def summarize_transcript(self, transcript: dict) -> dict:
        """
        transcript: AssemblyAI response with utterances and speaker labels
        """
        if not isinstance(transcript, dict) or 'utterances' not in transcript:
            return self._get_fallback_summary("Invalid transcript data provided.")

        utterances = transcript.get('utterances', [])
        if not utterances:
             return self._get_fallback_summary("No speech detected in the audio file.")

        text_with_speakers = "\n".join([
            f"Speaker {u.get('speaker', 'Unknown')}: {u.get('text', '')}" for u in utterances
        ])

        prompt = f"""
        You are a professional meeting analyst. Summarize this meeting transcript.

        TRANSCRIPT:
        {text_with_speakers}

        Extract:
        1. Overall summary (3-4 sentences)
        2. Key topics discussed
        3. Decisions made
        4. Sentiment: overall tone (positive, neutral, tense)
        5. Speaker roles: who was leading? who was quiet?

        Return JSON with keys: summary, topics, decisions, sentiment, speaker_roles.
        """
        response = self.llm.generate(prompt, task_type="summarization")
        raw_content = response.get("response", "{}")
        
        try:
            # Try to parse the response as JSON
            data = json.loads(raw_content)
            if isinstance(data, dict):
                # Ensure all required keys exist
                required_keys = ["summary", "topics", "decisions", "sentiment", "speaker_roles"]
                for key in required_keys:
                    if key not in data:
                        data[key] = "N/A" if key in ["summary", "sentiment", "speaker_roles"] else []
                return data
            else:
                return self._get_fallback_summary(f"LLM returned {type(data).__name__} instead of dictionary.")
        except json.JSONDecodeError:
            # If standard parsing fails, try to extract JSON from markdown blocks
            import re
            json_match = re.search(r'```json\n(.*?)\n```', raw_content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    if isinstance(data, dict):
                        return data
                except json.JSONDecodeError:
                    pass
            
            return self._get_fallback_summary("Could not parse JSON from LLM response.")

    def _get_fallback_summary(self, error_msg: str) -> dict:
        return {
            "summary": f"Error: {error_msg}",
            "topics": [],
            "decisions": [],
            "sentiment": "unknown",
            "speaker_roles": "unknown"
        }