import asyncio
import websockets
import json
import time

async def test_agent():
    uri = "ws://localhost:8080/ws/voice"
    async with websockets.connect(uri) as websocket:
        print("--- Connected to Clinical Voice AI Agent ---")
        print("Type your request below (e.g. 'Book cardiology appointment')")
        print("Type 'exit' to quit.\n")

        while True:
            user_text = input("You: ")
            if user_text.lower() == 'exit':
                break
            
            start_time = time.time()
            
            # Send text request
            await websocket.send(json.dumps({"text": user_text}))
            
            # Receive response(s)
            while True:
                response = await websocket.recv()
                
                if isinstance(response, str):
                    data = json.loads(response)
                    if data["type"] == "text":
                        print(f"\nAgent: {data['content']}")
                        print(f"  [Reasoning Time: {data['reasoning_ms']}ms]")
                    elif data["type"] == "latency":
                        print(f"  [Total End-to-End Latency: {data['total_ms']}ms]")
                    elif data["type"] == "end_of_stream":
                        print("-" * 30)
                        break
                else:
                    # Audio data received (we'll just acknowledge it in CLI)
                    pass

if __name__ == "__main__":
    try:
        asyncio.run(test_agent())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
