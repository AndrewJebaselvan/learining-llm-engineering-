import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr


load_dotenv(override = True)

google_api_key = os.getenv('GOOGLE_API_KEY')
if google_api_key:
    print("Google API Key exists and begins {google_api_key[:2]}")
else:
    print("Google API Key not set (and this is optional)")
gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini = OpenAI(
    api_key=google_api_key,
    base_url=gemini_url
)
system_message = "you are a Helpful assistant"

def message_gemnini(prompt):
    messages = [{"role":"system","content":system_message},{"role":"user","content":prompt}]
    response = gemini.chat.completions.create(model = "gemini-2.5-flash", messages = messages)
    return response.choices[0].message.content
message_gemnini("tell me a joke about today and tomorrow")

"""def shout(text):
    print(f"shout function has been called with input {text}")
    return text.upper()
shout("hello")"""

view = gr.Interface(
    fn=message_gemnini,
    inputs=gr.Textbox(label="Enter your prompt"),
    outputs=gr.Textbox(label="Gemini response"),
    title="Test"
)

view.launch(
    auth=("user", "password")
)