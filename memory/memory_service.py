import redis
import json
import time

class MemoryService:
    def __init__(self, host='localhost', port=6379, db=0):
        self.r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    # --- Session Memory (Short-term context) ---
    def set_session_context(self, session_id, context, ttl=600):
        """Set or update short-term context for an active session."""
        self.r.setex(f"session:{session_id}", ttl, json.dumps(context))

    def get_session_context(self, session_id):
        """Retrieve active session context."""
        data = self.r.get(f"session:{session_id}")
        return json.loads(data) if data else {}

    def clear_session(self, session_id):
        self.r.delete(f"session:{session_id}")

    # --- Persistent Memory (Long-term patient history) ---
    def save_patient_history(self, patient_id, key, value):
        """Save a specific preference or history item for a patient."""
        self.r.hset(f"patient:{patient_id}", key, value)

    def get_patient_history(self, patient_id):
        """Get all stored history for a patient."""
        return self.r.hgetall(f"patient:{patient_id}")

    def update_last_interaction(self, patient_id):
        self.r.hset(f"patient:{patient_id}", "last_interaction", int(time.time()))

    def get_preferred_language(self, patient_id):
        return self.r.hget(f"patient:{patient_id}", "preferred_language") or "English"

class MockMemoryService:
    """Fallback if Redis is not available."""
    def __init__(self):
        self.sessions = {}
        self.patients = {}

    def set_session_context(self, session_id, context, ttl=600):
        self.sessions[session_id] = context

    def get_session_context(self, session_id):
        return self.sessions.get(session_id, {})

    def clear_session(self, session_id):
        if session_id in self.sessions: del self.sessions[session_id]

    def save_patient_history(self, patient_id, key, value):
        if patient_id not in self.patients: self.patients[patient_id] = {}
        self.patients[patient_id][key] = value

    def get_patient_history(self, patient_id):
        return self.patients.get(patient_id, {})

    def update_last_interaction(self, patient_id):
        self.save_patient_history(patient_id, "last_interaction", int(time.time()))

    def get_preferred_language(self, patient_id):
        return self.get_patient_history(patient_id).get("preferred_language", "English")
