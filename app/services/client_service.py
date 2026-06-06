from datetime import datetime

from app.supabase import get_supabase


# =====================================================
# CREATE CLIENT
# =====================================================

def create_client(
    psychologist_id: str,
    data: dict
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .insert({
            "psychologist_id": psychologist_id,
            **data
        })
        .execute()
    )


# =====================================================
# GET ACTIVE CLIENTS
# =====================================================

def get_clients(
    psychologist_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .select("*")
        .eq("psychologist_id", psychologist_id)
        .eq("is_archived", False)
        .order("created_at", desc=True)
        .execute()
    )


# =====================================================
# GET ARCHIVE
# =====================================================

def get_archived_clients(
    psychologist_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .select("*")
        .eq("psychologist_id", psychologist_id)
        .eq("is_archived", True)
        .order("archived_at", desc=True)
        .execute()
    )


# =====================================================
# GET CLIENT
# =====================================================

def get_client_by_id(
    psychologist_id: str,
    client_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .select("*")
        .eq("id", client_id)
        .eq("psychologist_id", psychologist_id)
        .single()
        .execute()
    )


# =====================================================
# UPDATE CLIENT
# =====================================================

def update_client(
    psychologist_id: str,
    client_id: str,
    data: dict
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .update(data)
        .eq("id", client_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )


# =====================================================
# ARCHIVE CLIENT
# =====================================================

def archive_client(
    psychologist_id: str,
    client_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .update({
            "is_archived": True,
            "archived_at": datetime.utcnow().isoformat()
        })
        .eq("id", client_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )


# =====================================================
# RESTORE CLIENT
# =====================================================

def restore_client(
    psychologist_id: str,
    client_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("clients")
        .update({
            "is_archived": False,
            "archived_at": None
        })
        .eq("id", client_id)
        .eq("psychologist_id", psychologist_id)
        .execute()
    )
