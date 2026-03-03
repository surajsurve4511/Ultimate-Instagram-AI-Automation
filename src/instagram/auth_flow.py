"""
Instagram OAuth2 Auth Flow — Connects Instagram Business accounts via Meta OAuth.

Implements the server-side OAuth2 flow for:
1. Business Login for Instagram (or Facebook Login for Business)
2. Token exchange
3. Token storage (encrypted)
4. Token refresh

Docs: https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/business-login
"""

import logging
from typing import Optional
from urllib.parse import urlencode

import httpx

from src.config.settings import SETTINGS
from src.auth.auth_service import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)

# Meta OAuth endpoints
AUTHORIZE_URL = "https://www.instagram.com/oauth/authorize"
TOKEN_URL = "https://api.instagram.com/oauth/access_token"
LONG_LIVED_TOKEN_URL = "https://graph.instagram.com/access_token"
REFRESH_TOKEN_URL = "https://graph.instagram.com/refresh_access_token"
GRAPH_URL = "https://graph.instagram.com"


class InstagramAuthFlow:
    """
    Handles Instagram Business Login OAuth2 flow.
    
    Flow:
    1. Generate auth URL → redirect user to Instagram
    2. User authorizes → Instagram redirects back with code
    3. Exchange code for short-lived token
    4. Exchange short-lived for long-lived token (60 days)
    5. Store encrypted token in database
    6. Refresh token before expiry
    """

    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        redirect_uri: str = "http://localhost:8000/auth/instagram/callback",
    ):
        self._app_id = app_id or SETTINGS.META_APP_ID
        self._app_secret = app_secret or SETTINGS.META_APP_SECRET
        self._redirect_uri = redirect_uri

        if not self._app_id or not self._app_secret:
            logger.warning(
                "META_APP_ID or META_APP_SECRET not set. "
                "Instagram auth will not work. "
                "Create a Meta App at https://developers.facebook.com/apps/"
            )

    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate the Instagram authorization URL.
        Redirect the user to this URL to start the OAuth flow.
        
        Args:
            state: Optional CSRF state parameter
            
        Returns:
            Authorization URL string
        """
        params = {
            "client_id": self._app_id,
            "redirect_uri": self._redirect_uri,
            "response_type": "code",
            "scope": "instagram_business_basic,instagram_business_content_publish",
        }
        if state:
            params["state"] = state

        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict:
        """
        Exchange authorization code for a short-lived access token.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dict with 'access_token', 'user_id'
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TOKEN_URL,
                data={
                    "client_id": self._app_id,
                    "client_secret": self._app_secret,
                    "grant_type": "authorization_code",
                    "redirect_uri": self._redirect_uri,
                    "code": code,
                },
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"Token exchanged for user: {data.get('user_id')}")
            return data

    async def get_long_lived_token(self, short_lived_token: str) -> dict:
        """
        Exchange a short-lived token for a long-lived token (valid ~60 days).
        
        Args:
            short_lived_token: Short-lived access token
            
        Returns:
            Dict with 'access_token', 'token_type', 'expires_in'
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                LONG_LIVED_TOKEN_URL,
                params={
                    "grant_type": "ig_exchange_token",
                    "client_secret": self._app_secret,
                    "access_token": short_lived_token,
                },
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"Long-lived token obtained, expires in {data.get('expires_in')}s")
            return data

    async def refresh_token(self, long_lived_token: str) -> dict:
        """
        Refresh a valid, non-expired long-lived token.
        Tokens can be refreshed as long as they are at least 24 hours old
        and not expired. Refreshed tokens are valid for 60 days.
        
        Args:
            long_lived_token: Current long-lived access token
            
        Returns:
            Dict with new 'access_token', 'token_type', 'expires_in'
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                REFRESH_TOKEN_URL,
                params={
                    "grant_type": "ig_refresh_token",
                    "access_token": long_lived_token,
                },
            )
            response.raise_for_status()
            data = response.json()

            logger.info("Token refreshed successfully")
            return data

    async def get_user_profile(self, access_token: str) -> dict:
        """
        Get the Instagram user's profile info.
        
        Args:
            access_token: Valid access token
            
        Returns:
            Dict with user profile data (id, username, name, etc.)
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GRAPH_URL}/me",
                params={
                    "fields": "id,username,name,account_type,media_count,followers_count",
                    "access_token": access_token,
                },
            )
            response.raise_for_status()
            return response.json()

    async def full_auth_flow(self, code: str) -> dict:
        """
        Complete the full auth flow from code to long-lived token + profile.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Dict with 'access_token' (long-lived), 'user_id', 'profile',
            'encrypted_token', 'expires_in'
        """
        # Step 1: Exchange code for short-lived token
        token_data = await self.exchange_code(code)
        short_token = token_data["access_token"]
        user_id = str(token_data["user_id"])

        # Step 2: Get long-lived token
        long_token_data = await self.get_long_lived_token(short_token)
        long_token = long_token_data["access_token"]
        expires_in = long_token_data.get("expires_in", 5184000)  # ~60 days

        # Step 3: Get profile
        profile = await self.get_user_profile(long_token)

        # Step 4: Encrypt the token for storage
        encrypted = encrypt_token(long_token)

        return {
            "access_token": long_token,
            "encrypted_token": encrypted,
            "user_id": user_id,
            "profile": profile,
            "expires_in": expires_in,
        }
