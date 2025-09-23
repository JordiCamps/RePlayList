# RePlayList Architecture

This document describes the technical architecture of RePlayList, a cross-platform playlist transfer application.

## System Overview

RePlayList consists of three main components:
- **Backend API** - Python FastAPI server handling authentication and transfer logic
- **Frontend Web App** - SvelteKit application providing the user interface
- **Desktop Application** - Tauri-based native desktop wrapper

## Backend Architecture

### Core Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── entry_server.py           # Production server entry point
├── replaylist/               # Core application package
│   ├── auth/                 # Authentication modules
│   │   ├── manager.py        # AuthManager - unified auth handling
│   │   ├── spotify.py        # Spotify OAuth implementation
│   │   ├── youtube.py        # YouTube OAuth implementation
│   │   ├── callback.py       # OAuth callback handler
│   │   └── types.py          # Authentication data models
│   ├── spotify/              # Spotify API integration
│   │   ├── client.py         # SpotifyAPI client
│   │   └── types.py          # Spotify data models
│   ├── youtube/              # YouTube API integration
│   │   ├── client.py         # YouTubeAPI client
│   │   └── types.py          # YouTube data models
│   ├── transfer/             # Playlist transfer logic
│   │   ├── executor.py       # TransferExecutor - core transfer logic
│   │   ├── matching.py       # TrackMatcher - fuzzy matching
│   │   ├── playlist.py       # PlaylistManager - playlist operations
│   │   ├── naming.py         # PlaylistNamer - name validation
│   │   └── types.py          # Transfer data models
│   ├── server/               # API endpoints
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── playlists.py      # Playlist management endpoints
│   │   ├── transfer.py       # Transfer operation endpoints
│   │   ├── config.py         # Configuration endpoints
│   │   ├── models.py         # Pydantic request/response models
│   │   └── state.py          # Global application state
│   ├── utils/                # Utility functions
│   │   ├── decorators.py     # Retry, rate limiting decorators
│   │   ├── text.py           # Text processing utilities
│   │   ├── validate.py       # Validation functions
│   │   └── logging.py        # Logging configuration
│   └── cli/                  # Command-line interface
│       ├── core.py           # Main CLI class
│       ├── auth.py           # Authentication commands
│       ├── playlists.py      # Playlist commands
│       ├── transfer.py       # Transfer commands
│       └── parser.py         # Argument parsing
└── config.json               # Application configuration
```

### Authentication Flow

1. **OAuth2 Initiation**: Client requests authentication URL
2. **Browser Redirect**: User authenticates with platform
3. **Callback Handling**: OAuth callback processed by `OAuthCallbackHandler`
4. **Token Exchange**: Authorization code exchanged for access token
5. **Token Storage**: Tokens stored in global state for API calls

### Transfer Process

1. **Playlist Retrieval**: Source playlist fetched via platform API
2. **Track Matching**: `TrackMatcher` performs fuzzy matching between platforms
3. **Target Creation**: `PlaylistManager` creates target playlist
4. **Track Addition**: Matched tracks added to target playlist
5. **Progress Tracking**: Real-time progress updates via WebSocket

### API Endpoints

#### Authentication
- `GET /auth/{platform}/login` - Get OAuth login URL
- `POST /auth/{platform}/callback` - Handle OAuth callback
- `GET /auth/{platform}/status` - Check authentication status

#### Playlists
- `GET /playlists/{platform}` - List user playlists
- `GET /playlists/{platform}/{id}` - Get playlist tracks
- `POST /playlists/{platform}` - Create new playlist

#### Transfer Operations
- `POST /transfer/start` - Start playlist transfer
- `GET /transfer/{id}/progress` - Get transfer progress
- `GET /transfer/{id}/summary` - Get transfer summary
- `DELETE /transfer/{id}` - Cancel transfer

#### Configuration
- `GET /config` - Get current configuration
- `POST /config` - Update configuration

## Frontend Architecture

### Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── StepNav.svelte
│   │   │   ├── SourceSelector.svelte
│   │   │   └── TargetSelector.svelte
│   │   ├── stores/          # State management
│   │   │   ├── transferStore.ts
│   │   │   ├── playlistStore.ts
│   │   │   └── uiStore.ts
│   │   ├── services/        # API service layers
│   │   │   ├── authService.ts
│   │   │   ├── playlistService.ts
│   │   │   └── transferService.ts
│   │   ├── composables/     # Reusable logic functions
│   │   │   ├── useDebounce.ts
│   │   │   ├── useErrorHandling.ts
│   │   │   └── useLoadingStates.ts
│   │   └── types/           # TypeScript definitions
│   │       ├── auth.ts
│   │       ├── playlist.ts
│   │       └── transfer.ts
│   └── routes/
│       ├── components/
│       │   └── TransferWizard.svelte
│       ├── steps/
│       │   ├── ConnectionStep.svelte
│       │   ├── DirectionStep.svelte
│       │   ├── SelectionStep.svelte
│       │   ├── ConfirmationStep.svelte
│       │   ├── ProgressStep.svelte
│       │   └── CompleteStep.svelte
│       └── +page.svelte     # Main application page
└── package.json
```

