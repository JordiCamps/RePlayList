/// RePlayList Tauri Application Library
/// 
/// This is the main library crate for the RePlayList desktop application.
/// It provides a modular structure for Tauri commands and backend management.


// Module declarations
mod commands;
mod backend;
mod utils;

// Re-export commonly used items
pub use commands::*;
pub use backend::*;
pub use utils::*;

/// Main application entry point
/// 
/// This function initializes the Tauri application with all plugins and commands.
/// It handles both development and production configurations.
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let context = tauri::generate_context!();

    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            // System commands
            commands::system::greet,
            commands::system::open_url,
            commands::system::close_auth_self,
            // Auth commands
            commands::auth::open_auth_window,
            commands::auth::close_last_auth_window,
        ]);

    #[cfg(debug_assertions)]
    let builder = builder; // In dev, backend runs separately

    #[cfg(not(debug_assertions))]
    let builder = builder.setup(|app| {
        // Spawn bundled backend sidecar only in production builds
        backend::process::setup_backend_sidecar(app.handle())?;
        Ok(())
    });

    builder
        .run(context)
        .expect("error while running tauri application");
}