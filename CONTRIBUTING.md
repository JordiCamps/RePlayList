# Contributing to RePlayList

Thank you for your interest in contributing to RePlayList! This guide will help you get started with contributing to our project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## 🤝 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## ⚠️ Important Notice

**This project is not officially affiliated with, endorsed by, or sponsored by Spotify, YouTube, or Google. We are independent developers using their publicly available APIs.**

### Our Pledge

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Node.js** 18+ and npm
- **Python** 3.8+ with pip
- **Rust** (latest stable)
- **Git** for version control
- **Code editor** (VS Code recommended)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/Ahmet-Ozbay/RePlayList.git
   cd replaylist
   ```
3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/Ahmet-Ozbay/RePlayList.git
   ```

## 🛠️ Development Setup

### 1. Install Dependencies

```bash
# Frontend dependencies
cd frontend && npm install && cd ..

# Backend dependencies
cd backend && pip install -r requirements.txt && cd ..

# Tauri dependencies
cd tauri && npm install && cd ..

# Root dependencies
npm install
```

### 2. Environment Configuration

```bash
# Copy example configuration
cp backend/config.example.json backend/config.json

# Edit with your API credentials
# You'll need Spotify and YouTube API keys for testing
```

### 3. Verify Installation

```bash
# Test backend
cd backend && python -m uvicorn main:app --reload
# Should start on http://localhost:8000

# Test frontend
cd frontend && npm run dev
# Should start on http://localhost:3000

# Test Tauri app
cd tauri && npm run tauri dev
# Should open desktop application
```

## 📁 Project Structure

Understanding the project structure is crucial for effective contributions:

```
RePlayList/
├── frontend/                 # SvelteKit frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/   # Reusable UI components
│   │   │   ├── stores/       # State management (Svelte stores)
│   │   │   ├── services/     # API service layers
│   │   │   ├── composables/  # Reusable logic functions
│   │   │   └── types/        # TypeScript type definitions
│   │   └── routes/           # SvelteKit pages and layouts
│   ├── static/               # Static assets
│   └── package.json
├── backend/                  # Python FastAPI backend
│   ├── replaylist/
│   │   ├── auth/            # Authentication modules
│   │   │   ├── manager.py   # AuthManager class
│   │   │   ├── spotify.py   # Spotify OAuth
│   │   │   ├── youtube.py   # YouTube OAuth
│   │   │   └── callback.py  # OAuth callback handler
│   │   ├── spotify/         # Spotify API integration
│   │   │   ├── client.py    # SpotifyAPI class
│   │   │   └── types.py     # Spotify data models
│   │   ├── youtube/         # YouTube API integration
│   │   │   ├── client.py    # YouTubeAPI class
│   │   │   └── types.py     # YouTube data models
│   │   ├── transfer/        # Playlist transfer logic
│   │   │   ├── executor.py  # TransferExecutor
│   │   │   ├── matching.py  # TrackMatcher
│   │   │   └── playlist.py  # PlaylistManager
│   │   ├── server/          # API endpoints
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── playlists.py # Playlist endpoints
│   │   │   └── transfer.py  # Transfer endpoints
│   │   ├── utils/           # Utility functions
│   │   │   ├── decorators.py # Retry, rate limiting decorators
│   │   │   ├── text.py      # Text processing utilities
│   │   │   └── validate.py  # Validation functions
│   │   └── cli/             # Command-line interface
│   │       ├── core.py      # Main CLI class
│   │       ├── auth.py      # Auth commands
│   │       └── transfer.py  # Transfer commands
│   ├── main.py              # FastAPI application entry point
│   └── requirements.txt
├── tauri/                   # Tauri desktop application
│   ├── src/                 # Rust source code
│   │   ├── commands/        # Tauri commands
│   │   ├── backend/         # Backend management
│   │   └── utils/           # Rust utilities
│   ├── icons/               # Application icons
│   └── tauri.conf.json      # Tauri configuration
└── docs/                    # Documentation
    ├── api/                 # API documentation
    ├── architecture/        # Architecture decisions
    └── guides/              # User guides
```

## 📝 Coding Standards

### Python (Backend)

We follow PEP 8 and use modern Python features:

```python
# Use type hints
def transfer_playlist(
    source_playlist: PlaylistInfo,
    target_platform: str
) -> TransferResult:
    """Transfer playlist between platforms.
    
    Args:
        source_playlist: Source playlist information
        target_platform: Target platform identifier
        
    Returns:
        Transfer result with success status and details
    """
    pass

# Use dataclasses for data models
@dataclass
class TransferProgress:
    current: int
    total: int
    status: str
```

**Tools:**
- **Black** for code formatting: `black .`
- **Flake8** for linting: `flake8 .`
- **MyPy** for type checking: `mypy .`
- **Pytest** for testing: `pytest`

### TypeScript/JavaScript (Frontend)

We use modern ES6+ and TypeScript:

