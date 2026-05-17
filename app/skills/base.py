"""
Base Platform-API Skill (RG_Platform_API service edition)
==========================================================

Mirrors the shape of RG_Integrations/app/skills/base.py so the two
services stay structurally identical. The only difference is that
platform-API skills generally do NOT need user-owned credentials
(they call our own services and platform-owned APIs).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseIntegrationSkill(ABC):
    """Base class for all platform-API and utility skills."""

    skill_id: str = ""
    skill_name: str = ""
    api_key_names: List[str] = []  # Usually empty for platform-API skills.

    def get_credentials(self, context: Dict[str, Any]) -> Optional[str]:
        """Most platform-API skills don't need user creds. Provided for
        parity with RG_Integrations skills that may be moved here."""
        user_keys = context.get("user_api_keys") or {}
        for key_name in self.api_key_names:
            val = user_keys.get(key_name)
            if val:
                return val
        return None

    @abstractmethod
    async def execute(
        self, message: str, user_id: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute the skill action. Must be implemented by each skill."""
        ...

    def _no_credentials_error(self) -> Dict[str, Any]:
        return {
            "success": False,
            "action": self.skill_id,
            "error": f"**{self.skill_name}** is not connected.",
        }
