# Desktop Application Guide

The RePlayList desktop application provides a beautiful, intuitive interface for transferring playlists between Spotify and YouTube Music.

## 🚀 Getting Started

### Launching the App

```bash
# Development mode
npm run dev:tauri

# Production build
npm run build:app
```

The app will open in a new window with the transfer wizard.

## 🎨 Interface Overview

### Main Window
- **Header** - App title and settings
- **Transfer Wizard** - Step-by-step transfer process
- **Progress Bar** - Shows current step
- **Navigation** - Previous/Next buttons

### Transfer Wizard Steps

1. **Connection Step** - Connect to Spotify and YouTube
2. **Direction Step** - Choose transfer direction
3. **Selection Step** - Select source and target playlists
4. **Confirmation Step** - Review and confirm transfer
5. **Progress Step** - Monitor transfer progress
6. **Complete Step** - View results and summary

## 🔗 Connecting Accounts

### Spotify Connection

1. **Click "Connect Spotify"**
2. **Authorize in browser**
   - You'll be redirected to Spotify
   - Log in with your Spotify account
   - Grant permissions to RePlayList
3. **Return to app**
   - Connection status will show "Connected"
   - Your Spotify playlists will load

### YouTube Connection

1. **Click "Connect YouTube"**
2. **Authorize in browser**
   - You'll be redirected to Google
   - Log in with your Google account
   - Grant permissions to RePlayList
3. **Return to app**
   - Connection status will show "Connected"
   - Your YouTube playlists will load

### Connection Issues

- **"Authentication Failed"** - Check API credentials
- **"Permission Denied"** - Grant required permissions
- **"Network Error"** - Check internet connection

## 🎵 Transfer Process

### Step 1: Choose Direction

Select the transfer direction:
- **Spotify → YouTube** - Transfer from Spotify to YouTube Music
- **YouTube → Spotify** - Transfer from YouTube Music to Spotify

### Step 2: Select Source Playlist

**Browse Playlists:**
- Use search to find specific playlists
- Filter by playlist type (public, private, collaborative)
- Sort by name, date, or track count

**Playlist Information:**
- **Name** - Playlist title
- **Owner** - Playlist creator
- **Track Count** - Number of tracks
- **Last Modified** - When playlist was updated

### Step 3: Choose Target Playlist

**Create New Playlist:**
- Enter playlist name
- Add description (optional)
- Set privacy (public, private, unlisted)

**Use Existing Playlist:**
- Browse your existing playlists
- Select target playlist
- Choose to replace or append tracks

### Step 4: Review Transfer

**Transfer Summary:**
- Source playlist details
- Target playlist details
- Estimated transfer time
- Track count and matching preview

**Advanced Options:**
- **Transfer Mode** - New playlist or existing
- **Duplicate Handling** - Skip or add duplicates
- **Match Threshold** - Similarity threshold for matching

### Step 5: Monitor Progress

**Progress Indicators:**
- **Overall Progress** - Transfer completion percentage
- **Current Track** - Currently processing track
- **Matches Found** - Successfully matched tracks
- **Errors** - Failed matches or errors

**Real-time Updates:**
- Track-by-track progress
- Match quality indicators
- Error notifications
- Time estimates

### Step 6: View Results

**Transfer Summary:**
- **Total Tracks** - Source playlist track count
- **Matched Tracks** - Successfully transferred tracks
- **Unmatched Tracks** - Tracks that couldn't be found
- **Success Rate** - Percentage of successful matches
- **Transfer Time** - Total time taken

**Detailed Results:**
- **Perfect Matches** - Exact title and artist matches
- **Good Matches** - High similarity matches
- **Partial Matches** - Title matches, artist differs
- **No Matches** - Tracks not found on target platform

## ⚙️ Settings and Configuration

### App Settings

Access settings via the gear icon in the header:

**General:**
- **Default Transfer Mode** - New playlist or existing
- **Match Threshold** - Similarity threshold (70-95%)
- **Duplicate Handling** - Skip or add duplicates
- **Auto-refresh** - Refresh playlists automatically

