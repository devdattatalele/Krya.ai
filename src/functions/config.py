import os
import google.generativeai as genai
from dotenv import load_dotenv


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def get_full_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)

instruction_path = get_full_path("system/instruction.txt")

with open(instruction_path, "r", encoding="utf-8") as f:
    instruct = f.read()

def configure_model():
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    generation_config = {
        "temperature": 1.55,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config=generation_config,
        system_instruction=instruct,

    )
    return model
