from openai import OpenAI

import config
from prompts import SUMMARY_PROMPT


def get_client() -> OpenAI:
    return OpenAI(
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
    )


def chat_completion(messages: list[dict], *, temperature: float = 0.7, max_tokens: int = 500) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if response.usage:
        print("USAGE:", response.usage)
    content = response.choices[0].message.content
    return content or "（模型没有返回内容）"


def generate_summary(history_text: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=config.SUMMARY_MODEL,
        messages=[
            {
                "role": "user",
                "content": SUMMARY_PROMPT.format(history=history_text),
            }
        ],
    )
    return response.choices[0].message.content or ""
