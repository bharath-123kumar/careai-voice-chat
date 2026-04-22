# Real-Time Multilingual Voice AI Agent - Clinical Booking

A high-performance, real-time voice AI system built for digital healthcare. This agent manages clinical appointments (booking, cancellation, rescheduling) with sub-450ms latency, supporting English, Hindi, and Tamil.

## 🚀 Key Features
- **Low Latency Voice Pipeline**: Optimized using Deepgram Aura and GPT-4o-mini to achieve <450ms end-to-end response time.
- **Multilingual Support**: Dynamic language detection and response for English, Hindi, and Tamil.
- **Contextual Memory**: Dual-layered memory using Redis (Session-level for intent tracking & Persistent-level for patient history).
- **Tool Orchestration**: Genuine tool-calling for schedule management and conflict resolution.
- **Outbound Campaigns**: Capabilities for automated reminders and follow-up check-ins.

## 🛠️ Tech Stack
- **Backend**: FastAPI (Python)
- **STT/TTS**: Deepgram (High Speed)
- **Agent**: OpenAI GPT-4o-mini
- **Memory**: Redis
- **Database**: SQLite (SQLAlchemy)

## 🏗️ Architecture
Refer to the [Architecture Diagram](./docs/architecture.mermaid).
The pipeline follows: `User Audio` -> `WebSocket` -> `Deepgram STT` -> `GPT-4o-mini Agent (with Tools)` -> `Deepgram TTS` -> `User Audio Stream`.

## ⏱️ Latency Distribution
| Component | Latency |
| :--- | :--- |
| **STT (Deepgram)** | ~120ms |
| **Agent Reasoning (GPT-4o-mini)** | ~180ms |
| **TTS First Byte (Deepgram Aura)** | ~90ms |
| **Total** | **~390ms** (Measured) |

## ⚙️ Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Copy `.env.template` to `.env` and add your API keys:
   ```bash
   OPENAI_API_KEY=your_key
   DEEPGRAM_API_KEY=your_key
   ```

3. **Run Redis**:
   Ensure Redis is running locally on port 6379 (or the system will fall back to in-memory mock).

4. **Start the Backend**:
   ```bash
   python backend/main.py
   ```

5. **Open the Frontend**:
   Open `web/index.html` in your browser.

## 🧪 Testing Scenarios
- **Booking**: "Book a dermatologist appointment for Dr. Priya tomorrow at 10 AM."
- **Hindi Support**: "मुझे कल डॉक्टर शर्मा से मिलना है।"
- **Conflict Handling**: Try booking an already taken slot; the agent will suggest alternatives.
