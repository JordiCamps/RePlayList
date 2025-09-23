"""Authentication endpoints for the RePlayList API."""

import logging
import time
from typing import Dict

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from replaylist.auth import auth_manager
from .models import AuthResponse, TokenExchangeRequest
from .state import user_tokens

logger = logging.getLogger(__name__)

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])


def get_user_id() -> str:
    """Get current user ID (simplified for demo)."""
    return "default_user"


@router.post("/{platform}/login", response_model=AuthResponse)
async def start_auth(platform: str, request: Request):
    """
    Start OAuth authentication for a platform.
    
    Args:
        platform: Platform name (spotify or youtube)
        
    Returns:
        Authentication URL
    """
    try:
        if platform.lower() not in ['spotify', 'youtube']:
            raise HTTPException(status_code=400, detail="Unsupported platform")
        
        # Start callback server on the correct port for this platform
        if platform.lower() == 'spotify':
            auth_manager.start_callback_server(8888)
        else:
            auth_manager.start_callback_server(8889)
        
        # Generate auth URL
        import uuid
        state = str(uuid.uuid4())
        
        if platform.lower() == 'spotify':
            auth_url = auth_manager.spotify_auth.get_auth_url(state)
        else:
            auth_url = auth_manager.youtube_auth.get_auth_url(state)
        
        # Store the state for later retrieval
        auth_manager._pending_auth[state] = {
            'platform': platform.lower(),
            'timestamp': time.time()
        }
        
        # In desktop (Tauri) we can't receive postMessage from external browser.
        # Return the generated state so the client can poll /auth/{platform}/status?state=...
        return AuthResponse(success=True, auth_url=auth_url, state=state)
        
    except Exception as e:
        logger.error(f"Authentication start failed: {e}")
        return AuthResponse(success=False, error=str(e))


@router.get("/{platform}/callback")
async def handle_auth_callback_redirect(platform: str, code: str = None, error: str = None):
    """
    Handle OAuth callback redirect and return HTML that auto-closes and notifies parent.
    """
    logger.info(f"OAuth callback received for {platform}: code={code}, error={error}")
    
    if error:
        # Return HTML that sends error message to parent and closes
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Error</title></head>
        <body>
            <script>
                console.log('Sending AUTH_ERROR message for platform: {platform}');
                if (window.opener) {{
                    window.opener.postMessage({{
                        type: 'AUTH_ERROR',
                        platform: '{platform}',
                        error: '{error}'
                    }}, 'http://localhost:3004');
                }} else {{
                    console.log('No window.opener found');
                }}
                setTimeout(() => {{
                    window.close();
                }}, 100);
            </script>
            <p>Authentication failed. This window will close automatically.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    if code:
        # Exchange code for tokens
        try:
            result = auth_manager.exchange_code(platform, code)
            
            if result.success:
                # Store tokens for user
                user_id = get_user_id()
                if user_id not in user_tokens:
                    user_tokens[user_id] = {}
                
                user_tokens[user_id][platform.lower()] = result.access_token
                logger.info(f"Successfully stored token for {platform}, user_id: {user_id}")
                
                # Return HTML that sends success message to parent and closes
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Authentication Successful</title></head>
                <body>
                    <script>
                        console.log('Sending AUTH_SUCCESS message for platform: {platform}');
                        if (window.opener) {{
                            window.opener.postMessage({{
                                type: 'AUTH_SUCCESS',
                                platform: '{platform}'
                            }}, 'http://localhost:3004');
                        }} else {{
                            console.log('No window.opener found');
                        }}
                        setTimeout(() => {{
                            window.close();
                        }}, 100);
                    </script>
                    <p>Authentication successful! This window will close automatically.</p>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content)
            else:
                # Return HTML that sends error message to parent and closes
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Authentication Error</title></head>
                <body>
                    <script>
                        if (window.opener) {{
                            window.opener.postMessage({{
                                type: 'AUTH_ERROR',
                                platform: '{platform}',
                                error: '{result.error}'
                            }}, window.location.origin);
                        }}
                        window.close();
                    </script>
                    <p>Authentication failed. This window will close automatically.</p>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content)
                
        except Exception as e:
            logger.error(f"Token exchange failed: {e}")
            # Return HTML that sends error message to parent and closes
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Authentication Error</title></head>
            <body>
                <script>
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'AUTH_ERROR',
                            platform: '{platform}',
                            error: '{str(e)}'
                        }}, window.location.origin);
                    }}
                    window.close();
                </script>
                <p>Authentication failed. This window will close automatically.</p>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
    
    # No code or error, return HTML that sends error message to parent and closes
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Authentication Error</title></head>
    <body>
        <script>
            if (window.opener) {{
                window.opener.postMessage({{
                    type: 'AUTH_ERROR',
                    platform: '{platform}',
                    error: 'no_code'
                }}, window.location.origin);
            }}
            window.close();
        </script>
        <p>Authentication failed. This window will close automatically.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/{platform}/status", response_model=AuthResponse)
async def check_auth_status(platform: str, state: str):
    """
    Check authentication status for a given state.
    
    Args:
        platform: Platform name
        state: OAuth state parameter
        
    Returns:
        Authentication result
    """
    try:
        if state not in auth_manager._auth_results:
            return AuthResponse(success=False, error="Authentication not found or expired")
        
        result = auth_manager._auth_results.pop(state)
        
        if result.success:
            # Store tokens for user
            user_id = get_user_id()
            if user_id not in user_tokens:
                user_tokens[user_id] = {}
            
            user_tokens[user_id][platform.lower()] = result.access_token
            
            # Clean up pending auth
            if state in auth_manager._pending_auth:
                del auth_manager._pending_auth[state]
            
            return AuthResponse(success=True)
        else:
            return AuthResponse(success=False, error=result.error)
            
    except Exception as e:
        logger.error(f"Auth status check failed: {e}")
        return AuthResponse(success=False, error=str(e))


@router.post("/store-token")
async def store_token(request: dict):
    """
    Store authentication token for a platform.
    
    Args:
        request: Token data including platform, access_token, etc.
        
    Returns:
        Success status
    """
    try:
        platform = request.get('platform')
        access_token = request.get('access_token')
        
        if not platform or not access_token:
            return {"success": False, "error": "Missing platform or access_token"}
        
        # Store tokens for user
        user_id = get_user_id()
        if user_id not in user_tokens:
            user_tokens[user_id] = {}
        
        user_tokens[user_id][platform.lower()] = access_token
        
        logger.info(f"Token stored for {platform}, user_id: {user_id}")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"Token storage failed: {e}")
        return {"success": False, "error": str(e)}


@router.post("/{platform}/callback", response_model=AuthResponse)
async def handle_auth_callback(platform: str, request: TokenExchangeRequest):
    """
    Handle OAuth callback and exchange code for tokens.
    
    Args:
        platform: Platform name
        request: Token exchange request
        
    Returns:
        Authentication result
    """
    try:
        result = auth_manager.exchange_code(platform, request.code)
        
        if result.success:
            # Store tokens for user
            user_id = get_user_id()
            if user_id not in user_tokens:
                user_tokens[user_id] = {}
            
            user_tokens[user_id][platform.lower()] = result.access_token
            
            return AuthResponse(success=True)
        else:
            return AuthResponse(success=False, error=result.error)
            
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return AuthResponse(success=False, error=str(e))
