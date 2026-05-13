from supabase import create_client
from app.config import SUPABASE_URL, SUPABASE_KEY


def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)
