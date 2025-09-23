/// Backend process management
/// 
/// Handles spawning and monitoring the Python backend sidecar process.


/// Setup backend sidecar process for production builds
/// 
/// # Arguments
/// * `app` - Tauri app handle
/// 
/// # Returns
/// Result indicating success or failure
pub fn setup_backend_sidecar(app: &tauri::AppHandle) -> Result<(), String> {
    use tauri_plugin_shell::ShellExt;
    
    // Spawn bundled backend sidecar only in production builds
    let spawn_result = {
        let shell = app.shell();
        shell.sidecar("replaylist-backend").and_then(|cmd| cmd.spawn())
    };

    match spawn_result {
        Ok((mut rx, _child)) => {
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        tauri_plugin_shell::process::CommandEvent::Stdout(line) => {
                            println!("[backend] {}", String::from_utf8_lossy(&line));
                        }
                        tauri_plugin_shell::process::CommandEvent::Stderr(line) => {
                            eprintln!("[backend:err] {}", String::from_utf8_lossy(&line));
                        }
                        tauri_plugin_shell::process::CommandEvent::Terminated(payload) => {
                            eprintln!("[backend] terminated: {:?}", payload);
                            break;
                        }
                        _ => {}
                    }
                }
            });
        }
        Err(err) => {
            eprintln!("Failed to spawn backend sidecar: {}", err);
        }
    }

    Ok(())
}
