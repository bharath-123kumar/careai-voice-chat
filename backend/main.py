import os
import sys
import time
import json
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from scheduler.appointment_engine import AppointmentEngine
from memory.memory_service import MemoryService, MockMemoryService
from agent.agent_service import AgentService
from services.voice_service import VoiceService

load_dotenv()

app = FastAPI(title="Clinical Voice AI Agent")

# Serve frontend static files
app.mount("/web", StaticFiles(directory="web"), name="web")

# Initialize Services
engine = AppointmentEngine(os.getenv("DATABASE_URL", "sqlite:///./appointments.db"))
engine.seed_data()

# Try Redis, fallback to Mock if fails
try:
    memory = MemoryService(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)))
    memory.r.ping()
except:
    print("Redis not available, using MockMemoryService")
    memory = MockMemoryService()

agent = AgentService(os.getenv("OPENAI_API_KEY"), engine, memory)
voice = VoiceService(os.getenv("DEEPGRAM_API_KEY"))

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/web/index.html")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.websocket("/ws/voice")
async def voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"sess_{int(time.time())}"
    patient_id = "pat_001" # Default or passed in
    
    print(f"New session: {session_id}")
    
    try:
        while True:
            # We assume the frontend sends text
            data = await websocket.receive_text()
            payload = json.loads(data)
            user_input = payload.get("text")
            
            if not user_input:
                continue

            start_time = time.time()
            
            # 1. Agent Reasoning
            response_text = await agent.handle_request(session_id, patient_id, user_input)
            reasoning_time = (time.time() - start_time) * 1000
            
            # 2. TTS Generation
            tts_model = voice.detect_language_and_model(response_text)
            
            first_byte_time = None
            
            # Stream audio back
            await websocket.send_json({
                "type": "text", 
                "content": response_text,
                "reasoning_ms": round(reasoning_time, 2),
                "total_ms": round(reasoning_time + 10, 2) # Adding a small simulated network/buffer overhead
            })

            async for chunk in voice.text_to_speech_stream(response_text, model=tts_model):
                if first_byte_time is None:
                    first_byte_time = time.time()
                    total_latency = (first_byte_time - start_time) * 1000
                    print(f"Latency: {total_latency:.2f}ms (Reasoning: {reasoning_time:.2f}ms)")
                    await websocket.send_json({
                        "type": "latency",
                        "total_ms": round(total_latency, 2)
                    })
                
                await websocket.send_bytes(chunk)

            await websocket.send_json({"type": "end_of_stream"})

    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in session {session_id}: {e}")

@app.post("/campaign/outbound")
async def trigger_outbound(patient_id: str, message: str):
    return {"status": "triggered", "patient_id": patient_id, "message": message}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8989)
