from app.supabase import get_supabase
from app.config import DEFAULT_PROVIDER
from app.services.agent_task_service import create_agent_tasks
from app.services.agents import TranscriptionAgent, EditorAgent, SummarizerAgent


async def process_session_audio(
    session_id: str,
    psychologist_id: str,
) -> None:
    """
    Background task to process session audio:
    1. Transcribe audio → transcript
    2. Edit transcript → edited_transcript
    3. Summarize → summary
    """
    supabase = get_supabase()

    # --- Determine provider from profile ---
    try:
        profile = (
            supabase.table("profiles")
            .select("llm_provider")
            .eq("id", psychologist_id)
            .single()
            .execute()
        )
        provider = (
            profile.data.get("llm_provider", DEFAULT_PROVIDER)
            if profile.data
            else DEFAULT_PROVIDER
        )
    except Exception:
        provider = DEFAULT_PROVIDER

    # --- Create agent task records ---
    create_agent_tasks(session_id)

    # --- Get session info ---
    session_res = (
        supabase.table("sessions")
        .select("*")
        .eq("id", session_id)
        .single()
        .execute()
    )
    session = session_res.data
    if not session or not session.get("audio_url"):
        raise ValueError("Session not found or audio_url is empty")

    audio_url = session["audio_url"]

    # --- Step 1: Transcription ---
    transcription_agent = TranscriptionAgent(session_id, provider)
    transcript = await transcription_agent.process(audio_url)

    supabase.table("sessions").update({
        "transcript": transcript,
    }).eq("id", session_id).execute()

    # --- Step 2: Editing ---
    editor_agent = EditorAgent(session_id, provider)
    edited_transcript = await editor_agent.process(transcript)

    supabase.table("sessions").update({
        "edited_transcript": edited_transcript,
    }).eq("id", session_id).execute()

    # --- Step 3: Summarization ---
    summarizer_agent = SummarizerAgent(session_id, provider)
    summary = await summarizer_agent.process(edited_transcript)

    supabase.table("sessions").update({
        "summary": summary,
    }).eq("id", session_id).execute()
