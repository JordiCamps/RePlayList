#!/usr/bin/env python3
"""
Build script for RePlayList Windows executable.
This script builds both the backend executable and prepares the release package.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ Success: {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build process."""
    print("🚀 Building RePlayList Windows Executable")
    print("=" * 50)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("⚠️  Warning: This script is designed for Windows builds")
        print("   You can still run it, but the executable will be for the current platform")
    
    # Step 1: Build frontend
    print("\n📦 Step 1: Building frontend...")
    if not run_command("npm run build", cwd="frontend"):
        print("❌ Frontend build failed!")
        return False
    
    # Step 2: Install PyInstaller if not present
    print("\n🔧 Step 2: Installing PyInstaller...")
    if not run_command("pip install pyinstaller"):
        print("❌ Failed to install PyInstaller!")
        return False
    
    # Step 3: Clean previous builds
    print("\n🧹 Step 3: Cleaning previous builds...")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Step 4: Build backend executable
    print("\n⚙️  Step 4: Building backend executable...")
    if not run_command("pyinstaller backend/pyinstaller.spec --noconfirm"):
        print("❌ Backend build failed!")
        return False
    
    # Step 5: Create release package
    print("\n📁 Step 5: Creating release package...")
    
    # Create release directory
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable and dependencies
    exe_dir = Path("dist/replaylist-backend")
    if exe_dir.exists():
        shutil.copytree(exe_dir, release_dir / "replaylist-backend")
        print("✅ Copied executable and dependencies")
    else:
        print("❌ Executable directory not found!")
        return False
    
    # Copy frontend build
    frontend_build = Path("frontend/build")
    if frontend_build.exists():
        shutil.copytree(frontend_build, release_dir / "frontend")
        print("✅ Copied frontend build")
    else:
        print("❌ Frontend build not found!")
        return False
    
    # Create example config
    config_example = release_dir / "config.example.json"
    with open(config_example, "w") as f:
        f.write("""{
  "spotify": {
    "client_id": "your_spotify_client_id_here",
    "client_secret": "your_spotify_client_secret_here",
    "redirect_uri": "http://127.0.0.1:8888/callback"
  },
  "youtube": {
    "client_id": "your_youtube_client_id_here",
    "client_secret": "your_youtube_client_secret_here",
    "redirect_uri": "http://127.0.0.1:8889/callback"
  },
  "app": {
    "debug": false,
    "default_transfer_mode": "new_playlist",
    "http_port": 5000,
    "log_level": "INFO"
  }
}""")
    print("✅ Created example config file")
    
    # Create README for release
    readme_content = """# RePlayList - Windows Release

## Quick Start

1. **Configure API credentials:**
   - Copy `config.example.json` to `config.json`
   - Edit `config.json` with your Spotify and YouTube API credentials
   - See [API Setup Guide](https://github.com/Ahmet-Ozbay/RePlayList/wiki/API-Setup) for detailed instructions

2. **Run the application:**
   - Double-click `replaylist-backend.exe` to start the backend server
   - Open your browser and go to `http://localhost:5000`
   - The frontend will load automatically

## What's Included

- `replaylist-backend.exe` - Main application executable
- `frontend/` - Web interface files
- `config.example.json` - Example configuration file
- All necessary dependencies and libraries

## Requirements

- Windows 10 or later
- Internet connection for API access
- Spotify and YouTube API credentials

## Getting Help

- [GitHub Repository](https://github.com/Ahmet-Ozbay/RePlayList)
- [Documentation](https://github.com/Ahmet-Ozbay/RePlayList/wiki)
- [Report Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)

## License

MIT License - see [LICENSE](https://github.com/Ahmet-Ozbay/RePlayList/blob/main/LICENSE) for details.
"""
    
    with open(release_dir / "README.txt", "w") as f:
        f.write(readme_content)
    print("✅ Created release README")
    
    # Create batch file to run the application
    batch_content = """@echo off
echo Starting RePlayList...
echo.
echo Make sure you have configured config.json with your API credentials!
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak > nul
start http://localhost:5000
echo.
echo Starting backend server...
replaylist-backend.exe
pause
"""
    
    with open(release_dir / "start-replaylist.bat", "w") as f:
        f.write(batch_content)
    print("✅ Created start script")
    
    # Step 6: Create ZIP package
    print("\n📦 Step 6: Creating ZIP package...")
    import zipfile
    
    zip_path = "RePlayList-Windows.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, arc_path)
    
    print(f"✅ Created {zip_path}")
    
    # Step 7: Show results
    print("\n🎉 Build Complete!")
    print("=" * 50)
    print(f"📁 Release directory: {release_dir.absolute()}")
    print(f"📦 ZIP package: {zip_path}")
    print(f"📊 Package size: {os.path.getsize(zip_path) / (1024*1024):.1f} MB")
    print("\n📋 Next steps:")
    print("1. Test the executable in the release directory")
    print("2. Upload the ZIP file to GitHub Releases")
    print("3. Update the release notes with installation instructions")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
