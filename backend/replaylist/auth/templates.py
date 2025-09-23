"""HTML templates for OAuth callback responses.

These helpers return small HTML pages that communicate success or error back to
the opener window (or Tauri webview) and then self-close.

Browser/Tauri integration:
- The pages attempt to `postMessage` to the opener (for browser) and then call
  a Tauri command to close embedded windows if available.
"""

from typing import Optional


def render_success_html(platform: str) -> str:
    """Render success page content for the given platform."""
    return f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>Authentication Successful</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 16px;
            }}
            .card {{
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 12px;
                padding: 24px;
                max-width: 560px;
                width: 100%;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
            }}
            .icon {{
                width: 64px; height: 64px;
                border-radius: 50%;
                background: #10b98133;
                color: #10b981;
                display: inline-flex; align-items: center; justify-content: center;
                margin-bottom: 16px;
                font-size: 36px;
            }}
            h1 {{ font-size: 22px; margin: 0 0 8px; }}
            p {{ margin: 0 0 16px; color: #94a3b8; }}
            .badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 9999px;
                background: #1f2937;
                color: #e5e7eb;
                font-size: 12px;
                margin-bottom: 8px;
            }}
            .dim {{ font-size: 12px; color: #94a3b8; margin-top: 6px; }}
        </style>
    </head>
    <body>
        <div class=\"card\">
            <div class=\"icon\">✓</div>
            <div class=\"badge\">{platform.title()} Connected</div>
            <h1>Authentication Successful</h1>
            <p>You can return to RePlayList. This window can be closed.</p>
            <div class=\"dim\">You can now return to RePlayList.</div>
        </div>
        <script>
            try {{
                if (window.opener) {{
                    window.opener.postMessage({{ type: 'AUTH_SUCCESS', platform: '{platform}' }}, '*');
                }}
                const __TAURI__ = (window.__TAURI__ || (window.window && window.window.__TAURI__));
                if (__TAURI__ && (__TAURI__.core?.invoke || __TAURI__.invoke)) {{
                    const inv = (__TAURI__.core && __TAURI__.core.invoke) ? __TAURI__.core.invoke : __TAURI__.invoke;
                    inv('close_last_auth_window').catch(() => {{}});
                }}
            }} catch (e) {{}}
        </script>
    </body>
    </html>
    """


def render_error_html(platform: str, error: Optional[str]) -> str:
    """Render error page content with a human-readable message."""
    safe_error = error or "Unknown error"
    return f"""
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
                    error: '{safe_error}'
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


def render_cli_success_html() -> bytes:
    """Render minimal success page for CLI-driven flows."""
    return (
        b"""\
        <!DOCTYPE html>
        <html>
        <head><title>Authentication Successful</title></head>
        <body>
            <script>
                // Notify opener if present and then close this window (Tauri webview aware)
                try {
                    if (window.opener) {
                        window.opener.postMessage({ type: 'AUTH_SUCCESS' }, '*');
                    }
                    // Try Tauri invoke if available to close the auth window
                    const anyWin = window;
                    const __TAURI__ = anyWin.__TAURI__ || (anyWin.window && anyWin.window.__TAURI__);
                    if (__TAURI__ && (__TAURI__.core?.invoke || __TAURI__.invoke)) {
                        const inv = (__TAURI__.core && __TAURI__.core.invoke) ? __TAURI__.core.invoke : __TAURI__.invoke;
                        inv('close_last_auth_window').catch(() => {});
                    }
                } catch (e) {}
                setTimeout(() => { window.close(); }, 100);
            </script>
            <p>Authentication successful. This window will close automatically.</p>
        </body>
        </html>
    """
    )


