import traceback
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
    print(f"[process_session_audio] Starting for session {session_id}, psychologist {psychologist_id}")
    
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
        print(f"[process_session_audio] Using provider: {provider}")
    except Exception as e:
        print(f"[process_session_audio] Error getting provider: {e}")
        provider = DEFAULT_PROVIDER

    # --- Create agent task records ---
    try:
        create_agent_tasks(session_id)
        print(f"[process_session_audio] Agent tasks created")
    except Exception as e:
        print(f"[process_session_audio] Error creating agent tasks: {e}")
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
            print(f"[process_session_audio] Session {session_id} not found")
            return
        
        session = session_res.data[0]
        audio_url = session.get("audio_url")
        
        if not audio_url or audio_url == "string":
            print(f"[process_session_audio] Invalid audio_url: {audio_url}")
            return
        
        print(f"[process_session_audio] Audio URL: {audio_url}")
    except Exception as e:
        print(f"[process_session_audio] Error getting session: {e}")
        traceback.print_exc()
        return

    # --- Step 1: Transcription ---
    try:
        print(f"[process_session_audio] Starting transcription...")
        transcription_agent = TranscriptionAgent(session_id, provider)
        transcript = await transcription_agent.process(audio_url)
        print(f"[process_session_audio] Transcription completed, length: {len(transcript)}")

        supabase.table("sessions").update({
            "transcript": transcript,
        }).eq("id", session_id).execute()
        print(f"[process_session_audio] Transcript saved to DB")
    except Exception as e:
        print(f"[process_session_audio] Transcription failed: {e}")
        traceback.print_exc()
        return

    # --- Step 2: Editing ---
    try:
        print(f"[process_session_audio] Starting editing...")
        editor_agent = EditorAgent(session_id, provider)
        edited_transcript = await editor_agent.process(transcript)
        print(f"[process_session_audio] Editing completed, length: {len(edited_transcript)}")

        supabase.table("sessions").update({
            "edited_transcript": edited_transcript,
        }).eq("id", session_id).execute()
        print(f"[process_session_audio] Edited transcript saved to DB")
    except Exception as e:
        print(f"[process_session_audio] Editing failed: {e}")
        traceback.print_exc()
        return

    # --- Step 3: Summarization ---
    try:
        print(f"[process_session_audio] Starting summarization...")
        summarizer_agent = SummarizerAgent(session_id, provider)
        summary = await summarizer_agent.process(edited_transcript)
        print(f"[process_session_audio] Summarization completed, length: {len(summary)}")

        supabase.table("sessions").update({
            "summary": summary,
        }).eq("id", session_id).execute()
        print(f"[process_session_audio] Summary saved to DB")
    except Exception as e:
        print(f"[process_session_audio] Summarization failed: {e}")
        traceback.print_exc()
        return

    print(f"[process_session_audio] ALL DONE for session {session_id}")