```typescript
// Use interfaces for type definitions
interface PlaylistInfo {
  id: string;
  name: string;
  trackCount: number;
  platform: 'spotify' | 'youtube';
}

// Use async/await for promises
async function fetchPlaylists(platform: string): Promise<PlaylistInfo[]> {
  try {
    const response = await api.get(`/playlists/${platform}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch playlists:', error);
    throw error;
  }
}

// Use Svelte stores for state management
export const transferStore = writable<TransferState>({
  status: 'idle',
  progress: 0,
  currentTrack: null
});
```

**Tools:**
- **Prettier** for formatting: `npm run format`
- **ESLint** for linting: `npm run lint`
- **TypeScript** for type checking: `npm run check`
- **Vitest** for testing: `npm run test`

### Rust (Tauri)

We follow Rust conventions and use modern features:

```rust
// Use proper error handling
#[tauri::command]
pub async fn open_auth_window(url: String) -> Result<(), String> {
    match open::that(&url) {
        Ok(_) => Ok(()),
        Err(e) => Err(format!("Failed to open URL: {}", e)),
    }
}

// Use serde for serialization
#[derive(Serialize, Deserialize)]
pub struct AuthResult {
    pub success: bool,
    pub message: String,
}
```

**Tools:**
- **rustfmt** for formatting: `cargo fmt`
- **clippy** for linting: `cargo clippy`
- **cargo check** for compilation: `cargo check`

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=replaylist --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

**Test Structure:**
```python
# tests/test_auth.py
import pytest
from unittest.mock import Mock, patch
from replaylist.auth.manager import AuthManager

class TestAuthManager:
    def test_spotify_auth_success(self):
        """Test successful Spotify authentication."""
        # Arrange
        manager = AuthManager()
        
        # Act
        result = manager.authenticate_spotify()
        
        # Assert
        assert result.success is True
        assert result.access_token is not None
```

### Frontend Testing

```bash
cd frontend

# Run unit tests
npm run test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

**Test Structure:**
```typescript
// tests/services/transferService.test.ts
import { describe, it, expect, vi } from 'vitest';
import { transferService } from '$lib/services/transferService';

describe('TransferService', () => {
  it('should start transfer successfully', async () => {
    // Arrange
    const mockTransfer = { id: 'test-id', status: 'running' };
    vi.spyOn(transferService, 'startTransfer').mockResolvedValue(mockTransfer);
    
    // Act
    const result = await transferService.startTransfer('playlist-id');
    
    // Assert
    expect(result).toEqual(mockTransfer);
  });
});
```

### Integration Testing

```bash
# Test full application flow
npm run test:integration

# Test API endpoints
npm run test:api
```

## 📤 Submitting Changes

### 1. Create a Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 2. Make Your Changes

- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed
- Follow the coding standards

### 3. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add playlist search functionality

- Add search endpoint to API
- Implement search UI component
- Add search tests
- Update documentation

Closes #123"
```

**Commit Message Format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

### 4. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## 🐛 Issue Guidelines

### Before Creating an Issue

1. **Search existing issues** - Check if your issue already exists
2. **Check documentation** - Ensure it's not covered in docs
3. **Try latest version** - Make sure you're using the latest code

### Creating a Good Issue

**Bug Reports:**
```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g. Windows 10]
- Node.js version: [e.g. 18.17.0]
- Python version: [e.g. 3.9.0]
- Browser: [e.g. Chrome 91]

## Additional Context
Any other context about the problem
```

**Feature Requests:**
```markdown
## Feature Description
Brief description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other context or screenshots
```

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] All checks pass

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts

## Screenshots (if applicable)
Add screenshots to help explain your changes

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs tests
2. **Code Review** - Maintainers review code
3. **Testing** - Manual testing if needed
4. **Approval** - At least one maintainer approval required
5. **Merge** - Squash and merge to main branch

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Release Steps

1. **Update version numbers** in package.json, Cargo.toml
2. **Update CHANGELOG.md** with new features/fixes
3. **Create release tag** - `git tag v1.2.0`
4. **Build artifacts** - `npm run build:app`
5. **Create GitHub release** with release notes
6. **Publish to package managers** (if applicable)

## 📚 Additional Resources

### Documentation
- [API Documentation](docs/api/)
- [Architecture Guide](docs/architecture/)
- [User Guides](docs/guides/)

### Communication
- **GitHub Discussions** - General questions and ideas
- **GitHub Issues** - Bug reports and feature requests
- **Discord** - Real-time chat (if available)

### Learning Resources
- [SvelteKit Documentation](https://kit.svelte.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tauri Documentation](https://tauri.app/)
- [Rust Book](https://doc.rust-lang.org/book/)

## 🙏 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** - List of all contributors
- **Release Notes** - Credit for specific contributions
- **GitHub Contributors** - Automatic recognition

---

**Thank you for contributing to RePlayList! Your contributions help make music playlist management better for everyone. 🎵✨**
