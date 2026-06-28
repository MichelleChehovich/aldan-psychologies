from fastapi import APIRouter, Depends, HTTPException

from app.config import LLM_PROVIDERS, PROVIDER_DESCRIPTIONS
from app.supabase import get_supabase
from app.deps import get_current_user

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("")
async def list_providers():
    """
    Return list of all available LLM providers configured on the server.
    No DB access needed — just server configuration.
    """
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
    }


@router.patch("/select")
async def select_provider(
    provider: str,
    psychologist_id: str = Depends(get_current_user),
):
    """
    Save user's preferred LLM provider to their profile.
    """
    if provider not in LLM_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {provider}")

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
