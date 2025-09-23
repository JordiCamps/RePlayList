/// System-related Tauri commands
/// 
/// Commands for general system operations like opening URLs and window management.


/// Greet command for testing Tauri communication
/// 
/// # Arguments
/// * `name` - The name to greet
/// 
/// # Returns
/// A greeting message
#[tauri::command]
pub fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

/// Open a URL in the default browser
/// 
/// # Arguments
/// * `app` - Tauri app handle
/// * `url` - URL to open
/// 
/// # Returns
/// Result indicating success or failure
#[tauri::command]
pub fn open_url(app: tauri::AppHandle, url: String) -> Result<(), String> {
    use tauri_plugin_opener::OpenerExt;
    app.opener()
        .open_url(url, Option::<String>::None)
        .map_err(|e| e.to_string())
}

/// Close the current window
/// 
/// # Arguments
/// * `window` - Tauri webview window
/// 
/// # Returns
/// Result indicating success or failure
#[tauri::command]
pub fn close_auth_self(window: tauri::WebviewWindow) -> Result<(), String> {
    window.close().map_err(|e| e.to_string())
}
