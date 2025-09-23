#!/usr/bin/env python3
"""
Build script for RePlayList Desktop Application (Tauri).
This script builds the complete desktop application with embedded backend.
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
    print("🚀 Building RePlayList Desktop Application")
    print("=" * 50)
    
    # Step 1: Build frontend
    print("\n📦 Step 1: Building frontend...")
    if not run_command("npm run build", cwd="frontend"):
        print("❌ Frontend build failed!")
        return False
    
    # Step 2: Build backend executable
    print("\n⚙️  Step 2: Building backend executable...")
    if not run_command("pip install pyinstaller"):
        print("❌ Failed to install PyInstaller!")
        return False
    
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    if not run_command("pyinstaller backend/pyinstaller.spec --noconfirm"):
        print("❌ Backend build failed!")
        return False
    
    # Step 3: Copy backend executable to Tauri
    print("\n📁 Step 3: Copying backend to Tauri...")
    tauri_binaries = Path("tauri/binaries")
    tauri_binaries.mkdir(exist_ok=True)
    
    # Copy the executable
    backend_exe = Path("dist/replaylist-backend/replaylist-backend.exe")
    if backend_exe.exists():
        shutil.copy2(backend_exe, tauri_binaries / "replaylist-backend.exe")
        print("✅ Backend executable copied to Tauri")
    else:
        print("❌ Backend executable not found!")
        return False
    
    # Step 4: Install Tauri dependencies
    print("\n🔧 Step 4: Installing Tauri dependencies...")
    if not run_command("npm install", cwd="tauri"):
        print("❌ Tauri dependencies installation failed!")
        return False
    
    # Step 5: Build Tauri desktop app
    print("\n🖥️  Step 5: Building Tauri desktop application...")
    if not run_command("npm run tauri build", cwd="tauri"):
        print("❌ Tauri build failed!")
        return False
    
    # Step 6: Create release package
    print("\n📦 Step 6: Creating release package...")
    
    # Find the built Tauri app
    tauri_dist = Path("tauri/target/release/bundle")
    if not tauri_dist.exists():
        print("❌ Tauri build output not found!")
        return False
    
    # Look for the MSI installer
    msi_files = list(tauri_dist.glob("**/*.msi"))
    if not msi_files:
        print("❌ MSI installer not found!")
        return False
    
    msi_file = msi_files[0]
    print(f"✅ Found MSI installer: {msi_file.name}")
    
    # Create release directory
    release_dir = Path("release-desktop")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy MSI installer
    release_msi = release_dir / "RePlayList-Setup.msi"
    shutil.copy2(msi_file, release_msi)
    print(f"✅ Copied installer to {release_msi}")
    
    # Copy example config
    config_example = release_dir / "config.example.json"
    shutil.copy2("config.example.json", config_example)
    print("✅ Copied example config")
    
    # Create README for release
    readme_content = """# RePlayList - Desktop Application

## Installation

1. **Run the installer:**
   - Double-click `RePlayList-Setup.msi`
   - Follow the installation wizard
   - The app will be installed to your Programs folder

2. **Configure API credentials:**
   - Copy `config.example.json` to the installation directory
   - Rename it to `config.json`
   - Edit `config.json` with your Spotify and YouTube API credentials
   - See [API Setup Guide](https://github.com/Ahmet-Ozbay/RePlayList/wiki/API-Setup) for detailed instructions

3. **Run the application:**
   - Find "RePlayList" in your Start Menu
   - Or run from the installation directory
   - The desktop app will open automatically

## What's Included

- **Desktop Application** - Native Windows app with embedded backend
- **Web Interface** - Modern UI accessible within the app
- **Backend Server** - Embedded Python server (no separate installation needed)
- **Example Config** - Template for API credentials

## Features

- **Cross-Platform Playlist Transfer** - Move playlists between Spotify and YouTube Music
- **Smart Track Matching** - Intelligent fuzzy matching with duplicate detection
- **Native Desktop App** - No browser required, runs as a desktop application
- **Offline Capable** - Once configured, works without internet (except for API calls)

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

---

**Made with ❤️ for music lovers who want to keep their playlists in sync across platforms.**
"""
    
    with open(release_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("✅ Created release README")
    
    # Step 7: Create ZIP package
    print("\n📦 Step 7: Creating ZIP package...")
    import zipfile
    
    zip_path = "RePlayList-Desktop-Windows.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(release_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, release_dir)
                zipf.write(file_path, arc_path)
    
    print(f"✅ Created {zip_path}")
    
    # Step 8: Show results
    print("\n🎉 Desktop Application Build Complete!")
    print("=" * 50)
    print(f"📁 Release directory: {release_dir.absolute()}")
    print(f"📦 ZIP package: {zip_path}")
    print(f"📊 Package size: {os.path.getsize(zip_path) / (1024*1024):.1f} MB")
    print(f"🖥️  MSI installer: {release_msi}")
    print("\n📋 Next steps:")
    print("1. Test the MSI installer")
    print("2. Upload the ZIP file to GitHub Releases")
    print("3. Users can install the desktop app directly")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
