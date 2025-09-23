# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project documentation
- Professional README with setup instructions
- Detailed CONTRIBUTING.md guide
- Architecture documentation
- Code of Conduct
- MIT License with legal protections
- Platform disclaimers for API usage

### Changed
- Complete backend refactoring into modular architecture
- Frontend refactoring with component-based design
- Tauri desktop application optimization
- Icon system with multi-resolution support

## [1.0.0] - 2025-09-23

### Highlights
- First stable release with a portable Windows build (no Python/Rust/Node required).
- One-file Python backend sidecar bundled with Tauri; reads `config.json` next to the EXE.
- Crisp app icons generated from SVG with proper multi-layer ICO to fix blurry taskbar icon.

### Added
- Portable ZIP distribution with `RePlayList.exe` and configuration template.
- Automatic config discovery for portable and installed setups.
- Comprehensive accessibility improvements (keyboard nav, ARIA, focus management).
- Animations and transitions (staggered, responsive) for a smoother UX.
- Notifications/toasts for errors and status updates.

### Changed
- Major frontend refactor (SvelteKit) for performance, responsiveness, and maintainability.
- Tauri structure cleanup and module extraction (commands, backend, utils) adhering to SOLID.
- Backend config manager updated to prioritize executable directory and CI defaults.
- CI workflow simplified and made resilient to missing local config via `CI` defaults.

### Fixed
- Windows taskbar icon blurriness by generating a proper multi-size ICO.
- PyInstaller `python313.dll` issues by producing a true one-file EXE and adjusting startup.
- Backend startup import path issues by changing CWD and importing `main.app` directly.

### Notes
- Place `config.json` next to `RePlayList.exe` (or copy `config.example.json` to `config.json`).
- Project is not affiliated with Spotify/YouTube; uses their official APIs.

## [0.1.0] - 2025-09-23

### Added
- **Backend Architecture Refactoring**
  - Modular subpackage structure (`auth/`, `spotify/`, `youtube/`, `transfer/`, `server/`, `utils/`, `cli/`)
  - `AuthManager` class for unified OAuth2 handling
  - `SpotifyAPI` and `YouTubeAPI` client classes
  - `TransferExecutor` with background thread execution
  - `TrackMatcher` with fuzzy matching algorithms
  - `PlaylistManager` for playlist operations
  - Comprehensive CLI interface with subcommands
  - FastAPI server with modular endpoint organization
  - Utility functions with decorators for retry, rate limiting, and error handling

- **Frontend Architecture Refactoring**
  - SvelteKit-based modern web application
  - Component-based UI with reusable components
  - Svelte stores for reactive state management
  - Service layer for API communication
  - Composables for reusable logic functions
  - Step-based transfer wizard interface
  - TypeScript support with comprehensive type definitions

- **Desktop Application**
  - Tauri-based native desktop wrapper
  - Rust backend with modular command structure
  - Sidecar process management for Python backend
  - Multi-resolution icon support
  - Custom window configuration
  - System integration features

- **Authentication System**
  - OAuth2 flow for Spotify and YouTube
  - Secure token management
  - Callback handling with HTML templates
  - Authentication status tracking

- **Playlist Transfer System**
  - Cross-platform playlist transfer between Spotify and YouTube
  - Intelligent track matching with fuzzy logic
  - Duplicate detection and handling
  - Real-time progress tracking
  - Error handling and retry mechanisms
  - Transfer summary and reporting

- **API Endpoints**
  - Authentication endpoints (`/auth/{platform}/login`, `/auth/{platform}/callback`)
  - Playlist management (`/playlists/{platform}`)
  - Transfer operations (`/transfer/start`, `/transfer/{id}/progress`)
  - Configuration management (`/config`)

- **Command Line Interface**
  - Authentication commands
  - Playlist listing and management
  - Transfer operations
  - Search functionality
  - Comprehensive help system

- **Configuration Management**
  - JSON-based configuration system
  - Environment variable support
  - API credential management
  - Debug and logging configuration

### Changed
- **Backend Structure**
  - Refactored monolithic files into focused modules
  - Implemented facade pattern for backward compatibility
  - Separated concerns across dedicated subpackages
  - Enhanced error handling and logging

- **Frontend Structure**
  - Broke down large components into focused, reusable pieces
  - Implemented proper state management patterns
  - Created service layer for API abstraction
  - Added comprehensive TypeScript support

- **Desktop Application**
  - Optimized Tauri configuration
  - Enhanced icon system with multiple resolutions
  - Improved window management and user experience
  - Better integration with backend processes

### Technical Improvements
- **Code Quality**
  - Comprehensive documentation and comments
  - Type hints throughout Python codebase
  - TypeScript support in frontend
  - Consistent code formatting and linting
  - SOLID principles implementation

- **Performance**
  - Async/await patterns throughout
  - Efficient API rate limiting
  - Background processing for transfers
  - Optimized state management

- **Security**
  - OAuth2 secure authentication flow
  - Token management without persistent storage
  - Input validation and sanitization
  - CORS configuration for development

- **User Experience**
  - Intuitive step-based transfer wizard
  - Real-time progress updates
  - Comprehensive error handling
  - Responsive design with Tailwind CSS

### Documentation
- **README.md** - Comprehensive project overview and setup instructions
- **CONTRIBUTING.md** - Detailed contribution guidelines
- **ARCHITECTURE.md** - Technical architecture documentation
- **CODE_OF_CONDUCT.md** - Community guidelines
- **LICENSE** - MIT License with legal protections

### Dependencies
- **Backend**: FastAPI, Pydantic, requests, uvicorn
- **Frontend**: SvelteKit, TypeScript, Tailwind CSS
- **Desktop**: Tauri, Rust
- **Development**: Black, Flake8, Prettier, ESLint

## [0.0.1] - Initial Development

### Added
- Basic playlist transfer functionality
- Initial OAuth2 implementation
- Simple web interface
- Core API endpoints
- Basic configuration system

---

## Version History

- **v1.0.0** - First stable, portable Windows release
- **v0.1.0** - Complete architectural refactoring and modernization
- **v0.0.1** - Initial development and basic functionality

## Migration Notes

### From v0.0.1 to v0.1.0

The major refactoring in v0.1.0 maintains backward compatibility through facade patterns. However, some internal APIs have changed:

- **Backend**: All main classes are still available through their original module names
- **Frontend**: Component structure has changed, but main functionality remains the same
- **Configuration**: Configuration format remains the same
- **API**: All existing API endpoints continue to work

### Breaking Changes

None in v0.1.0 - all changes are internal refactoring with maintained compatibility.

## Future Roadmap

- [ ] Automated testing suite
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Docker containerization
- [ ] Additional platform support (Apple Music, Amazon Music)
- [ ] Advanced matching algorithms
- [ ] Batch transfer operations
- [ ] Transfer scheduling
- [ ] Plugin system for custom integrations
