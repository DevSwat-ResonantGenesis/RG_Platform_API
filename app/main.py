"""
RG_Platform_API service — main entry point.

Owns execution of platform-internal utilities and proxies (web search,
fetch URL, wikipedia, time, system info, platform API calls). These used
to live in RG_Chat/app/services/tools/web_tools.py and related files.

Sibling service to RG_Integrations:
  - RG_Integrations  → 3rd-party OAuth (figma, github, google, etc.)
  - RG_Platform_API  → platform utilities, search, proxies

Both expose the same /execute/{tool_id} contract; RG_Chat treats them
identically through the registry's handler_fn mechanism.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import config
from .routers import router
from .skills import SKILLS

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "[%s] startup — version=%s, skills_loaded=%d, enforce_secret=%s",
        config.SERVICE_NAME,
        config.SERVICE_VERSION,
        len(SKILLS),
        config.ENFORCE_INTERNAL_SECRET,
    )
    logger.info("[%s] available skills: %s", config.SERVICE_NAME, sorted(SKILLS.keys()))
    yield
    logger.info("[%s] shutdown", config.SERVICE_NAME)


app = FastAPI(
    title="RG_Platform_API",
    description=(
        "Execution service for platform-internal utilities and proxies "
        "(web fetch, search delegates, wikipedia, time, system info, "
        "platform API calls). Sibling of RG_Integrations."
    ),
    version=config.SERVICE_VERSION,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/")
async def root():
    return {"service": config.SERVICE_NAME, "version": config.SERVICE_VERSION, "status": "ok"}
