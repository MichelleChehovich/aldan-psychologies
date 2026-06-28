from openai import OpenAI
from app.config import get_provider_config


def get_transcription_client(provider: str = "proxyapi") -> OpenAI:
    """
    Create OpenAI client for transcription based on provider.
    Создайте клиент OpenAI для транскрипции на основе провайдера.
    """
    config = get_provider_config(provider)
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )


def get_transcription_model(provider: str = "proxyapi") -> str:
    """
    Get transcription model for specific provider.
    Получите модель транскрипции для конкретного провайдера.
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
    Расшифруйте аудиофайл с помощью указанного провайдера.
    Возвращает текст транскрипции.
    """
    client = get_transcription_client(provider)
    model = get_transcription_model(provider)

    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
        )
