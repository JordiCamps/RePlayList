# Quick Start Guide

Get RePlayList up and running in 5 minutes! This guide will help you transfer your first playlist.

## ⚡ 5-Minute Setup

### Step 1: Install RePlayList
```bash
git clone https://github.com/Ahmet-Ozbay/RePlayList.git
cd RePlayList
pip install -r requirements.txt
cd frontend && npm install && cd ..
cd tauri && npm install && cd ..
```

### Step 2: Configure APIs
```bash
cp config.example.json config.json
# Edit config.json with your API credentials
```

**Need API credentials?** See [API Setup](API-Setup) for detailed instructions.

### Step 3: Run the Desktop App
```bash
npm run dev:tauri
```

## 🎵 Your First Transfer

### Using the Desktop App

1. **Launch RePlayList**
   - The app will open in your browser
   - You'll see the transfer wizard

2. **Connect Your Accounts**
   - Click "Connect Spotify" and authorize
   - Click "Connect YouTube" and authorize
   - Both platforms will show as "Connected"

3. **Select Transfer Direction**
   - Choose "Spotify → YouTube" or "YouTube → Spotify"
   - Click "Next"

4. **Choose Source Playlist**
   - Browse your playlists
   - Select the playlist you want to transfer
   - Click "Next"

5. **Choose Target Playlist**
   - Select existing playlist or create new one
   - Enter name for new playlist (if creating)
   - Click "Next"

6. **Review and Transfer**
   - Review your selections
   - Click "Start Transfer"
   - Watch the progress bar

7. **Complete!**
   - View transfer summary
   - Check your target platform for the new playlist

### Using the Command Line

```bash
# List your playlists
python cli.py playlists list --platform spotify

# Preview a transfer
python cli.py transfer preview --source spotify --playlist "My Playlist"

# Execute transfer
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist"
```

## 🔧 Basic Configuration

### Essential Settings

Edit `config.json`:

```json
{
  "spotify": {
    "client_id": "your_spotify_client_id",
    "client_secret": "your_spotify_client_secret",
    "redirect_uri": "http://127.0.0.1:8888/callback"
  },
  "youtube": {
    "client_id": "your_youtube_client_id",
    "client_secret": "your_youtube_client_secret",
    "redirect_uri": "http://127.0.0.1:8889/callback"
  },
  "app": {
    "debug": false,
    "default_transfer_mode": "new_playlist"
  }
}
```

### Transfer Modes

- **`new_playlist`** - Always create a new playlist (default)
- **`existing_playlist`** - Add to existing playlist
- **`ask`** - Prompt user to choose

## 🎯 Common Use Cases

### Transfer Spotify Playlist to YouTube

1. **Desktop App:**
   - Connect both accounts
   - Select "Spotify → YouTube"
   - Choose your Spotify playlist
   - Create new YouTube playlist
   - Start transfer

2. **CLI:**
   ```bash
   python cli.py transfer start \
     --source spotify \
     --target youtube \
     --playlist "My Spotify Playlist" \
     --target-name "My YouTube Playlist"
   ```

### Transfer YouTube Playlist to Spotify

1. **Desktop App:**
   - Connect both accounts
   - Select "YouTube → Spotify"
   - Choose your YouTube playlist
   - Create new Spotify playlist
   - Start transfer

2. **CLI:**
   ```bash
   python cli.py transfer start \
     --source youtube \
     --target spotify \
     --playlist "My YouTube Playlist" \
     --target-name "My Spotify Playlist"
   ```

## 🔍 Understanding Track Matching

RePlayList uses intelligent matching to find corresponding tracks:

### Matching Process
1. **Exact Match** - Same title and artist
2. **Fuzzy Match** - Similar title and artist (85%+ similarity)
3. **Partial Match** - Title matches, artist is similar
4. **No Match** - Track not found on target platform

### Match Quality Indicators
- ✅ **Perfect Match** - Exact title and artist
- ⚠️ **Good Match** - High similarity (85%+)
- ❌ **No Match** - Track not found

## 📊 Transfer Results

After each transfer, you'll see:

- **Total Tracks** - Number of tracks in source playlist
- **Matched Tracks** - Successfully matched tracks
- **Unmatched Tracks** - Tracks that couldn't be found
- **Transfer Time** - How long the transfer took
- **Success Rate** - Percentage of successful matches

## 🚨 Troubleshooting

### Common Issues

#### "Authentication Failed"
- Check your API credentials in `config.json`
- Ensure redirect URIs match exactly
- Try reconnecting your accounts

#### "No Tracks Found"
- Verify the playlist exists and is public
- Check if you have access to the playlist
- Try refreshing your playlists

#### "Transfer Failed"
- Check your internet connection
- Verify API credentials are correct
- Check the logs for detailed error messages

### Getting Help

- **Logs**: Check console output for error details
- **Debug Mode**: Set `"debug": true` in config.json
- **GitHub Issues**: [Report problems](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- **Discussions**: [Ask questions](https://github.com/Ahmet-Ozbay/RePlayList/discussions)

## 🎉 Success!

You've successfully transferred your first playlist! 

### What's Next?

- **[Desktop Application](Desktop-Application)** - Learn advanced features
- **[CLI Usage](CLI-Usage)** - Master command-line operations
- **[Track Matching](Track-Matching)** - Understand matching algorithms
- **[Performance](Performance)** - Optimize transfer speeds
- **[Contributing](Contributing)** - Help improve RePlayList

---

**Ready for more?** Check out our [User Guides](Home#user-guides) for advanced features! 🚀
