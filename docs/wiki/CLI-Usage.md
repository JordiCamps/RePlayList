# CLI Usage Guide

The RePlayList command-line interface provides powerful tools for playlist management and transfer operations.

## 🚀 Getting Started

### Basic Usage

```bash
# Show help
python cli.py --help

# Show version
python cli.py --version

# Show configuration
python cli.py config show
```

### Installation

```bash
# Install from source
git clone https://github.com/Ahmet-Ozbay/RePlayList.git
cd RePlayList
pip install -r requirements.txt

# Or install via pip
pip install replaylist
```

## 🔐 Authentication

### Login to Platforms

```bash
# Login to Spotify
python cli.py auth login --platform spotify

# Login to YouTube
python cli.py auth login --platform youtube

# Login to both platforms
python cli.py auth login --platform all
```

### Check Authentication Status

```bash
# Check all platforms
python cli.py auth status

# Check specific platform
python cli.py auth status --platform spotify
```

### Logout

```bash
# Logout from platform
python cli.py auth logout --platform spotify

# Logout from all platforms
python cli.py auth logout --platform all
```

## 📋 Playlist Management

### List Playlists

```bash
# List all playlists
python cli.py playlists list

# List Spotify playlists
python cli.py playlists list --platform spotify

# List YouTube playlists
python cli.py playlists list --platform youtube

# Filter by name
python cli.py playlists list --name "My Playlist"

# Show detailed information
python cli.py playlists list --verbose
```

### View Playlist Details

```bash
# Show playlist tracks
python cli.py playlists show --platform spotify --playlist "My Playlist"

# Show with track details
python cli.py playlists show --platform spotify --playlist "My Playlist" --verbose

# Export playlist to file
python cli.py playlists show --platform spotify --playlist "My Playlist" --export playlist.json
```

### Create Playlists

```bash
# Create new playlist
python cli.py playlists create --platform spotify --name "New Playlist" --description "My new playlist"

# Create with tracks
python cli.py playlists create --platform spotify --name "New Playlist" --tracks "track1,track2,track3"
```

## 🔄 Transfer Operations

### Preview Transfer

```bash
# Preview transfer
python cli.py transfer preview --source spotify --target youtube --playlist "My Playlist"

# Preview with detailed matching
python cli.py transfer preview --source spotify --target youtube --playlist "My Playlist" --verbose

# Preview with custom settings
python cli.py transfer preview --source spotify --target youtube --playlist "My Playlist" --threshold 0.8
```

### Execute Transfer

```bash
# Basic transfer
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist"

# Transfer with custom target name
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist" --target-name "My YouTube Playlist"

# Transfer to existing playlist
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist" --target-playlist "Existing Playlist"

# Transfer with custom settings
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist" --threshold 0.8 --mode append
```

### Transfer Modes

- **`new_playlist`** - Create new playlist (default)
- **`existing_playlist`** - Add to existing playlist
- **`append`** - Append to existing playlist
- **`replace`** - Replace existing playlist content

### Monitor Transfer

```bash
# Show transfer status
python cli.py transfer status --transfer-id <id>

# List all transfers
python cli.py transfer list

# Show transfer history
python cli.py transfer history
```

## 🔍 Search Operations

### Search Tracks

```bash
# Search for tracks
python cli.py search tracks --platform spotify --query "artist:Beatles song:Hey Jude"

# Search with filters
python cli.py search tracks --platform spotify --query "rock" --year 2020 --limit 10

# Search on both platforms
python cli.py search tracks --platform all --query "My Song"
```

### Search Playlists

```bash
# Search playlists
python cli.py search playlists --platform spotify --query "rock music"

# Search public playlists
python cli.py search playlists --platform spotify --query "rock" --public
```

## ⚙️ Configuration

### Show Configuration

```bash
# Show current configuration
python cli.py config show

# Show specific section
python cli.py config show --section spotify
```

### Update Configuration

```bash
# Update configuration value
python cli.py config set --key "app.debug" --value "true"

# Update multiple values
python cli.py config set --key "app.debug" --value "true" --key "app.log_level" --value "debug"
```

### Reset Configuration

```bash
# Reset to defaults
python cli.py config reset

# Reset specific section
python cli.py config reset --section app
```

## 📊 Advanced Features

