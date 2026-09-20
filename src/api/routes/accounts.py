"""
Accounts API routes — Connect and manage Instagram Business accounts.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.instagram.auth_flow import InstagramAuthFlow
from src.core.logging_config import get_logger, log_error

logger = get_logger("api.routes.accounts")

router = APIRouter()
_auth_flow = InstagramAuthFlow()


# ========== Request / Response Models ==========

class ConnectRequest(BaseModel):
    redirect_uri: str = "http://localhost:8000/api/accounts/callback"


class CallbackRequest(BaseModel):
    code: str
    redirect_uri: str = "http://localhost:8000/api/accounts/callback"


class RefreshTokenRequest(BaseModel):
    access_token: str


# ========== Routes ==========

@router.post("/connect-url")
async def get_connect_url(request: ConnectRequest):
    """
    Generate the Instagram Business Login URL.
    
    The user should be redirected to this URL to authorize the app.
    After authorization, Instagram redirects back with an auth code.
    """
    try:
        url = _auth_flow.get_authorization_url(redirect_uri=request.redirect_uri)
        logger.info("Generated Instagram connect URL")
        return {"authorization_url": url}
    except Exception as e:
        log_error("api.accounts", "get_connect_url", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback")
async def handle_callback(request: CallbackRequest):
    """
    Handle the OAuth callback — exchange the auth code for tokens.
    
    1. Exchanges code for short-lived token
    2. Exchanges short-lived for long-lived token (60 days)
    3. Fetches the Instagram user profile
    """
    try:
        # Step 1: Exchange code for short-lived token
        short_token = await _auth_flow.exchange_code(
            code=request.code,
            redirect_uri=request.redirect_uri,
        )
        logger.info("Exchanged code for short-lived token")

        # Step 2: Exchange for long-lived token
        long_token = await _auth_flow.exchange_for_long_lived_token(
            short_lived_token=short_token,
        )
        logger.info("Got long-lived token (60 days)")

        # Step 3: Get profile info
        profile = await _auth_flow.get_profile(access_token=long_token["access_token"])
        logger.info("Fetched Instagram profile: %s", profile.get("username", "unknown"))

        return {
            "message": "Instagram account connected successfully",
            "access_token": long_token["access_token"],
            "token_type": long_token.get("token_type", "bearer"),
            "expires_in": long_token.get("expires_in"),
            "profile": profile,
        }
    except Exception as e:
        log_error("api.accounts", "handle_callback", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-token")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh a long-lived token for another 60 days."""
    try:
        result = await _auth_flow.refresh_long_lived_token(
            long_lived_token=request.access_token,
        )
        logger.info("Token refreshed successfully")
        return {
            "message": "Token refreshed",
            "access_token": result["access_token"],
            "expires_in": result.get("expires_in"),
        }
    except Exception as e:
        log_error("api.accounts", "refresh_token", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verify/{access_token}")
async def verify_account(access_token: str):
    """Verify that an access token is valid by fetching the profile."""
    try:
        profile = await _auth_flow.get_profile(access_token=access_token)
        return {
            "valid": True,
            "profile": profile,
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
        }
