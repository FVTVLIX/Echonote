# src/core/meeting_orchestrator.py
from src.stt.assemblyai_client import transcribe_audio_file
from src.agents.summarizer import SummarizerAgent
from src.agents.action_extractor import ActionExtractor
from src.agents.critic import CriticAgent
from src.agents.executor import ExecutorAgent
import json, logging

logger = logging.getLogger("meeting_orch")

class MeetingOrchestrator:
    def __init__(self, execution_tool: str = "gmail"):
        self.summarizer = SummarizerAgent()
        self.extractor = ActionExtractor()
        self.critic = CriticAgent()
        self.executor = ExecutorAgent(tool=execution_tool)

    def process_meeting(self, audio_file: str, execution_tool: str = None, feedback_data: dict = None):
        if execution_tool:
            self.executor.tool = execution_tool.lower()
        # Step 1: Transcribe
        logger.info("Transcribing audio...")
        transcript_data = transcribe_audio_file(audio_file)
        transcript_text = " ".join([u['text'] for u in transcript_data['utterances']])

        # Step 2: Summarize
        summary = self.summarizer.summarize_transcript(transcript_data)

        # Step 3: Extract action items
        actions = self.extractor.extract(transcript_text)

        # Step 4: (Optional) Critique if feedback provided
        if feedback_data:
            critique = self.critic.evaluate_extraction(transcript_text, actions, feedback_data['gold'])
            # Use critique to improve prompt (via Optimizer pattern from Project 2)
            # ... (reuse OptimizerAgent logic)

        # Step 5: Execute
        self.executor.execute_action_items(actions, summary['summary'])

        return {
            "summary": summary,
            "action_items": actions,
            "transcript": transcript_text,
            "status": "completed"
        }