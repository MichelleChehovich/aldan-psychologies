from app.supabase import get_supabase

def get_profile(
    psychologist_id: str
):
    supabase = get_supabase()

    return (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", psychologist_id)
        .single()
        .execute()
    )


def update_profile(
    psychologist_id: str,
    data: dict
):
    supabase = get_supabase()

    return (
        supabase
        .table("profiles")
        .update(data)
        .eq("id", psychologist_id)
        .execute()
    )
