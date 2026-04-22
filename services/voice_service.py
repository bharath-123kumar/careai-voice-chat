import os
import aiohttp
import json

class VoiceService:
    def __init__(self, api_key):
        self.api_key = api_key

    async def text_to_speech_stream(self, text, model="aura-asteria-en"):
        if self.api_key == "placeholder" or not self.api_key:
            # Skip TTS in demo mode
            print("Demo Mode: Skipping Deepgram TTS")
            return
            yield # dummy

        url = "https://api.deepgram.com/v1/speak"
        params = {"model": model, "encoding": "linear16", "container": "none", "sample_rate": 16000}
        headers = {"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"}
        payload = {"text": text}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, params=params) as response:
                if response.status == 200:
                    async for chunk in response.content.iter_any():
                        yield chunk
                else:
                    print(f"Deepgram TTS Error: {response.status}")

    def detect_language_and_model(self, text):
        from langdetect import detect
        try:
            lang = detect(text)
            if lang == 'hi': return "aura-orchard-hi"
            if lang == 'ta': return "aura-stella-ta"
            return "aura-asteria-en"
        except: return "aura-asteria-en"
