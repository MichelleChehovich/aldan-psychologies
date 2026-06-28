import os

def get_supabase_url():
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise RuntimeError("SUPABASE_URL is missing")
    return url

def get_supabase_key():
    key = os.getenv("SUPABASE_KEY")
    if not key:
        raise RuntimeError("SUPABASE_KEY is missing")
    return key

# =====================================================
# LLM PROVIDERS CONFIGURATION
# =====================================================

LLM_PROVIDERS = {
    "proxyapi": {
        "name": "ProxyAPI",
        "base_url": "https://api.proxyapi.ru/openai/v1",
        "api_key": os.getenv("PROXYAPI_KEY"),
        "transcription_model": "gpt-4o-transcribe",
        "chat_model": "gpt-4o-mini",
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.getenv("OPENROUTER_KEY"),
        "transcription_model": "openai/whisper-1",
        "chat_model": "openai/gpt-4o-mini",
    },
    "openai": {
        "name": "OpenAI Direct",
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("OPENAI_API_KEY"),
        "transcription_model": "gpt-4o-transcribe",
        "chat_model": "gpt-4o",
    },
}

PROVIDER_DESCRIPTIONS = {
    "proxyapi":   "Российский прокси с доступом к OpenAI моделям",
    "openrouter": "Международный прокси с множеством моделей",
    "openai":     "Прямой доступ к OpenAI API",
}

DEFAULT_PROVIDER = "proxyapi"


def get_provider_config(provider: str = None):
    """
    Get provider configuration by name.
    Falls back to DEFAULT_PROVIDER if not specified.
    Получаем конфигурацию провайдера по имени.
    Если не указано иное, возвращается к параметру DEFAULT_PROVIDER.

    """
    if not provider:
        provider = DEFAULT_PROVIDER

    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")

    config = LLM_PROVIDERS[provider]
    if not config["api_key"]:
        raise RuntimeError(f"API key missing for provider: {provider}")

    return config


def get_available_providers():
    """
    Return list of providers that have API keys configured.
    Возвращает список поставщиков, у которых настроены ключи API.
    """
    available = []
    for code, config in LLM_PROVIDERS.items():
        if config.get("api_key"):
            available.append({
                "code": code,
                "name": config["name"],
                "description": PROVIDER_DESCRIPTIONS.get(code, ""),
            })
