from torch import cuda

EOS_TOKEN = "<|im_end|>"
"""End of Sequence token, special token used
by Qwen to mark the end of a series of streamable
chunks in a message from the assistant"""

PARAGRAPH_TOKEN = "\n\n"
"""Sequence that represents a paragraph, used
to translate paragraphs into separate messages
during the message stream"""

INITIAL_COLOR = "rgb(59 130 246)"
"""Initial user color for the chat bubbles and UI,
inspired from Tailwind's bg-blue-500"""

MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
"""Name of the Hugging Face model that will be used"""

DEVICE = "cuda" if cuda.is_available() else "cpu"
"""Device that will process the compute, (cuda = GPU,
or cpu = CPU). Keep in mind that GPU processing tends
to be much more performant. Warning: CUDA drivers only
exist for Windows at this time"""