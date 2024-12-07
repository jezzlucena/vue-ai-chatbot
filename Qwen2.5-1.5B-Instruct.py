from time import time_ns
from torch import bfloat16, cuda
from transformers import AutoModelForCausalLM, AutoTokenizer

def current_secs():
    return int(time_ns() / 1000000000)

model_name = "Qwen/Qwen2.5-1.5B-Instruct"

device = "cuda" if cuda.is_available() else "cpu"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=bfloat16,
    device_map=device
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

print("Starting LLM (model name: " + model_name + ")")

messages = [{ "role": "system", "content": "You are a helpful assistant." }]

while True:
    # Get the input data from the user
    input_text = input("> ")

    if input_text.lower() in ["exit", "exit()"]:
        break

    # Add interaction to conversation history
    messages.append({ "role": "user", "content": input_text })

    # Mark the time where computation starts (in seconds)
    latest_time_secs = current_secs()
    print("Computing...")

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
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

    # Erase the line that says "Computing..." and move
    # the cursor one line up
    print("\033[A                             \033[A")
    print("Response processed in " + str(current_secs() - latest_time_secs) + " seconds.")

    # Print the response from the LLM to the console
    print(response)

    # Add interaction to conversation history
    messages.append({ "role": "assistant", "content": response })

print("Successfuly finished running LLM (model name: " + model_name + ")")
