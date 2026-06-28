from datetime import datetime
from app.supabase import get_supabase

# Agent status constants
AGENT_STATUS = {
    "not_started": "not_started",
    "in_progress": "in_progress",
    "waiting_external": "waiting_external",
    "completed": "completed",
    "error": "error",
}

AGENT_NAMES = [
    "transcription_agent",
    "editor_agent",
    "summarizer_agent",
]


def create_agent_tasks(session_id: str) -> None:
    """
    Create initial agent tasks for a session (all set to 'not_started').
    Safe to call multiple times — does nothing if tasks already exist.
    """
    supabase = get_supabase()
    now = datetime.utcnow().isoformat()

    for agent_name in AGENT_NAMES:
        # Check if task already exists
        existing = (
            supabase.table("agent_tasks")
            .select("id")
            .eq("session_id", session_id)
            .eq("agent_name", agent_name)
            .execute()
        )
        if existing.data:
            continue

        supabase.table("agent_tasks").insert({
            "session_id": session_id,
            "agent_name": agent_name,
            "status": AGENT_STATUS["not_started"],
            "created_at": now,
            "updated_at": now,
        }).execute()


def update_agent_status(
    session_id: str,
    agent_name: str,
    status: str,
    error_message: str = None,
) -> None:
    """
    Update status of a specific agent task.
    """
    supabase = get_supabase()

    update_data = {
        "status": status,
        "updated_at": datetime.utcnow().isoformat(),
    }
    if error_message:
        update_data["error_message"] = error_message

    supabase.table("agent_tasks").update(update_data) \
        .eq("session_id", session_id) \
        .eq("agent_name", agent_name) \
        .execute()


def get_agent_statuses(session_id: str):
    """
    Get all agent statuses for a session.
    Returns Supabase response object — use .data to access list.
    """
    supabase = get_supabase()
    return supabase.table("agent_tasks") \
        .select("*") \
        .eq("session_id", session_id) \
        .order("created_at") \
        .execute()
