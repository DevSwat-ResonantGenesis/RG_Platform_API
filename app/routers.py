"""HTTP API for RG_Platform_API."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from .config import config
from .skills import SKILLS, get_skill

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / response models ───────────────────────────────────────


class ExecuteRequest(BaseModel):
    """Body for POST /execute/{tool_id}.

    `context` matches the shape RG_Chat's ToolExecutor builds.
    Platform-API skills typically ignore `user_api_keys` (they use
    platform-owned credentials), but the field is accepted for parity
    with the rg_integrations contract.
    """

    message: str
    user_id: str
    context: Dict[str, Any] = {}


class SkillListResponse(BaseModel):
    skills: List[str]
    count: int


# ── Endpoints ───────────────────────────────────────────────────────


def _check_internal_secret(x_internal_secret: Optional[str]) -> None:
    """Reject calls that don't carry the expected internal s2s secret.

    Only enforced when ENFORCE_INTERNAL_SECRET=true (production).
    """
    if not config.ENFORCE_INTERNAL_SECRET:
        return
    expected = config.INTERNAL_SECRET
    if not expected:
        raise HTTPException(status_code=503, detail="Service misconfigured: INTERNAL_SECRET missing")
    if x_internal_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid internal secret")


@router.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "service": config.SERVICE_NAME,
        "version": config.SERVICE_VERSION,
        "status": "ok",
        "skills_loaded": list(SKILLS.keys()),
        "skill_count": len(SKILLS),
    }


@router.get("/skills", response_model=SkillListResponse)
async def list_skills() -> SkillListResponse:
    names = sorted(SKILLS.keys())
    return SkillListResponse(skills=names, count=len(names))


@router.post("/execute/{tool_id}")
async def execute_tool(
    tool_id: str,
    body: ExecuteRequest,
    x_internal_secret: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Execute the named skill and return its result dict."""
    _check_internal_secret(x_internal_secret)

    skill = get_skill(tool_id)
    if skill is None:
        raise HTTPException(
            status_code=404,
            detail=f"No skill registered for tool_id={tool_id!r}. "
                   f"Loaded: {sorted(SKILLS.keys())}",
        )

    user_id = body.user_id or x_user_id or ""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    try:
        result = await skill.execute(body.message, user_id, body.context or {})
        if not isinstance(result, dict):
            result = {"success": True, "data": result}
        result.setdefault("tool_id", tool_id)
        return result
    except Exception as e:
        logger.exception(f"Skill {tool_id} failed for user {user_id}: {e}")
        return {
            "success": False,
            "tool_id": tool_id,
            "error": f"{type(e).__name__}: {str(e)[:300]}",
        }
