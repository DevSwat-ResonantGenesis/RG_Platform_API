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
  - media_tools.py: generate_image, generate_audio, generate_music,
                    generate_video, generate_chart, visualize   (6 total)

Add a new utility by:
  1. Implementing a subclass of BaseIntegrationSkill in this directory
  2. Importing and merging it into the SKILLS dict below.
"""

from __future__ import annotations

from typing import Dict

from .base import BaseIntegrationSkill
from .dev_tools import DEV_TOOLS
from .filesystem_tools import FILESYSTEM_TOOLS
from .media_tools import MEDIA_TOOLS
from .web_tools import WEB_TOOLS


SKILLS: Dict[str, BaseIntegrationSkill] = {
    **WEB_TOOLS,
    **MEDIA_TOOLS,
    # 4 dev tools: execute_code, http_request, external_http_request, dev_tool.
    **DEV_TOOLS,
    # 13 filesystem/IDE tools: file_read/write/edit/list/delete, multi_edit,
    # grep_search, find_by_name, run_command, command_status,
    # file_download_curl, file_upload_curl, file_extract_zip.
    **FILESYSTEM_TOOLS,
}


def get_skill(tool_id: str) -> BaseIntegrationSkill | None:
    """Resolve a tool_id to its skill instance, or None if unknown."""
    return SKILLS.get(tool_id)
