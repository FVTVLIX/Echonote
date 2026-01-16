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
        utterances = transcript['utterances']
        text_with_speakers = "\n".join([
            f"Speaker {u['speaker']}: {u['text']}" for u in utterances
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
        return json.loads(response["response"])