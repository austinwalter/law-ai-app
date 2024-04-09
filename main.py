from decouple import config
from openai import OpenAI
import gradio as gr
import yaml

client = OpenAI(api_key=config("OPENAI_API_KEY"))

prompt = ""

with open("prompt.yaml") as stream:
    try:
        prompt = yaml.safe_load(stream)
        print(prompt)
        print(prompt.get("system_prompt", '').strip())
    except yaml.YAMLError as exc:
        print(exc)

def predict(message, history, complaint):
    history_openai_format = []

    if message == "objection!":
      message = "tell me lawyer jokes"

    if len(history) == 0:
      history_openai_format.append({"role": "assistant", "content": prompt["system_prompt"].strip()})
      history_openai_format.append({"role": "assistant", "content": complaint})

    for human, assistant in history:
        history_openai_format.append({"role": "user", "content": human })
        history_openai_format.append({"role": "assistant", "content":assistant})
    
    history_openai_format.append({"role": "user", "content": message})
  
    response = client.chat.completions.create(
      model='gpt-4-turbo-preview',
      messages= history_openai_format,
      temperature=0,
      stream=True
    )

    partial_message = ""
    for chunk in response:
      if chunk.choices[0].delta.content is not None:
        partial_message = partial_message + chunk.choices[0].delta.content
        yield partial_message

gr.ChatInterface(predict, additional_inputs=[gr.Textbox(label="Complaint Summary")]).launch()