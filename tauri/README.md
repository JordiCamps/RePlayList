# RePlayList Tauri Desktop Application

A modern desktop application built with Tauri for transferring playlists between Spotify and YouTube platforms.

## Architecture

### Technology Stack
- **Framework**: Tauri 2.x with Rust backend
- **Frontend**: SvelteKit (referenced from `../frontend/`)
- **Backend**: Python FastAPI (sidecar process)
- **Build System**: Cargo + npm
- **Platform**: Windows (primary), with cross-platform support

### Project Structure

```
tauri/
├── src/                    # Rust source code
│   ├── commands/          # Tauri command modules
│   │   ├── mod.rs        # Command module exports
│   │   ├── auth.rs       # Authentication commands
│   │   └── system.rs     # System utility commands
│   ├── backend/          # Backend process management
│   │   ├── mod.rs        # Backend module exports
│   │   └── process.rs    # Sidecar process handling
│   ├── utils/            # Utility functions
│   │   ├── mod.rs        # Utility module exports
│   │   └── error.rs      # Error handling types
│   ├── lib.rs            # Main library entry point
│   └── main.rs           # Application entry point
├── binaries/             # Backend executable (production)
├── capabilities/         # Tauri security capabilities
├── gen/                  # Generated schemas
├── icons/               # Custom application icons (from frontend/assets/logo)
├── target/              # Rust build artifacts
├── Cargo.toml           # Rust dependencies
├── package.json         # Node.js dependencies
└── tauri.conf.json      # Tauri configuration
```

## Development

### Prerequisites
- Rust 1.70+
- Node.js 18+
- Python 3.8+ (for backend)
- Tauri CLI: `npm install -g @tauri-apps/cli`

### Setup
```bash
# Install Rust dependencies
cargo build

# Install Node.js dependencies
npm install

# Install backend dependencies (from project root)
cd .. && pip install -r requirements.txt
```

### Development Commands

#### From Project Root
```bash
# Start development environment (backend + frontend + tauri)
npm run dev:tauri

# Build desktop application
npm run build:app

# Run Tauri development
npm run tauri
```

#### From Tauri Directory
```bash
# Check Rust code
cargo check

# Build Rust code
cargo build

# Run Tauri development
npm run tauri dev

# Build desktop application
npm run tauri build
```

## Rust Architecture

### Module Organization

#### Commands Module (`src/commands/`)
Tauri commands are organized by functionality:

- **`system.rs`**: General system operations
  - `greet()` - Test command for Tauri communication
  - `open_url()` - Open URLs in default browser
  - `close_auth_self()` - Close current window

- **`auth.rs`**: Authentication flow management
  - `open_auth_window()` - Open OAuth authentication window
  - `close_last_auth_window()` - Close last opened auth window

#### Backend Module (`src/backend/`)
Backend process management for production builds:

- **`process.rs`**: Sidecar process handling
  - `setup_backend_sidecar()` - Spawn Python backend process
  - Process monitoring and error handling

#### Utils Module (`src/utils/`)
Utility functions and error handling:

- **`error.rs`**: Application error types
  - `AppError` enum with specific error variants
  - Error conversion and display implementations

### Command Registration
Commands are registered in `src/lib.rs`:

```rust
.invoke_handler(tauri::generate_handler![
    // System commands
    commands::system::greet,
    commands::system::open_url,
    commands::system::close_auth_self,
    // Auth commands
    commands::auth::open_auth_window,
    commands::auth::close_last_auth_window,
])
```

## Configuration

### Tauri Configuration (`tauri.conf.json`)
```json
{
  "productName": "RePlayList",
  "version": "0.1.0",
  "identifier": "com.replaylist.tauri",
  "build": {
    "beforeDevCommand": "cd .. && npm run dev:tauri",
    "devUrl": "http://localhost:3000",
    "frontendDist": "../frontend/build"
  },
  "app": {
    "windows": [
      {
        "title": "RePlayList",
        "width": 1200,
        "height": 800,
        "center": true,
        "minWidth": 800,
        "minHeight": 600,
        "resizable": true
      }
    ]
  },
  "bundle": {
    "externalBin": ["binaries/replaylist-backend"],
    "icon": ["icons/32x32.png", "icons/128x128.png", ...]
  }
}
```