### State Management

- **Svelte Stores**: Reactive state management using Svelte's built-in stores
- **Transfer Store**: Manages transfer state, progress, and results
- **Playlist Store**: Handles playlist data and filtering
- **UI Store**: Manages general UI state and notifications

### Component Architecture

- **Step-based UI**: Transfer process broken into discrete steps
- **Reusable Components**: Shared components for common UI patterns
- **Service Layer**: API calls abstracted into service classes
- **Composables**: Reusable logic functions for common operations

## Desktop Application Architecture

### Tauri Structure

```
tauri/
├── src/
│   ├── commands/             # Tauri commands
│   │   ├── system.rs         # System operations
│   │   └── mod.rs           # Command module exports
│   ├── backend/              # Backend management
│   │   └── mod.rs           # Backend process handling
│   ├── utils/                # Utility functions
│   │   └── mod.rs           # Utility module exports
│   └── main.rs               # Application entry point
├── icons/                    # Application icons
├── tauri.conf.json          # Tauri configuration
└── Cargo.toml               # Rust dependencies
```

### Desktop Integration

- **Sidecar Process**: Backend runs as separate process
- **Window Management**: Native window controls and configuration
- **System Integration**: File system access and system notifications
- **Icon Management**: Multi-resolution icon support

## Data Flow

### Transfer Process Flow

1. **Authentication**: User authenticates with both platforms
2. **Playlist Selection**: User selects source and target playlists
3. **Transfer Initiation**: Frontend sends transfer request to backend
4. **Track Retrieval**: Backend fetches tracks from source platform
5. **Matching Process**: Tracks matched between platforms using fuzzy logic
6. **Target Creation**: Target playlist created on destination platform
7. **Track Addition**: Matched tracks added to target playlist
8. **Progress Updates**: Real-time progress sent to frontend
9. **Completion**: Transfer summary returned to user

### API Communication

- **REST API**: HTTP-based communication between frontend and backend
- **WebSocket**: Real-time progress updates during transfers
- **CORS**: Cross-origin resource sharing configured for development
- **Error Handling**: Standardized error responses with appropriate HTTP codes

## Configuration

### Backend Configuration

```json
{
  "spotify": {
    "client_id": "string",
    "client_secret": "string",
    "redirect_uri": "string"
  },
  "youtube": {
    "api_key": "string"
  },
  "app": {
    "debug": "boolean",
    "log_level": "string"
  }
}
```

### Tauri Configuration

- **Window Settings**: Size, position, and behavior configuration
- **Security**: CSP policies and allowed origins
- **Build Settings**: Target platforms and build options
- **Icon Configuration**: Multi-resolution icon support

## Build and Deployment

### Development

- **Backend**: `python -m uvicorn main:app --reload`
- **Frontend**: `npm run dev`
- **Tauri**: `npm run tauri dev`

### Production

- **Backend**: PyInstaller executable with embedded dependencies
- **Frontend**: Static build output
- **Tauri**: Native desktop application with bundled backend

### Build Process

1. **Backend Compilation**: Python code compiled to executable
2. **Frontend Build**: SvelteKit application built to static files
3. **Tauri Build**: Rust application compiled with embedded frontend
4. **Asset Bundling**: Icons and resources bundled with application

## Security Considerations

- **OAuth2 Flow**: Secure authentication without storing credentials
- **Token Management**: Access tokens stored in memory only
- **CORS Configuration**: Restricted cross-origin access
- **Input Validation**: All inputs validated and sanitized
- **Error Handling**: Sensitive information not exposed in error messages
