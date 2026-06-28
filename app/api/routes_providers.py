from fastapi import APIRouter, Depends, HTTPException

from app.config import LLM_PROVIDERS, PROVIDER_DESCRIPTIONS, DEFAULT_PROVIDER
from app.supabase import get_supabase
from app.deps import get_current_user

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("")
async def list_providers(psychologist_id: str = Depends(get_current_user)):
    """
    Return list of available LLM providers and the current user selection.
    """
    supabase = get_supabase()

    # Current user's provider
    profile = (
        supabase.table("profiles")
        .select("llm_provider")
        .eq("id", psychologist_id)
        .single()
        .execute()
    )
    current = (
        profile.data.get("llm_provider", DEFAULT_PROVIDER)
        if profile.data
        else DEFAULT_PROVIDER
    )

    # Build available providers list (only those with API key set)
    available = []
    for code, config in LLM_PROVIDERS.items():
        if config.get("api_key"):
            available.append({
                "code": code,
                "name": config["name"],
                "description": PROVIDER_DESCRIPTIONS.get(code, ""),
            })

    return {
        "providers": available,
        "current": current,
    }


@router.patch("/select")
async def select_provider(
    provider: str,
    psychologist_id: str = Depends(get_current_user),
):
    """
    Set user's preferred LLM provider.
    """
    if provider not in LLM_PROVIDERS:
        raise HTTPException(status_code=400, detail="Unknown provider")

    if not LLM_PROVIDERS[provider].get("api_key"):
        raise HTTPException(
            status_code=400,
            detail=f"Provider '{provider}' is not configured (API key missing)",
        )

    supabase = get_supabase()
    supabase.table("profiles").update({
        "llm_provider": provider,
    }).eq("id", psychologist_id).execute()

    return {"status": "ok", "provider": provider}