### Batch Operations

```bash
# Transfer multiple playlists
python cli.py transfer batch --source spotify --target youtube --playlists "Playlist1,Playlist2,Playlist3"

# Batch with custom settings
python cli.py transfer batch --source spotify --target youtube --playlists "Playlist1,Playlist2" --threshold 0.8 --mode new_playlist
```

### Export/Import

```bash
# Export playlists
python cli.py playlists export --platform spotify --output playlists.json

# Import playlists
python cli.py playlists import --platform youtube --input playlists.json
```

### Backup and Restore

```bash
# Backup all playlists
python cli.py backup create --output backup.json

# Restore from backup
python cli.py backup restore --input backup.json
```

## 🔧 Command Options

### Global Options

- **`--config`** - Path to configuration file
- **`--verbose`** - Enable verbose output
- **`--debug`** - Enable debug mode
- **`--quiet`** - Suppress output
- **`--json`** - Output in JSON format
- **`--csv`** - Output in CSV format

### Platform Options

- **`--platform`** - Target platform (spotify, youtube, all)
- **`--source`** - Source platform for transfers
- **`--target`** - Target platform for transfers

### Transfer Options

- **`--playlist`** - Playlist name or ID
- **`--target-name`** - Target playlist name
- **`--target-playlist`** - Existing target playlist
- **`--threshold`** - Match threshold (0.0-1.0)
- **`--mode`** - Transfer mode
- **`--limit`** - Maximum number of tracks

## 📝 Output Formats

### JSON Output

```bash
# Get JSON output
python cli.py playlists list --json

# Pretty print JSON
python cli.py playlists list --json | python -m json.tool
```

### CSV Output

```bash
# Get CSV output
python cli.py playlists list --csv

# Save to file
python cli.py playlists list --csv --output playlists.csv
```

### Table Output

```bash
# Default table output
python cli.py playlists list

# Custom table format
python cli.py playlists list --format "name,owner,tracks,modified"
```

## 🚨 Error Handling

### Common Errors

**Authentication Errors:**
```bash
# Re-authenticate
python cli.py auth login --platform spotify

# Check credentials
python cli.py config show --section spotify
```

**Network Errors:**
```bash
# Check connection
python cli.py auth status

# Retry with debug
python cli.py --debug playlists list
```

**Permission Errors:**
```bash
# Check file permissions
ls -la config.json

# Fix permissions
chmod 600 config.json
```

### Debug Mode

```bash
# Enable debug mode
python cli.py --debug playlists list

# Show detailed logs
python cli.py --debug --verbose transfer start --source spotify --target youtube --playlist "My Playlist"
```

## 📚 Examples

### Complete Workflow

```bash
# 1. Login to platforms
python cli.py auth login --platform all

# 2. List playlists
python cli.py playlists list --platform spotify

# 3. Preview transfer
python cli.py transfer preview --source spotify --target youtube --playlist "My Playlist"

# 4. Execute transfer
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist" --target-name "My YouTube Playlist"

# 5. Check results
python cli.py playlists show --platform youtube --playlist "My YouTube Playlist"
```

### Batch Transfer

```bash
# Transfer multiple playlists
python cli.py transfer batch --source spotify --target youtube --playlists "Rock,Pop,Jazz" --mode new_playlist
```

### Backup and Restore

```bash
# Backup all playlists
python cli.py backup create --output backup_$(date +%Y%m%d).json

# Restore from backup
python cli.py backup restore --input backup_20231201.json
```

## 🔧 Troubleshooting

### Common Issues

**Command not found:**
```bash
# Check Python path
which python
python --version

# Install dependencies
pip install -r requirements.txt
```

**Permission denied:**
```bash
# Check file permissions
ls -la cli.py

# Fix permissions
chmod +x cli.py
```

**Configuration errors:**
```bash
# Validate configuration
python cli.py config validate

# Reset configuration
python cli.py config reset
```

### Getting Help

- **Help command**: `python cli.py --help`
- **Command help**: `python cli.py <command> --help`
- **GitHub Issues**: [Report problems](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- **Discussions**: [Ask questions](https://github.com/Ahmet-Ozbay/RePlayList/discussions)

---

**Ready to use the CLI?** Check out our [Quick Start Guide](Quick-Start) for a complete walkthrough! 🚀
