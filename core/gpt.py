from openai import OpenAI
import os

class GPT:
    def __init__(self, model: str):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def add_user_message(self, messages: list, message):
        user_message = {
            "role": "user",
            "content": message["content"]
            if isinstance(message, dict)
            else message,
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        assistant_message = {
            "role": "assistant",
            "content": message["content"]
            if isinstance(message, dict)
            else message,
        }
        messages.append(assistant_message)

    def text_from_message(self, message):
        # OpenAI selalu return string langsung di content
        return message["content"]

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop_sequences=None,
        tools=None,
    ):
        # Masukkan system prompt jika ada
        if system:
            messages = [{"role": "system", "content": system}] + messages

        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if stop_sequences:
            params["stop"] = stop_sequences

        if tools:
            params["tools"] = tools

        completion = self.client.chat.completions.create(**params)
        return completion.choices[0].message
