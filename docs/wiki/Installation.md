# Installation Guide

This guide will walk you through installing RePlayList on your system.

## 📋 Prerequisites

Before installing RePlayList, ensure you have:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **Rust** (for desktop app) - [Install Rust](https://rustup.rs/)
- **Git** - [Download Git](https://git-scm.com/)

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.15, or Ubuntu 18.04+
- **RAM**: 4GB
- **Storage**: 500MB free space
- **Network**: Internet connection for API access

### Recommended Requirements
- **OS**: Windows 11, macOS 12+, or Ubuntu 20.04+
- **RAM**: 8GB
- **Storage**: 1GB free space
- **Network**: Stable broadband connection

## 🚀 Installation Methods

### Method 1: From Source (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ahmet-Ozbay/RePlayList.git
   cd RePlayList
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   # Frontend
   cd frontend && npm install && cd ..
   
   # Tauri
   cd tauri && npm install && cd ..
   ```

4. **Install Rust dependencies:**
   ```bash
   cd tauri
   cargo build
   cd ..
   ```

### Method 2: Using pip (Backend only)

```bash
pip install replaylist
```

### Method 3: Pre-built Binaries (Coming Soon)

Download pre-built binaries from the [Releases page](https://github.com/Ahmet-Ozbay/RePlayList/releases).

## ⚙️ Configuration

1. **Copy the example configuration:**
   ```bash
   cp config.example.json config.json
   ```

2. **Edit the configuration:**
   ```bash
   # Using your preferred editor
   nano config.json
   # or
   code config.json
   ```

3. **Add your API credentials:**
   - See [API Setup](API-Setup) for detailed instructions
   - Configure Spotify and YouTube API keys

## 🧪 Verify Installation

### Test Backend
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Test Frontend
```bash
cd frontend
npm run dev
```

### Test Desktop App
```bash
cd tauri
npm run tauri dev
```

## 🔧 Platform-Specific Instructions

### Windows

1. **Install Python:**
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. **Install Node.js:**
   - Download from [nodejs.org](https://nodejs.org/)
   - Use the LTS version

3. **Install Rust:**
   ```powershell
   # Run in PowerShell
   Invoke-WebRequest -Uri "https://win.rustup.rs/" -OutFile "rustup-init.exe"
   .\rustup-init.exe
   ```

### macOS

1. **Install using Homebrew:**
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install dependencies
   brew install python node rust git
   ```

2. **Or use official installers:**
   - Python: [python.org](https://www.python.org/downloads/)
   - Node.js: [nodejs.org](https://nodejs.org/)
   - Rust: [rustup.rs](https://rustup.rs/)

### Linux (Ubuntu/Debian)

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nodejs npm git curl
   
   # Install Rust
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source ~/.cargo/env
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

## 🐛 Troubleshooting

### Common Issues

#### Python not found
```bash
# Windows
python --version
# If not found, reinstall Python and check "Add to PATH"

# macOS/Linux
python3 --version
# Use python3 instead of python
```

#### Node.js version issues
```bash
# Check version
node --version
# Should be 18.0.0 or higher

# Update if needed
npm install -g n
n latest
```

#### Rust installation issues
```bash
# Check installation
rustc --version
cargo --version

# Reinstall if needed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Permission errors
```bash
# Linux/macOS
sudo chown -R $USER:$USER ~/.npm
sudo chown -R $USER:$USER ~/.cargo

# Windows - Run as Administrator
```

### Getting Help

- Check the [Troubleshooting](Troubleshooting) page
- Search [GitHub Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- Join our [Discussions](https://github.com/Ahmet-Ozbay/RePlayList/discussions)

## ✅ Next Steps

After successful installation:

1. **[Configure APIs](API-Setup)** - Set up Spotify and YouTube credentials
2. **[Quick Start](Quick-Start)** - Run your first playlist transfer
3. **[Desktop App](Desktop-Application)** - Use the graphical interface
4. **[CLI Usage](CLI-Usage)** - Learn command-line operations

---

*Installation complete! Ready to transfer playlists?* 🎵
