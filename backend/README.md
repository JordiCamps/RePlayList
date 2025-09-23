# RePlayList Backend

The backend service for RePlayList, a cross-platform desktop application for transferring playlists between Spotify and YouTube.

## Features

- **OAuth2 Authentication**: Secure authentication with Spotify and YouTube APIs
- **Playlist Management**: List, view, and manage playlists on both platforms
- **Cross-Platform Transfer**: Transfer playlists between Spotify and YouTube
- **Progress Tracking**: Real-time progress updates during transfers
- **REST API**: Clean REST API for frontend integration
- **CLI Interface**: Command-line interface for power users

## Architecture

The backend follows a modular architecture with clear separation of concerns:

```
backend/
├── main.py                # FastAPI application entry point
├── entry_server.py        # Tauri sidecar entry point
├── cli.py                 # CLI facade (backward compatibility)
├── server/                # FastAPI server modules
│   ├── __init__.py        # Server package initialization
│   ├── models.py          # Pydantic models for API
│   ├── state.py           # Global state management
│   ├── auth.py            # Authentication endpoints
│   ├── playlists.py       # Playlist endpoints
│   ├── transfer.py        # Transfer endpoints
│   └── config.py          # Configuration endpoints
├── cli/                   # CLI modules
│   ├── __init__.py        # CLI package initialization
│   ├── types.py           # CLI-specific data types
│   ├── core.py            # Main CLI orchestrator
│   ├── auth.py            # Authentication operations
│   ├── playlists.py       # Playlist operations
│   ├── transfer.py        # Transfer operations
│   ├── search.py          # Search operations
│   └── parser.py          # Argument parsing
└── replaylist/            # Core business logic
    ├── __init__.py        # Package initialization
    ├── config/            # Configuration management
    │   ├── __init__.py    # Config facade
    │   ├── types.py       # Configuration data types
    │   └── manager.py     # Configuration manager
    ├── auth/              # Authentication system
    │   ├── __init__.py    # Auth facade
    │   ├── types.py       # Auth data types
    │   ├── manager.py     # Auth manager
    │   ├── spotify.py     # Spotify OAuth
    │   ├── youtube.py     # YouTube OAuth
    │   ├── callback.py    # OAuth callback handler
    │   └── templates.py   # HTML templates
    ├── spotify/           # Spotify API client
    │   ├── __init__.py    # Spotify facade
    │   ├── types.py       # Spotify data types
    │   └── client.py      # Spotify API client
    ├── youtube/           # YouTube API client
    │   ├── __init__.py    # YouTube facade
    │   ├── types.py       # YouTube data types
    │   └── client.py      # YouTube API client
    ├── transfer/          # Transfer system
    │   ├── __init__.py    # Transfer facade
    │   ├── types.py       # Transfer data types
    │   ├── transfer.py    # Main transfer orchestrator
    │   ├── executor.py    # Transfer execution
    │   ├── matching.py    # Track matching logic
    │   ├── playlist.py    # Playlist management
    │   └── naming.py      # Playlist naming
    └── utils/             # Utility functions
        ├── __init__.py    # Utils facade
        ├── logging.py     # Logging utilities
        ├── ids.py         # ID generation
        ├── text.py        # Text processing
        ├── format.py      # Formatting utilities
        ├── api.py         # API utilities
        ├── validate.py    # Validation utilities
        ├── decorators.py  # Decorators
        ├── collections.py # Collection utilities
        └── dupes.py       # Duplicate detection
```

## Architecture Overview

The backend follows a modular architecture with clear separation of concerns:

- **Server modules**: Each endpoint group has its own module
- **CLI modules**: Command functionality is logically grouped  
- **Core packages**: Business logic is organized by domain
- **Facade pattern**: Maintains backward compatibility for existing imports

## Setup

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account
- YouTube Data API v3 access

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API credentials in `config.json`:
```json
{
  "spotify": {
    "client_id": "YOUR_SPOTIFY_CLIENT_ID",
    "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8080/callback"
  },
  "youtube": {
    "client_id": "YOUR_YOUTUBE_CLIENT_ID",
    "client_secret": "YOUR_YOUTUBE_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8080/callback"
  },
  "app": {
    "debug": true,
    "default_transfer_mode": "new_playlist",
    "http_port": 5000,
    "log_level": "INFO"
  }
}
```

