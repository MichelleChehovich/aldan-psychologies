from openai import OpenAI
from app.config import get_provider_config


def get_llm_client(provider: str = "proxyapi") -> OpenAI:
    """
    Create OpenAI client for chat completions based on provider.
    Создайте клиент OpenAI для завершения чата на основе провайдера.
    """
    config = get_provider_config(provider)
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )


def get_chat_model(provider: str = "proxyapi") -> str:
    """
    Get chat model for specific provider.
    Получите модель чата для конкретного провайдера.
    """
    config = get_provider_config(provider)
    return config["chat_model"]


async def chat_completion(
    messages: list,
    provider: str = "proxyapi",
    temperature: float = 0.7,
    max_tokens: int = 4000,
) -> str:
    """
    Make chat completion request.
    Returns the response text.
    Отправьте запрос на завершение разговора.
    Возвращает текст ответа.
    """
    client = get_llm_client(provider)
    model = get_chat_model(provider)

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
