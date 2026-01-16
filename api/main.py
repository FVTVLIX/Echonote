# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.websockets import WebSocket
import asyncio
import os
from src.core.meeting_orchestrator import MeetingOrchestrator
from src.config.settings import settings

app = FastAPI()
orchestrator = MeetingOrchestrator()

# Ensure data directory exists
os.makedirs(settings.data_dir, exist_ok=True)

@app.post("/process")
async def process_meeting(file: UploadFile = File(...), tool: str = "gmail"):
    file_path = os.path.join(settings.data_dir, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        result = orchestrator.process_meeting(file_path, execution_tool=tool)
        return result
    except Exception as e:
        print(f"Error processing meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    Real-time transcription endpoint.
    Note: Requires client to send audio chunks.
    """
    await websocket.accept()
    await websocket.send_text("Real-time transcription connection established.")
    
    try:
        while True:
            # Wait for audio chunks from the client
            data = await websocket.receive_bytes()
            # In a live integration, these chunks would be streamed to AssemblyAI
            # For now, we acknowledge receipt to keep the connection alive
            await websocket.send_text(f"Processing {len(data)} bytes...")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()