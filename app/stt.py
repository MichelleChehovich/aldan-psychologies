from openai import OpenAI
from app.config import get_provider_config


def get_transcription_client(provider: str = "proxyapi") -> OpenAI:
    """
    Create OpenAI client for transcription based on provider.
    """
    config = get_provider_config(provider)
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )


def get_transcription_model(provider: str = "proxyapi") -> str:
    """
    Get transcription model for specific provider.
    """
    config = get_provider_config(provider)
    return config["transcription_model"]


async def transcribe_audio(
    audio_file_path: str,
    provider: str = "proxyapi",
) -> str:
    """
    Transcribe audio file using specified provider.
    Returns the transcription text.
    """
    from app.config import LLM_PROVIDERS
    
    config = LLM_PROVIDERS[provider]
    api_key = config["api_key"]
    base_url = config["base_url"]
    model = config["transcription_model"]

    # Use httpx directly to avoid multipart issues with OpenAI SDK
    import httpx
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open(audio_file_path, "rb") as audio_file:
            files = {
                "file": ("audio.mp3", audio_file, "audio/mpeg"),
                "model": (None, model),
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
            }
            
            response = await client.post(
                f"{base_url}/audio/transcriptions",
                headers=headers,
                files=files,
            )
            
            if response.status_code != 200:
                raise Exception(f"Transcription failed: {response.status_code} - {response.text}")
            
            result = response.json()
            return result.get("text", "")
