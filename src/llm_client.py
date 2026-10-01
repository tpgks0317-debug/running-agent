"""Thin wrapper around the OpenAI-compatible chat API (Groq or xAI)."""
from openai import OpenAI

from src import config

_client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)


def chat(messages: list[dict], tools: list[dict] | None = None):
    """Send messages (and optional tool schemas) to the LLM and return the assistant message."""
    kwargs = {}
    if tools is not None:
        kwargs["tools"] = tools
    response = _client.chat.completions.create(model=config.MODEL, messages=messages, **kwargs)
    return response.choices[0].message


if __name__ == "__main__":
    reply = chat([{"role": "user", "content": "Hello"}])
    print(reply.content)
