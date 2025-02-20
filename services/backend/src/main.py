from typing import List
from fastapi import FastAPI
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
    allow_origins=["http://localhost:8081", "http://143.198.102.62:8081", "http://jezzlucena.com:8081", "http://jezzlucena.xyz:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from fastapi.staticfiles import StaticFiles
# import os
# parent_dir = os.path.dirname(os.path.abspath(__file__))
# app.mount("/dist", StaticFiles(directory=os.path.join(parent_dir, "..", "..", "frontend", "dist"), html=True), name="dist")

@app.get("/messages")
def get_messages() -> List[Message]:
    return messages

@app.post("/messages")
def create_message(message: Message) -> Message:
    # Add interaction to conversation history
    messages.append(message)

    if (message.role == "system"):
        return message

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

@app.delete("/messages")
def delete_messages():
    del messages [:]
    return messages