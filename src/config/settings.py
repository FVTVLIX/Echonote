# src/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        self.assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY")
        
        self.gmail_credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
        self.gmail_token_path = os.getenv("GMAIL_TOKEN_PATH", "token.json")
        
        self.notion_api_key = os.getenv("NOTION_API_KEY")
        self.notion_database_id = os.getenv("NOTION_DATABASE_ID")
        
        self.trello_api_key = os.getenv("TRELLO_API_KEY")
        self.trello_token = os.getenv("TRELLO_TOKEN")
        self.trello_board_id = os.getenv("TRELLO_BOARD_ID")
        
        self.data_dir = os.getenv("DATA_DIR", "./data")
        
        # Default LLM provider
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")

settings = Settings()
