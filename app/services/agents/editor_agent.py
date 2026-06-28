from app.llm import chat_completion
from app.services.agent_task_service import update_agent_status, AGENT_STATUS

EDITOR_PROMPT = """Ты — профессиональный редактор психологических транскриптов. 
Отредактируй следующую транскрипцию сессии психолога с клиентом:

1. Раздели текст на реплики психолога и клиента (Психолог: ... Клиент: ...)
2. Убери неразборчивые слова (помеченные как [неразборчиво])
3. Удали повторы, запинки и слова-паразиты
4. Сохрани полный смысл и содержание разговора
5. Исправь очевидные грамматические ошибки

Оригинальная транскрипция:
{transcript}

Отредактированный диалог:"""


class EditorAgent:
    """
    Agent responsible for cleaning and structuring the transcript.
    """

    def __init__(self, session_id: str, provider: str = "proxyapi"):
        self.session_id = session_id
        self.provider = provider
        self.agent_name = "editor_agent"

    async def process(self, transcript: str) -> str:
        """
        Edit and structure the raw transcript.
        Returns the edited transcript text.
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
                    "content": EDITOR_PROMPT.format(transcript=transcript),
                }
            ]

            edited_text = await chat_completion(
                messages=messages,
                provider=self.provider,
                temperature=0.3,
                max_tokens=4000,
            )

            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["completed"],
            )

            return edited_text

        except Exception as e:
            update_agent_status(
                self.session_id,
                self.agent_name,
                AGENT_STATUS["error"],
                str(e),
            )
