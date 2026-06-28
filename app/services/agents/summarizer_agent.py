from app.llm import chat_completion
from app.services.agent_task_service import update_agent_status, AGENT_STATUS

SUMMARIZER_PROMPT = """Проанализируй следующую транскрипцию психологической сессии 
и составь краткое резюме (summary), включающее:

1. Основные темы и запросы, с которыми обратился клиент
2. Ключевые моменты обсуждения
3. Основные выводы и инсайты
4. Достигнутые договорённости и планы
5. Эмоциональное состояние клиента

Отредактированная транскрипция:
{transcript}

Резюме сессии:"""


class SummarizerAgent:
    """
    Agent responsible for creating a summary of the therapy session.
    """

    def __init__(self, session_id: str, provider: str = "proxyapi"):
        self.session_id = session_id
        self.provider = provider
        self.agent_name = "summarizer_agent"

    async def process(self, transcript: str) -> str:
        """
        Create summary from the edited transcript.
        Returns the summary text.
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

            messages = [
                {
                    "role": "user",
                    "content": SUMMARIZER_PROMPT.format(transcript=transcript),
                }
            ]

            summary = await chat_completion(
                messages=messages,
                provider=self.provider,
                temperature=0.5,
                max_tokens=2000,
            )

            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["completed"],
            )

            return summary

        except Exception as e:
            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["error"],
                str(e),
            )
