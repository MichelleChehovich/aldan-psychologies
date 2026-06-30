from openai import OpenAI
from app.config import get_provider_config
import asyncio


def get_llm_client(provider: str = "proxyapi") -> OpenAI:
    config = get_provider_config(provider)
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )


def get_chat_model(provider: str = "proxyapi") -> str:
    config = get_provider_config(provider)
    return config["chat_model"]


async def chat_completion(
    messages: list,
    provider: str = "proxyapi",
    temperature: float = 0.7,
    max_tokens: int = 4000,
) -> str:
    import json
    from datetime import datetime
    
    config = get_provider_config(provider)
    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
    model = config["chat_model"]
    
    # Логируем запрос
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/app/storage/processing.log", "a") as f:
        f.write(f"[{timestamp}] [LLM] Calling {provider} model {model}\n")
        f.write(f"[{timestamp}] [LLM] Messages count: {len(messages)}\n")
        if messages:
            f.write(f"[{timestamp}] [LLM] First message length: {len(messages[0]['content'])}\n")
            f.write(f"[{timestamp}] [LLM] First 200 chars: {messages[0]['content'][:200]}\n")
    
    def _sync_call():
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response
    
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(None, _sync_call)
    
    content = response.choices[0].message.content if response.choices else ""
    
    # Логируем ответ
    with open("/app/storage/processing.log", "a") as f:
        f.write(f"[{timestamp}] [LLM] Response length: {len(content) if content else 0}\n")
        f.write(f"[{timestamp}] [LLM] Finish reason: {response.choices[0].finish_reason if response.choices else 'N/A'}\n")
        if content:
            f.write(f"[{timestamp}] [LLM] First 200 chars of response: {content[:200]}\n")
        else:
            f.write(f"[{timestamp}] [LLM] EMPTY RESPONSE\n")
            f.write(f"[{timestamp}] [LLM] Full response object: {str(response)[:500]}\n")
    
    return content if content else ""
