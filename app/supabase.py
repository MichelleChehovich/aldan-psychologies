#from supabase import create_client
#from app.config import SUPABASE_URL, SUPABASE_KEY

#supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#def get_supabase():
#    return supabase

import os
from supabase import create_client

_supabase_client = None


def get_supabase():
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing")

    _supabase_client = create_client(url, key)

    return _supabase_client
