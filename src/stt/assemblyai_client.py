# src/stt/assemblyai_client.py
import requests
import time
import json
from src.config.settings import settings

ASSEMBLYAI_BASE = "https://api.assemblyai.com/v2"

headers = {
    "authorization": settings.assemblyai_api_key,
    "content-type": "application/json"
}

def transcribe_audio_file(file_path: str) -> dict:
    """
    Uploads a local audio file and returns transcript with speaker labels.
    Supports: mp3, wav, m4a
    """
    # Step 1: Upload file
    upload_url = upload_file(file_path)
    
    # Step 2: Start transcription with diarization
    data = {
        "audio_url": upload_url,
        "speaker_labels": True,
        "language_code": "en_us"
    }
    
    response = requests.post(f"{ASSEMBLYAI_BASE}/transcript", json=data, headers=headers)
    transcript_id = response.json()['id']
    
    # Step 3: Poll for completion
    polling_endpoint = f"{ASSEMBLYAI_BASE}/transcript/{transcript_id}"
    
    while True:
        result = requests.get(polling_endpoint, headers=headers).json()
        if result['status'] == 'completed':
            return result
        elif result['status'] == 'error':
            raise Exception(f"Transcription failed: {result['error']}")
        time.sleep(1)

def upload_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        response = requests.post(f"{ASSEMBLYAI_BASE}/upload", headers=headers, data=f)
    return response.json()["upload_url"]