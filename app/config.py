#import os

#SUPABASE_URL = os.getenv("SUPABASE_URL")  
#SUPABASE_KEY = os.getenv("SUPABASE_KEY")  

import os


def get_supabase_url():
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise RuntimeError("SUPABASE_URL is missing")
    return url


def get_supabase_key():
    key = os.getenv("SUPABASE_KEY")
    if not key:
        raise RuntimeError("SUPABASE_KEY is missing")
    return key
