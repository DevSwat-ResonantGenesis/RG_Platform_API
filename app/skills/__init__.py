"""
Skill registry for RG_Platform_API.

This service hosts the execution code for *platform-internal* utilities
and proxies that previously lived in RG_Chat. Distinct from RG_Integrations
(which hosts 3rd-party OAuth integrations).

Migrated skills:
  - web_tools.py: fetch_url, read_webpage, read_many_pages, reddit_search,
                  image_search, news_search, places_search, youtube_search,
                  deep_research, wikipedia, weather, stock_crypto,
                  stock_market_data, scrape_page, scrape_platforms,
                  get_current_time, get_system_info, platform_api_search,
                  platform_api_call   (19 total)

Add a new utility by:
  1. Implementing a subclass of BaseIntegrationSkill in this directory
  2. Importing and merging it into the SKILLS dict below.
"""

from __future__ import annotations

from typing import Dict

from .base import BaseIntegrationSkill
from .web_tools import WEB_TOOLS


SKILLS: Dict[str, BaseIntegrationSkill] = {
    **WEB_TOOLS,
    # Future:
    # **MEDIA_TOOLS,
    # **DEV_TOOLS,
    # **FILESYSTEM_TOOLS,
    # (see RG_Chat/app/services/tools/ for the remaining files; their
    # migration follows the same pattern as web_tools.)
}


def get_skill(tool_id: str) -> BaseIntegrationSkill | None:
    """Resolve a tool_id to its skill instance, or None if unknown."""
    return SKILLS.get(tool_id)
