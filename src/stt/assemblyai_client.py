# src/stt/assemblyai_client.py
import requests
import time
import json
import logging
from src.config.settings import settings

logger = logging.getLogger("assemblyai")
ASSEMBLYAI_BASE = "https://api.assemblyai.com/v2"

headers = {
    "authorization": settings.assemblyai_api_key or "",
    "content-type": "application/json"
}

def transcribe_audio_file(file_path: str) -> dict:
    """
    Uploads a local audio file and returns transcript with speaker labels.
    Supports: mp3, wav, m4a
    """
    if not settings.assemblyai_api_key:
        raise ValueError("ASSEMBLYAI_API_KEY is not set in environment variables.")

    # Step 1: Upload file
    logger.info(f"Uploading file: {file_path}")
    upload_url = upload_file(file_path)
    
    # Step 2: Start transcription with diarization
    data = {
        "audio_url": upload_url,
        "speaker_labels": True,
        "language_code": "en_us"
    }
    
    logger.info("Starting transcription...")
    response = requests.post(f"{ASSEMBLYAI_BASE}/transcript", json=data, headers=headers)
    
    if response.status_code != 200:
        error_detail = response.json().get("error", response.text)
        raise Exception(f"Failed to start transcription (HTTP {response.status_code}): {error_detail}")
        
    transcript_id = response.json().get('id')
    if not transcript_id:
        raise Exception(f"No transcript ID returned from AssemblyAI. Response: {response.text}")
    
    # Step 3: Poll for completion
    polling_endpoint = f"{ASSEMBLYAI_BASE}/transcript/{transcript_id}"
    
    logger.info(f"Polling for transcript {transcript_id}...")
    while True:
        resp = requests.get(polling_endpoint, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Error polling transcription (HTTP {resp.status_code}): {resp.text}")
            
        result = resp.json()
        if result['status'] == 'completed':
            logger.info("Transcription completed successfully.")
            return result
        elif result['status'] == 'error':
            raise Exception(f"Transcription failed: {result.get('error', 'Unknown error')}")
            
        time.sleep(3) # Increase sleep to be respectful and reduce requests

def upload_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        response = requests.post(f"{ASSEMBLYAI_BASE}/upload", headers=headers, data=f)
    
    if response.status_code != 200:
        error_detail = response.json().get("error", response.text)
        raise Exception(f"Failed to upload file to AssemblyAI (HTTP {response.status_code}): {error_detail}")
        
    return response.json().get("upload_url")