### Running the Server

#### Option 1: Using the Tauri sidecar entry point
```bash
python backend/entry_server.py
```

#### Option 2: Direct server execution
```bash
cd backend
python main.py
```

#### Option 3: Using uvicorn directly
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload
```

#### Option 4: Using npm scripts (from project root)
```bash
npm run dev:backend
npm run start:backend
```

## API Endpoints

### Authentication
- `POST /auth/{platform}/login` - Start OAuth authentication
- `POST /auth/{platform}/callback` - Handle OAuth callback

### Playlists
- `GET /playlists/{platform}` - List user playlists
- `GET /playlists/{platform}/{id}` - Get playlist tracks

### Transfer
- `POST /transfer/start` - Start playlist transfer
- `GET /transfer/{id}/progress` - Get transfer progress
- `GET /transfer/{id}/summary` - Get transfer summary

### Configuration
- `GET /config` - Get current configuration
- `POST /config` - Update configuration

## CLI Usage

```bash
# Authenticate with platforms
python backend/cli.py auth spotify
python backend/cli.py auth youtube

# List playlists
python backend/cli.py list spotify
python backend/cli.py list youtube

# Show playlist tracks
python backend/cli.py tracks spotify PLAYLIST_ID
python backend/cli.py tracks youtube PLAYLIST_ID

# Transfer playlists
python backend/cli.py transfer spotify SOURCE_ID youtube --mode new_playlist
python backend/cli.py transfer youtube SOURCE_ID spotify --mode append --target-playlist-id TARGET_ID

# Search for tracks
python backend/cli.py search spotify "song name"
python backend/cli.py search youtube "video title"

# Show configuration
python backend/cli.py config
```

### CLI Modules

- **`cli/core.py`**: Main `RePlayListCLI` orchestrator class
- **`cli/auth.py`**: Authentication operations and token management
- **`cli/playlists.py`**: Playlist listing and track viewing
- **`cli/transfer.py`**: Transfer and preview operations
- **`cli/search.py`**: Search functionality
- **`cli/parser.py`**: Argument parsing and command execution
- **`cli/types.py`**: CLI-specific data structures

### Programmatic Usage

```python
from backend.cli import RePlayListCLI

cli = RePlayListCLI()
cli.authenticate_platform('spotify')
cli.list_playlists('spotify')
cli.search_tracks('spotify', 'bohemian rhapsody')
```

## Module Structure

The backend has been refactored from 8 large files into 40+ focused modules:

### Core Packages
- **`replaylist/auth/`**: OAuth2 authentication system
- **`replaylist/spotify/`**: Spotify API client
- **`replaylist/youtube/`**: YouTube API client  
- **`replaylist/transfer/`**: Playlist transfer logic
- **`replaylist/config/`**: Configuration management
- **`replaylist/utils/`**: Utility functions

### Server Modules
- **`server/auth.py`**: Authentication endpoints
- **`server/playlists.py`**: Playlist endpoints
- **`server/transfer.py`**: Transfer endpoints
- **`server/config.py`**: Configuration endpoints
- **`server/models.py`**: Pydantic models
- **`server/state.py`**: Global state management

### CLI Modules
- **`cli/core.py`**: Main CLI orchestrator
- **`cli/auth.py`**: Authentication operations
- **`cli/playlists.py`**: Playlist operations
- **`cli/transfer.py`**: Transfer operations
- **`cli/search.py`**: Search operations
- **`cli/parser.py`**: Argument parsing

## Development

### Testing
```bash
python test_backend.py
```

### Code Quality
```bash
# Format code
black backend/

# Lint checking
flake8 backend/

# Type checking
mypy backend/
```

## Configuration

Configuration is managed via `config.json` in the project root:

- **spotify/youtube**: API credentials and redirect URIs
- **app.debug**: Debug mode for development
- **app.http_port**: HTTP server port
- **app.log_level**: Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

- HTTP status codes and error messages for API errors
- Authentication error handling with clear messages
- Detailed error reporting for failed transfers
- Structured logging for debugging and monitoring

## Security

- OAuth2 tokens stored in memory only
- HTTPS for all API requests
- Input validation on all endpoints
- Rate limiting recommended for production