**Display:**
- **Theme** - Light or dark mode
- **Language** - Interface language
- **Font Size** - Text size preference
- **Animations** - Enable/disable animations

**Advanced:**
- **Debug Mode** - Show detailed logs
- **Log Level** - Error, warning, info, debug
- **Cache Size** - Playlist cache size
- **API Timeout** - Request timeout duration

### Keyboard Shortcuts

- **Ctrl+N** - New transfer
- **Ctrl+R** - Refresh playlists
- **Ctrl+S** - Settings
- **Ctrl+Q** - Quit application
- **F5** - Refresh current view
- **Esc** - Cancel current operation

## 🔍 Playlist Management

### Refreshing Playlists

**Manual Refresh:**
- Click the refresh button
- Use Ctrl+R shortcut
- Right-click in playlist list

**Auto-refresh:**
- Enable in settings
- Refreshes every 5 minutes
- Pauses during transfers

### Playlist Information

**View Details:**
- Click on playlist name
- See track list and metadata
- View playlist statistics

**Search and Filter:**
- Search by name or description
- Filter by playlist type
- Sort by various criteria

## 🚨 Error Handling

### Common Errors

**Authentication Errors:**
- **"Invalid Credentials"** - Check API configuration
- **"Token Expired"** - Reconnect your accounts
- **"Permission Denied"** - Grant required permissions

**Transfer Errors:**
- **"Playlist Not Found"** - Verify playlist exists
- **"Network Error"** - Check internet connection
- **"API Rate Limit"** - Wait and retry

**Matching Errors:**
- **"No Matches Found"** - Lower match threshold
- **"Ambiguous Match"** - Review match suggestions
- **"Invalid Track"** - Skip problematic tracks

### Error Recovery

**Automatic Recovery:**
- Retry failed requests
- Skip problematic tracks
- Continue with partial matches

**Manual Recovery:**
- Review error logs
- Adjust settings
- Retry specific tracks

## 📊 Performance Optimization

### Transfer Speed

**Factors Affecting Speed:**
- **Playlist Size** - Larger playlists take longer
- **Match Complexity** - Complex matching is slower
- **Network Speed** - Faster internet = faster transfers
- **API Rate Limits** - Respect platform limits

**Optimization Tips:**
- Use higher match thresholds
- Enable parallel processing
- Cache playlist data
- Optimize network settings

### Memory Usage

**Memory Management:**
- Playlist data is cached in memory
- Large playlists use more memory
- Cache is cleared after transfer
- Monitor memory usage in settings

## 🎯 Advanced Features

### Batch Transfers

**Multiple Playlists:**
- Select multiple source playlists
- Transfer to single target playlist
- Or create separate target playlists

**Scheduled Transfers:**
- Set up recurring transfers
- Transfer playlists at specific times
- Monitor transfer history

### Custom Matching

**Match Rules:**
- Set custom similarity thresholds
- Define matching criteria
- Exclude certain track types
- Prioritize specific attributes

**Manual Matching:**
- Review automatic matches
- Manually select correct matches
- Override automatic decisions
- Save custom match rules

## 🔧 Troubleshooting

### App Won't Start

1. **Check Dependencies:**
   ```bash
   npm run tauri dev
   ```

2. **Clear Cache:**
   - Delete `~/.replaylist/cache`
   - Restart application

3. **Check Logs:**
   - Enable debug mode
   - Check console output
   - Review error messages

### Performance Issues

1. **Reduce Memory Usage:**
   - Lower cache size
   - Process smaller playlists
   - Close other applications

2. **Optimize Network:**
   - Use wired connection
   - Close bandwidth-heavy apps
   - Check firewall settings

3. **Update Dependencies:**
   - Update Node.js
   - Update Rust
   - Reinstall dependencies

### Getting Help

- **GitHub Issues** - [Report bugs](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- **Discussions** - [Ask questions](https://github.com/Ahmet-Ozbay/RePlayList/discussions)
- **Documentation** - Check other wiki pages
- **Logs** - Enable debug mode for detailed information

---

**Ready to transfer playlists?** Check out our [Quick Start Guide](Quick-Start) to get started! 🎵
