import hashlib
import hmac
import json

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.models import PushEvent

router = APIRouter()


def verify_signature(raw_body: bytes, signature_header: str) -> bool:
    """Guard 1: Is this request actually from GitHub?"""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode(),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


async def is_duplicate(delivery_id: str, db: AsyncSession) -> bool:
    """Dedup check: have we already processed this delivery?"""
    result = await db.execute(
        select(PushEvent).where(PushEvent.delivery_id == delivery_id)
    )
    return result.scalar_one_or_none() is not None


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(default=None),
    x_github_event: str = Header(default=None),
    x_github_delivery: str = Header(default=None),
):
    # Read raw body first — signature check needs the exact bytes
    raw_body = await request.body()

    # Guard 1: signature
    if not verify_signature(raw_body, x_hub_signature_256):
        return {"status": "ignored", "reason": "invalid signature"}

    # Guard 2: event type
    if x_github_event != "push":
        return {"status": "ignored", "reason": "not a push event"}

    payload = json.loads(raw_body)

    # Guard 3: deletion check (deleted branches fire push events too)
    if payload.get("deleted", False):
        return {"status": "ignored", "reason": "branch deletion"}

    # Guard 4: ref filter — only main branch (or tags for milestone detection)
    ref = payload.get("ref", "")
    if ref != "refs/heads/main" and not ref.startswith("refs/tags/"):
        return {"status": "ignored", "reason": "not main branch"}

    # --- All guards passed. Store immediately (cold-start safety). ---

    # TODO: inject db session (wiring this up in next step)
    # For now just return what we parsed — confirms the logic works
    return {
        "status": "accepted",
        "repo": payload.get("repository", {}).get("full_name"),
        "ref": ref,
        "pusher": payload.get("pusher", {}).get("name"),
        "before": payload.get("before"),
        "after": payload.get("after"),
        "delivery_id": x_github_delivery,
    }