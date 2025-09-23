/// Error handling utilities
/// 
/// Common error types and handling functions for the Tauri application.

use std::fmt;

/// Application error types
#[derive(Debug)]
pub enum AppError {
    /// Authentication related errors
    Auth(String),
    /// Window management errors
    Window(String),
    /// URL parsing errors
    Url(String),
    /// Backend process errors
    Backend(String),
    /// General application errors
    General(String),
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AppError::Auth(msg) => write!(f, "Authentication error: {}", msg),
            AppError::Window(msg) => write!(f, "Window error: {}", msg),
            AppError::Url(msg) => write!(f, "URL error: {}", msg),
            AppError::Backend(msg) => write!(f, "Backend error: {}", msg),
            AppError::General(msg) => write!(f, "Application error: {}", msg),
        }
    }
}

impl std::error::Error for AppError {}

/// Convert AppError to String for Tauri command results
impl From<AppError> for String {
    fn from(error: AppError) -> Self {
        error.to_string()
    }
}
