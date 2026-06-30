import traceback
from datetime import datetime
from app.supabase import get_supabase
from app.config import DEFAULT_PROVIDER
from app.services.agent_task_service import create_agent_tasks
from app.services.agents import TranscriptionAgent, EditorAgent, SummarizerAgent


def log(msg: str):
    """Write log to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("/app/storage/processing.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(msg)


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
    log(f"=== START process_session_audio ===")
    log(f"Session: {session_id}, Psychologist: {psychologist_id}")
    
    supabase = get_supabase()

    # --- Determine provider from profile ---
    try:
        profile = (
            supabase.table("profiles")
            .select("llm_provider")
            .eq("id", psychologist_id)
            .execute()
        )
        if profile.data and len(profile.data) > 0:
            provider = profile.data[0].get("llm_provider", DEFAULT_PROVIDER)
        else:
            provider = DEFAULT_PROVIDER
        log(f"Using provider: {provider}")
    except Exception as e:
        log(f"Error getting provider: {e}")
        provider = DEFAULT_PROVIDER

    # --- Create agent task records ---
    try:
        create_agent_tasks(session_id)
        log(f"Agent tasks created")
    except Exception as e:
        log(f"Error creating agent tasks: {e}")
        traceback.print_exc()
        return

    # --- Get session info ---
    try:
        session_res = (
            supabase.table("sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        if not session_res.data or len(session_res.data) == 0:
            log(f"Session {session_id} not found")
            return
        
        session = session_res.data[0]
        audio_url = session.get("audio_url")
        
        if not audio_url or audio_url == "string":
            log(f"Invalid audio_url: {audio_url}")
            return
        
        log(f"Audio URL: {audio_url}")
    except Exception as e:
        log(f"Error getting session: {e}")
        traceback.print_exc()
        return

    # --- Step 1: Transcription ---
    transcript = None
    try:
        log(f"Starting transcription...")
        transcription_agent = TranscriptionAgent(session_id, provider)
        transcript = await transcription_agent.process(audio_url)
        log(f"Transcription completed, length: {len(transcript) if transcript else 0}")

        supabase.table("sessions").update({
            "transcript": transcript,
        }).eq("id", session_id).execute()
        log(f"Transcript saved to DB")
    except Exception as e:
        log(f"Transcription failed: {e}")
        traceback.print_exc()
        return

    # --- Step 2: Editing ---
    edited_transcript = None
    try:
        log(f"Starting editing...")
        editor_agent = EditorAgent(session_id, provider)
        edited_transcript = await editor_agent.process(transcript)
        log(f"Editing completed, length: {len(edited_transcript) if edited_transcript else 0}")
        log(f"Edited text preview: {edited_transcript[:200] if edited_transcript else 'EMPTY'}")

        if not edited_transcript:
            log(f"ERROR: edited_transcript is empty!")
            return

        result = supabase.table("sessions").update({
            "edited_transcript": edited_transcript,
        }).eq("id", session_id).execute()
        log(f"Edited transcript saved to DB, result: {result}")
    except Exception as e:
        log(f"Editing failed: {e}")
        traceback.print_exc()
        return

    # --- Step 3: Summarization ---
    try:
        log(f"Starting summarization...")
        summarizer_agent = SummarizerAgent(session_id, provider)
        summary = await summarizer_agent.process(edited_transcript)
        log(f"Summarization completed, length: {len(summary) if summary else 0}")

        supabase.table("sessions").update({
            "summary": summary,
        }).eq("id", session_id).execute()
        log(f"Summary saved to DB")
    except Exception as e:
        log(f"Summarization failed: {e}")
        traceback.print_exc()
        return

    log(f"=== ALL DONE for session {session_id} ===")

  # --- Функция для обработки только текста транскрипта ---

async def process_session_transcript(
    session_id: str,
    psychologist_id: str,
) -> None:
    """
    Background task to process existing transcript:
    1. Edit transcript → edited_transcript
    2. Summarize → summary
    """
    log(f"=== START process_session_transcript ===")
    log(f"Session: {session_id}, Psychologist: {psychologist_id}")
    
    supabase = get_supabase()

    # --- Determine provider from profile ---
    try:
        profile = (
            supabase.table("profiles")
            .select("llm_provider")
            .eq("id", psychologist_id)
            .execute()
        )
        if profile.data and len(profile.data) > 0:
            provider = profile.data[0].get("llm_provider", DEFAULT_PROVIDER)
        else:
            provider = DEFAULT_PROVIDER
        log(f"Using provider: {provider}")
    except Exception as e:
        log(f"Error getting provider: {e}")
        provider = DEFAULT_PROVIDER

    # --- Create agent task records ---
    try:
        create_agent_tasks(session_id)
        log(f"Agent tasks created")
    except Exception as e:
        log(f"Error creating agent tasks: {e}")
        return

    # --- Get session info ---
    try:
        session_res = (
            supabase.table("sessions")
            .select("*")
            .eq("id", session_id)
            .execute()
        )
        if not session_res.data or len(session_res.data) == 0:
            log(f"Session {session_id} not found")
            return
        
        session = session_res.data[0]
        transcript = session.get("transcript")
        
        if not transcript:
            log(f"No transcript found in session")
            return
        
        log(f"Transcript length: {len(transcript)}")
    except Exception as e:
        log(f"Error getting session: {e}")
        return

    # Mark transcription agent as completed (skipped)
    try:
        from app.services.agent_task_service import update_agent_status, AGENT_STATUS
        update_agent_status(session_id, "transcription_agent", AGENT_STATUS["completed"])
        log(f"Transcription agent marked as completed (skipped)")
    except Exception as e:
        log(f"Error updating transcription status: {e}")

    # --- Step 1: Editing ---
    edited_transcript = None
    try:
        log(f"Starting editing...")
        editor_agent = EditorAgent(session_id, provider)
        edited_transcript = await editor_agent.process(transcript)
        log(f"Editing completed, length: {len(edited_transcript) if edited_transcript else 0}")

        if not edited_transcript or len(edited_transcript.strip()) < 10:
            log(f"ERROR: Edited transcript is empty!")
            return

        result = (
            supabase.table("sessions")
            .update({"edited_transcript": edited_transcript})
            .eq("id", session_id)
            .execute()
        )
        log(f"Edited transcript saved to DB")
    except Exception as e:
        log(f"Editing failed: {e}")
        traceback.print_exc()
        return

    # --- Step 2: Summarization ---
    try:
        log(f"Starting summarization...")
        summarizer_agent = SummarizerAgent(session_id, provider)
        summary = await summarizer_agent.process(edited_transcript)
        log(f"Summarization completed, length: {len(summary) if summary else 0}")

        supabase.table("sessions").update({
            "summary": summary,
        }).eq("id", session_id).execute()
        log(f"Summary saved to DB")
    except Exception as e:
        log(f"Summarization failed: {e}")
        traceback.print_exc()
        return

    log(f"=== ALL DONE for session {session_id} ===")

