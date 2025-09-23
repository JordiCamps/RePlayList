/// Utility functions and helpers
/// 
/// This module contains utility functions used throughout the application.

pub mod error;

use std::{fs, io::Write, path::PathBuf};

/// Ensure a `config.json` exists next to the executable.
/// If missing, it will be created from the embedded `config.example.json`.
pub fn ensure_config_file_next_to_exe() -> Result<(), String> {
    // Determine install directory (next to the current executable)
    let exe_dir: PathBuf = std::env::current_exe()
        .map_err(|e| format!("Failed to get current_exe: {e}"))?
        .parent()
        .ok_or_else(|| "Failed to determine executable directory".to_string())?
        .to_path_buf();

    let config_path = exe_dir.join("config.json");
    if config_path.exists() {
        return Ok(());
    }

    // Embed example config at compile-time
    const EXAMPLE_JSON: &str = include_str!(concat!(env!("CARGO_MANIFEST_DIR"), "/../config.example.json"));

    // Write new config.json
    let mut f = fs::File::create(&config_path)
        .map_err(|e| format!("Failed to create {}: {e}", config_path.display()))?;
    f.write_all(EXAMPLE_JSON.as_bytes())
        .map_err(|e| format!("Failed to write {}: {e}", config_path.display()))?;

    Ok(())
}

pub use error::*;
