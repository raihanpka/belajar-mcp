from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
import os

class GPT:
    Message = ChatCompletionMessage
    def __init__(self, model: str):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def add_user_message(self, messages: list, message):
        if isinstance(message, self.Message):
            content = message.content
        elif isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = message
        user_message = {
            "role": "user",
            "content": content,
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        if isinstance(message, self.Message):
            assistant_message = {
                "role": "assistant",
                "content": message.content,
            }
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                assistant_message["tool_calls"] = tool_calls
        elif isinstance(message, dict):
            assistant_message = {
                "role": "assistant",
                "content": message.get("content", ""),
            }
            tool_calls = message.get("tool_calls")
            if tool_calls:
                assistant_message["tool_calls"] = tool_calls
        else:
            assistant_message = {
                "role": "assistant",
                "content": message,
            }
        messages.append(assistant_message)

    def text_from_message(self, message):
        # Support both ChatCompletionMessage and dict-like messages
        if isinstance(message, self.Message):
            return message.content
        if isinstance(message, dict):
            return message.get("content", "")
        return message

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
