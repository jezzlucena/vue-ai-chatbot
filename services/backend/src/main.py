import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from torch import cuda
from transformers import AutoModelForCausalLM, AutoTokenizer

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

messages: List[Message] = []

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", "http://143.198.102.62:8081", "https://chatbot.jezzlucena.com", "https://chatbot.jezzlucena.xyz"],
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

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

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

                # Generate the response from the model
                outputs = model.generate(
                    **model_inputs,
                    max_new_tokens=512
                )

                # Decode the response
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, outputs)
                ]
                response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                response = { "role": "assistant", "content": response_text }

                # Add interaction to conversation history
                messages.append(response)
                
                await manager.broadcast(json.dumps({
                    'type': "assistantMessage",
                    'content': response_text
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