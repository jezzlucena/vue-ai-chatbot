import json
import random
from threading import Thread
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from torch import cuda
from transformers import AutoModelForCausalLM, AutoTokenizer, AsyncTextIteratorStreamer

class Message(BaseModel):
    role: str
    content: str
    color: Optional[str] = None

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

device = "cuda" if cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map=device
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

EOS_TOKEN = "<|im_end|>"
PARAGRAPH_TOKEN = "\n\n"
INITIAL_COLOR = "rgb(59 130 246)"

messages: List[Message] = []
random_colors: List[str] = [INITIAL_COLOR]
color_index = 0

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "https://chatbot.jezzlucena.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def random_dark_color():
    low = random.randint(0, 50)
    mid = random.randint(0, 150)
    high = random.randint(0, 255)

    components = [
        { 'value': low, 'sortFactor': random.random() },
        { 'value': mid, 'sortFactor': random.random() },
        { 'value': high, 'sortFactor': random.random() }
    ]

    components.sort(key=lambda x: x['sortFactor'])

    red = components[0]['value']
    green = components[1]['value']
    blue = components[2]['value']

    return f"rgb({red}, {green}, {blue})"

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
        global color_index
        if (color_index >= len(random_colors)):
            random_colors.append(random_dark_color())
        await websocket.send_text(json.dumps({ 'type': "color", 'content': random_colors[color_index] }))
        print(random_colors[color_index])
        color_index += 1
        while True:
            text = await websocket.receive_text()
            data = json.loads(text)

            if (data['type'] == 'reset'):
                del messages [:]
                del random_colors [:]
                random_colors.append(INITIAL_COLOR)
                color_index = 0
                await manager.broadcast(json.dumps({ 'type': "reset" }))
            elif (data['type'] == 'userMessage'):
                messages.append({ 'role': "user", 'content': data['content'], 'color': data['color'] })

                await manager.broadcast(json.dumps({
                    'type': "userMessage",
                    'content': data['content'],
                    'color': data['color']
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
                    elif (chunk.endswith(PARAGRAPH_TOKEN)):
                        word = word.split(PARAGRAPH_TOKEN)[0]
                    await manager.broadcast(json.dumps({
                        'type': "assistantChunk",
                        'content': word
                    }))

                    response["content"] += word
                    
                    if (chunk.endswith(PARAGRAPH_TOKEN)):
                        await manager.broadcast(json.dumps({
                            'type': "assistantMessageEnd"
                        }))
                        response = { "role": "assistant", "content": "" }
                        messages.append(response)
                        await manager.broadcast(json.dumps({
                            'type': "assistantMessageStart"
                        }))

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