from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from torch import bfloat16, cuda
from transformers import AutoModelForCausalLM, AutoTokenizer

class Message(BaseModel):
    role: str
    content: str

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

device = "cuda" if cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=bfloat16,
    device_map=device
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

messages: List[Message] = [{ "role": "system", "content": "You are a helpful assistant." }]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "Hello, World!"

@app.get("/messages")
def get_messages() -> List[Message]:
    return messages

@app.post("/messages")
def create_message(message: Message) -> Message:
    # Add interaction to conversation history
    messages.append(message)

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

    return response

@app.get("/clear_messages")
def clear_messages():
    del messages [:]
    messages.append({ "role": "system", "content": "You are a helpful assistant." })
    return messages