from app.stt import transcribe_audio
from app.services.agent_task_service import update_agent_status, AGENT_STATUS


class TranscriptionAgent:
    """
    Agent responsible for audio transcription via Whisper.
    """

    def __init__(self, session_id: str, provider: str = "proxyapi"):
        self.session_id = session_id
        self.provider = provider
        self.agent_name = "transcription_agent"

    async def process(self, audio_file_path: str) -> str:
        """
        Transcribe audio file.
        Returns the raw transcript text.
        """
        try:
            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["in_progress"],
            )

            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["waiting_external"],
            )

            transcript = await transcribe_audio(
                audio_file_path,
                self.provider,
            )

            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["completed"],
            )

            return transcript

        except Exception as e:
            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["error"],
                str(e),
            )
