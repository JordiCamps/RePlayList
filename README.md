# RePlayList

A modern desktop application for transferring playlists between Spotify and YouTube Music. Built with Tauri (Rust + SvelteKit) for native performance and a beautiful user interface.

## 📋 Table of Contents

- [Features](#-features)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
  - [Backend Configuration](#backend-configuration)
  - [API Credentials Setup](#api-credentials-setup)
    - [Spotify Setup](#spotify-setup)
    - [YouTube Setup](#youtube-setup)
  - [Detailed API Setup Guide](#detailed-api-setup-guide)
- [Development](#-development)
  - [Available Scripts](#available-scripts)
  - [Backend Development](#backend-development)
  - [Frontend Development](#frontend-development)
  - [Tauri Development](#tauri-development)
- [Usage](#-usage)
  - [Desktop Application](#desktop-application)
  - [Command Line Interface](#command-line-interface)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
  - [Common Issues](#common-issues)
  - [Debug Mode](#debug-mode)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)
- [Disclaimer](#-disclaimer)
- [Acknowledgments](#-acknowledgments)
- [Support](#-support)

## ✨ Features

- **Cross-Platform Playlist Transfer** - Move playlists between Spotify and YouTube Music
- **Smart Track Matching** - Intelligent fuzzy matching with duplicate detection
- **Real-time Progress** - Live transfer progress with detailed status updates
- **OAuth2 Authentication** - Secure login to both platforms
- **Modern UI** - Clean, responsive interface built with SvelteKit
- **Native Performance** - Desktop app powered by Tauri and Rust
- **CLI Support** - Command-line interface for advanced users

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+ with pip
- **Rust** (latest stable)
- **Spotify Developer Account** - [Create app](https://developer.spotify.com/dashboard)
- **YouTube Data API Key** - [Get API key](https://console.developers.google.com/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ahmet-Ozbay/RePlayList.git
   cd replaylist
   ```

2. **Install dependencies:**
   ```bash
   # Install frontend dependencies
   cd frontend && npm install && cd ..
   
   # Install backend dependencies
   cd backend && pip install -r requirements.txt && cd ..
   
   # Install Tauri dependencies
   cd tauri && npm install && cd ..
   ```

3. **Configure API credentials:**
   ```bash
   # Copy the example config
   cp config.example.json config.json
   
   # Edit with your API credentials
   nano config.json
   ```
   
   **Note:** The app looks for `config.json` in the root directory. You can also edit the configuration through the app's settings interface once it's running.

4. **Run the application:**
   ```bash
   # Development mode (all components)
   npm run dev:tauri
   
   # Or run components separately
   npm run dev:backend    # Backend API
   npm run dev:frontend   # Frontend web app
   npm run tauri          # Desktop app
   ```

## 📁 Project Structure

```
RePlayList/
├── frontend/                 # SvelteKit frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/   # Reusable UI components
│   │   │   ├── stores/       # State management
│   │   │   ├── services/     # API services
│   │   │   └── types/        # TypeScript definitions
│   │   └── routes/           # SvelteKit pages
│   └── package.json
├── backend/                  # Python FastAPI backend
│   ├── replaylist/
│   │   ├── auth/            # Authentication modules
│   │   ├── spotify/         # Spotify API integration
│   │   ├── youtube/         # YouTube API integration
│   │   ├── transfer/        # Playlist transfer logic
│   │   ├── server/          # API endpoints
│   │   └── utils/           # Utility functions
│   ├── main.py              # FastAPI application
│   └── requirements.txt
├── tauri/                   # Tauri desktop app
│   ├── src/                 # Rust source code
│   ├── icons/               # Application icons
│   └── tauri.conf.json      # Tauri configuration
└── package.json             # Root package.json
```

## ⚙️ Configuration

### Backend Configuration

Create `backend/config.json`:

```json
{
  "spotify": {
    "client_id": "your_spotify_client_id",
    "client_secret": "your_spotify_client_secret",
    "redirect_uri": "http://localhost:8888/callback"
  },
  "youtube": {
    "api_key": "your_youtube_api_key"
  },
  "app": {
    "debug": false,
    "log_level": "INFO"
  }
}
```

### API Credentials Setup

**📖 For detailed setup instructions, see [API_SETUP.md](API_SETUP.md)**

#### Quick Setup:
1. **Spotify**: Create app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. **YouTube**: Enable YouTube Data API v3 at [Google Cloud Console](https://console.developers.google.com/)
3. **Configuration**: Copy `config.example.json` to `config.json` and add your credentials

#### Important Notes:
- **YouTube API**: Requires additional setup (test users, OAuth consent screen)
- **Redirect URIs**: Must match exactly in both app and configuration
- **Security**: Never commit your `config.json` file

### Detailed API Setup Guide

For comprehensive step-by-step instructions including:
- **Spotify API setup** with redirect URI configuration
- **YouTube API setup** with OAuth consent screen and test users
- **Troubleshooting common issues**
- **Security best practices**

See [API_SETUP.md](API_SETUP.md) for the complete guide.

## 🛠️ Development

### Available Scripts

```bash
# Development
npm run dev                 # Start all components
npm run dev:backend        # Backend only
npm run dev:frontend       # Frontend only
npm run dev:tauri          # Desktop app only

# Building
npm run build              # Build frontend
npm run build:backend      # Build backend executable
npm run build:app          # Build complete desktop app

# CLI
python -m replaylist.cli   # Run CLI interface
```

### Backend Development

```bash
cd backend

# Run with auto-reload
python -m uvicorn main:app --reload

# Run tests
python -m pytest

# Code formatting
black .
flake8 .
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Type checking
npm run check
```

### Tauri Development

```bash
cd tauri

# Development mode
npm run tauri dev

# Build for production
npm run tauri build
```

## 📖 Usage

### Desktop Application

1. **Launch the app** - Run `npm run dev:tauri`
2. **Authenticate** - Click "Connect" for Spotify and YouTube
3. **Select Playlists** - Choose source and target playlists
4. **Transfer** - Click "Start Transfer" and monitor progress

### Command Line Interface

```bash
# List playlists
python -m replaylist.cli playlists spotify
python -m replaylist.cli playlists youtube

# Transfer playlist
python -m replaylist.cli transfer --from spotify --to youtube --playlist-id "your_playlist_id"

# Search tracks
python -m replaylist.cli search --platform spotify --query "song name"
```

## 🏗️ Architecture

### Backend Architecture

- **FastAPI** - Modern Python web framework
- **Modular Design** - Organized into focused subpackages
- **OAuth2 Flow** - Secure authentication with both platforms
- **Async/Await** - High-performance async operations
- **Type Hints** - Full type safety with Pydantic models

### Frontend Architecture

- **SvelteKit** - Modern web framework with SSR
- **Component-Based** - Reusable, focused components
- **State Management** - Svelte stores for reactive state
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling

### Desktop Architecture

- **Tauri** - Rust-based desktop framework
- **Sidecar Process** - Backend runs as separate process
- **Native Performance** - Rust core with web frontend
- **Cross-Platform** - Windows, macOS, Linux support

## 🔧 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check config.json exists and has valid credentials

**Frontend build fails:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)
- Run type check: `npm run check`

**Tauri build fails:**
- Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
- Update Rust: `rustup update`
- Clear build cache: `cargo clean`

**Authentication issues:**
- Verify redirect URIs match exactly
- Check API credentials are correct
- Ensure ports 8000 and 8888 are available

### Debug Mode

Enable debug logging:

```json
{
  "app": {
    "debug": true,
    "log_level": "DEBUG"
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow existing code style and patterns
- Add tests for new features
- Update documentation as needed
- Use conventional commit messages
- Ensure all checks pass before submitting PR

## 🔒 Security

For security vulnerabilities, please see our [Security Policy](SECURITY.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any damages or issues that may arise from using this software. Users are responsible for complying with the terms of service of Spotify, YouTube, and other platforms when using this application.

**This project is not officially affiliated with, endorsed by, or sponsored by Spotify, YouTube, or Google. We are independent developers using their publicly available APIs.**

## 🙏 Acknowledgments

- [Tauri](https://tauri.app/) - Desktop app framework
- [SvelteKit](https://kit.svelte.dev/) - Web framework
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [YouTube Data API](https://developers.google.com/youtube/v3)

## 📞 Support

- **Issues** - [GitHub Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- **Discussions** - [GitHub Discussions](https://github.com/Ahmet-Ozbay/RePlayList/discussions)
- **Documentation** - [Wiki](https://github.com/Ahmet-Ozbay/RePlayList/wiki)

---

**Made with ❤️ for music lovers who want to keep their playlists in sync across platforms.**