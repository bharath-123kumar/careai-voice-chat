import os
import json
from openai import AsyncOpenAI
from scheduler.appointment_engine import AppointmentEngine
from memory.memory_service import MemoryService

class AgentService:
    def __init__(self, openai_api_key, appointment_engine: AppointmentEngine, memory_service: MemoryService):
        self.api_key = openai_api_key
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.engine = appointment_engine
        self.memory = memory_service
        self.system_prompt = """
        You are a highly efficient, multilingual Clinical Appointment Voice AI.
        Supported Languages: English, Hindi, Tamil.
        Your goal is to book, reschedule, or cancel appointments.
        """

    async def handle_request(self, session_id, patient_id, user_input, history=[]):
        user_input_lower = user_input.lower()
        context = self.memory.get_session_context(session_id)
        current_state = context.get("mock_state", "START")

        if self.api_key == "sk-placeholder" or not self.api_key:
            # Simple State Machine for Demo
            if "hello" in user_input_lower or "hi" in user_input_lower:
                self.memory.set_session_context(session_id, {"mock_state": "START"})
                return "[DEMO] Hello! I'm your clinical assistant. Would you like to book an appointment or check doctor availability?"
            
            elif "book" in user_input_lower or "appointment" in user_input_lower:
                self.memory.set_session_context(session_id, {"mock_state": "SELECTING_DOCTOR"})
                return "[DEMO] Sure! We have Dr. Sharma (Cardiologist) and Dr. Priya (Dermatologist). Who would you like to see?"
            
            elif current_state == "SELECTING_DOCTOR":
                self.memory.set_session_context(session_id, {"mock_state": "CONFIRMING"})
                return f"[DEMO] Great choice. I see a slot for {user_input} tomorrow at 10 AM. Should I confirm this for you?"
            
            elif current_state == "CONFIRMING" and ("yes" in user_input_lower or "sure" in user_input_lower or "confirm" in user_input_lower):
                self.memory.set_session_context(session_id, {"mock_state": "FINISHED"})
                return "[DEMO] Successfully booked! You will receive an SMS shortly. Is there anything else?"
            
            elif "doctor" in user_input_lower or "list" in user_input_lower:
                return "[DEMO] We have specialists in Cardiology, Dermatology, and General Medicine. Which department are you looking for?"
            
            else:
                return f"[DEMO] I understood: '{user_input}'. How can I help you further with your clinical booking?"

        # Real Logic
        context = self.memory.get_session_context(session_id)
        messages = [{"role": "system", "content": self.system_prompt}]
        for msg in history: messages.append(msg)
        messages.append({"role": "user", "content": user_input})

        tools = [
            {"type": "function", "function": {"name": "get_doctors", "parameters": {"type": "object", "properties": {"specialty": {"type": "string"}}}}}
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        return response.choices[0].message.content
