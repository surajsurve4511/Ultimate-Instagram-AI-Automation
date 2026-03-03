"""
Instagram account management API routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.instagram.auth_flow import InstagramAuthFlow

router = APIRouter()
_auth_flow = None


def _get_auth_flow() -> InstagramAuthFlow:
    global _auth_flow
    if _auth_flow is None:
        _auth_flow = InstagramAuthFlow()
    return _auth_flow


class ConnectRequest(BaseModel):
    redirect_uri: str = "http://localhost:8000/auth/instagram/callback"


class CallbackRequest(BaseModel):
    code: str


@router.get("/connect-url")
async def get_connect_url():
    """Get the Instagram OAuth authorization URL."""
    auth_flow = _get_auth_flow()
    url = auth_flow.get_authorization_url()
    return {"authorization_url": url}


@router.post("/callback")
async def handle_callback(request: CallbackRequest):
    """Handle Instagram OAuth callback with authorization code."""
    auth_flow = _get_auth_flow()
    try:
        result = await auth_flow.full_auth_flow(request.code)
        return {
            "ig_user_id": result["user_id"],
            "profile": result["profile"],
            "message": "Instagram account connected successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
