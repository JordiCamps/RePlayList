/// Authentication-related Tauri commands
/// 
/// Commands for handling OAuth authentication flows and window management.

use std::sync::{Mutex, OnceLock};
use tauri::Manager;

/// Global state for tracking the last authentication window
static LAST_AUTH_LABEL: OnceLock<Mutex<Option<String>>> = OnceLock::new();

/// Close the last opened authentication window
/// 
/// # Arguments
/// * `app` - Tauri app handle
/// 
/// # Returns
/// Result indicating success or failure
#[tauri::command]
pub fn close_last_auth_window(app: tauri::AppHandle) -> Result<(), String> {
    let lock = LAST_AUTH_LABEL.get_or_init(|| Mutex::new(None));
    if let Some(label) = lock.lock().map_err(|e| e.to_string())?.clone() {
        if let Some(w) = app.get_webview_window(&label) {
            w.close().map_err(|e| e.to_string())?;
        }
        *lock.lock().map_err(|e| e.to_string())? = None;
    }
    Ok(())
}

/// Open an authentication window for OAuth flow
/// 
/// # Arguments
/// * `app` - Tauri app handle
/// * `url` - OAuth provider URL
/// 
/// # Returns
/// Result indicating success or failure
#[tauri::command]
pub async fn open_auth_window(app: tauri::AppHandle, url: String) -> Result<(), String> {
    use url::Url;
    
    // Create a small auth window that loads the provider URL
    let label = format!("auth-{}", uuid::Uuid::new_v4());
    let auth_url: Url = Url::parse(&url).map_err(|e| e.to_string())?;
    
    let _window = tauri::WebviewWindowBuilder::new(&app, &label, tauri::WebviewUrl::External(auth_url))
        .title("Authenticate")
        .inner_size(500.0, 650.0)
        .resizable(true)
        .build()
        .map_err(|e| e.to_string())?;

    // Remember last auth window label so frontend can request closing after success
    let lock = LAST_AUTH_LABEL.get_or_init(|| Mutex::new(None));
    if let Ok(mut guard) = lock.lock() {
        *guard = Some(label);
    }

    // The provider will redirect to local callback which sets state in backend.
    // The window will be manually closed by the user or automatically when auth completes.
    Ok(())
}
