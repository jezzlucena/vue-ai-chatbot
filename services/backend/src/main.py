import json
from threading import Thread
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from torch import cuda
from transformers import AutoModelForCausalLM, AutoTokenizer, AsyncTextIteratorStreamer

class Message(BaseModel):
    role: str
    content: str

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

device = "cuda" if cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map=device
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

EOS_TOKEN = "<|im_end|>"

messages: List[Message] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "https://chatbot.jezzlucena.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)

            if (data['type'] == 'reset'):
                del messages [:]
                await manager.broadcast(json.dumps({ 'type': "reset" }))
            elif (data['type'] == 'userMessage'):
                messages.append({ 'role': "user", 'content': data['content'] })

                await manager.broadcast(json.dumps({
                    'type': "userMessage",
                    'content': data['content']
                }))

                # Tokenize the input text and history
                inputs = tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                model_inputs = tokenizer([inputs], return_tensors="pt").to(device)

                decode_kwargs = dict(skip_special_tokens=True)
                streamer = AsyncTextIteratorStreamer(tokenizer, skip_prompt=True, decode_kwargs=decode_kwargs)
                generation_kwargs = dict(**model_inputs, streamer=streamer, max_new_tokens=512)

                thread = Thread(target=model.generate, kwargs=generation_kwargs)
                thread.start()

                stream_started = False

                response = { "role": "assistant", "content": "" }

                # Add interaction to conversation history preemptively
                messages.append(response)

                async for chunk in streamer:
                    if (not stream_started and chunk != ""):
                        await manager.broadcast(json.dumps({
                            'type': "assistantMessageStart"
                        }))
                        stream_started = True
                    
                    word = chunk
                    if (chunk.endswith(EOS_TOKEN)):
                        word = word.split(EOS_TOKEN)[0]
                    await manager.broadcast(json.dumps({
                        'type': "assistantChunk",
                        'content': word
                    }))

                    response["content"] += word

                await manager.broadcast(json.dumps({
                    'type': "assistantMessageEnd"
                }))
            elif (data['type'] == 'prompt'):
                messages.append({ 'role': "system", 'content': data['content'] })
                
                await manager.broadcast(json.dumps({
                    'type': "prompt",
                    'content': data['content']
                }))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/messages")
def get_messages() -> List[Message]:
    return messages