### Window Configuration
The application window is configured with:
- **Default Size**: 1200x800 pixels (larger for better UX)
- **Centered**: Automatically centers on screen
- **Resizable**: Users can resize the window
- **Minimum Size**: 800x600 pixels (prevents too small windows)
- **Window Controls**: Maximize, minimize, and close buttons enabled
- **Decorations**: Standard window title bar and borders
- **User Experience**: Standard desktop application behavior

### Cargo Configuration (`Cargo.toml`)
```toml
[package]
name = "replaylist-tauri"
version = "0.1.0"
description = "RePlayList Desktop Application"
authors = ["Ozbay"]
edition = "2021"

[lib]
name = "replaylist_tauri_lib"
crate-type = ["staticlib", "cdylib", "rlib"]
```

## Build Process

### Development Build
1. **Backend**: Python FastAPI server runs separately
2. **Frontend**: SvelteKit dev server on port 3000
3. **Tauri**: Desktop app connects to localhost:3000

### Production Build
1. **Backend**: Python executable bundled as sidecar
2. **Frontend**: Static files built to `../frontend/build`
3. **Tauri**: Desktop app with embedded frontend and backend

### Build Commands
```bash
# Full production build
npm run build:app

# Individual components
npm run build:backend    # Build Python executable
npm run build           # Build frontend
npm run tauri build     # Build desktop app
```

## Security

### Capabilities
Tauri security is configured in `capabilities/default.json`:
- File system access for configuration
- Network access for API calls
- Window management for authentication

### CSP (Content Security Policy)
Currently disabled for development:
```json
"security": {
  "csp": null
}
```

## Platform Support

### Windows
- Primary development platform
- NSIS installer generation
- MSI package creation
- Windows-specific optimizations

### Cross-Platform
- macOS support (with additional setup)
- Linux support (with additional setup)
- Platform-specific build configurations

### Custom Icons
The application uses custom logos from `../frontend/public/assets/logo/`:
- **Windows**: ICO format (32x32, 128x128, 256x256, 512x512)
- **macOS**: ICNS format (256x256)
- **Windows Store**: PNG format (various sizes for different contexts)
- **General**: PNG format (16x16 to 512x512)

Icons are automatically copied from the frontend assets during setup.

## Dependencies

### Rust Dependencies
```toml
[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-opener = "2"
tauri-plugin-shell = "2"
uuid = { version = "1", features = ["v4"] }
url = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

### Node.js Dependencies
```json
{
  "dependencies": {
    "@tauri-apps/api": "^2",
    "@tauri-apps/plugin-opener": "^2"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2"
  }
}
```

## Troubleshooting

### Common Issues

#### Build Failures
```bash
# Clean and rebuild
cargo clean
cargo build

# Check Rust version
rustc --version
```

#### Frontend Connection Issues
- Ensure frontend dev server is running on port 3000
- Check `tauri.conf.json` devUrl configuration
- Verify frontend build output in `../frontend/build`

#### Backend Sidecar Issues
- Ensure Python executable is in `binaries/` directory
- Check backend build process completed successfully
- Verify sidecar configuration in `tauri.conf.json`

### Debug Mode
Enable debug logging:
```rust
// In Rust code
println!("Debug: {}", message);

// Check console output in development
```

## Contributing

### Code Style
- Follow Rust naming conventions
- Use `cargo fmt` for formatting
- Use `cargo clippy` for linting
- Document all public functions

### Module Guidelines
- Single responsibility per module
- Clear module boundaries
- Consistent error handling
- Comprehensive documentation

### Testing
```bash
# Run Rust tests
cargo test

# Check code quality
cargo clippy

# Format code
cargo fmt
```

## Deployment

### Release Build
```bash
# Full release build
npm run build:app

# Output locations
# - Windows: target/release/bundle/nsis/
# - MSI: target/release/bundle/msi/
```

### Distribution
- NSIS installer for Windows
- MSI package for enterprise deployment
- Portable executable option
- Code signing (production)

## Performance

### Optimization
- Release builds with optimizations
- Minimal bundle size
- Efficient memory usage
- Fast startup time

### Monitoring
- Backend process monitoring
- Error logging and reporting
- Performance metrics collection
- User experience tracking