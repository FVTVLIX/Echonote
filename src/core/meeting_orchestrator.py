# src/core/meeting_orchestrator.py
from src.stt.assemblyai_client import transcribe_audio_file
from src.agents.summarizer import SummarizerAgent
from src.agents.action_extractor import ActionExtractor
from src.agents.critic import CriticAgent
from src.agents.executor import ExecutorAgent
import json, logging

# Configure logging
logging.basicConfig(level=logging.INFO)
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
        
        try:
            # Step 1: Transcribe
            logger.info(f"Transcribing audio from {audio_file}...")
            transcript_data = transcribe_audio_file(audio_file)
            
            # Validation Step 1
            if not isinstance(transcript_data, dict) or 'utterances' not in transcript_data:
                raise ValueError(f"Invalid transcript data format. Expected dict with 'utterances', got {type(transcript_data).__name__}")
                
            transcript_text = " ".join([u.get('text', '') for u in transcript_data.get('utterances', [])])
            logger.info(f"Transcription complete. Text length: {len(transcript_text)}")

            # Step 2: Summarize
            logger.info("Generating summary...")
            summary = self.summarizer.summarize_transcript(transcript_data)
            
            # Validation Step 2
            if not isinstance(summary, dict):
                logger.warning(f"Summarizer returned {type(summary).__name__}, using fallback.")
                summary = {"summary": str(summary), "topics": [], "decisions": [], "sentiment": "unknown", "speaker_roles": "unknown"}
            
            summary_text = summary.get('summary', "No summary provided.")
            logger.info("Summary generated.")

            # Step 3: Extract action items
            logger.info("Extracting action items...")
            actions = self.extractor.extract(transcript_text)
            
            # Validation Step 3
            if not isinstance(actions, list):
                logger.warning(f"Extractor returned {type(actions).__name__}, using fallback.")
                actions = []
            logger.info(f"Extracted {len(actions)} action items.")

            # Step 4: (Optional) Critique
            if feedback_data:
                logger.info("Applying critique...")
                # Ensure actions is what critic expects
                self.critic.evaluate_extraction(transcript_text, actions, feedback_data.get('gold', []))

            # Step 5: Execute
            logger.info(f"Executing follow-ups via {self.executor.tool}...")
            self.executor.execute_action_items(actions, summary_text)

            return {
                "summary": summary,
                "action_items": actions,
                "transcript": transcript_text,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in meeting orchestration: {str(e)}", exc_info=True)
            return {
                "summary": {"summary": f"Process failed: {str(e)}", "topics": [], "decisions": [], "sentiment": "error", "speaker_roles": "error"},
                "action_items": [],
                "transcript": "Error during processing.",
                "status": "failed",
                "error": str(e)
            }