from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from backend.agent import run_agent
from backend.drive_service import get_folder_analytics

load_dotenv()

app = FastAPI(title="Google Drive AI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    message: str
    folder_id: str | None = None
    chat_history: list = []

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/connect")
async def connect_folder(request: ConnectRequest):
    import re
    # Extract folder ID from URL
    match = re.search(r"/folders/([a-zA-Z0-9\-_]+)", request.url)
    if not match:
        match = re.search(r"id=([a-zA-Z0-9\-_]+)", request.url)
    
    if not match:
        raise HTTPException(status_code=400, detail="Invalid Google Drive folder link")
    
    folder_id = match.group(1)
    
    try:
        analytics = get_folder_analytics(folder_id)
        return {"folder_id": folder_id, "analytics": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        response = run_agent(request.message, request.folder_id, request.chat_history)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
