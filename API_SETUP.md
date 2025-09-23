# API Setup Guide

This guide provides detailed instructions for setting up API credentials for both Spotify and YouTube Music.

## 📋 Prerequisites

Before setting up API credentials, ensure you have:
- A Spotify account
- A Google account
- Access to both platforms' developer consoles

## 🎵 Spotify API Setup

### Step 1: Create a Spotify App

1. **Go to Spotify Developer Dashboard**
   - Visit [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
   - Log in with your Spotify account

2. **Create a New App**
   - Click "Create an App"
   - Fill in the required information:
     - **App name**: `RePlayList` (or your preferred name)
     - **App description**: `Playlist transfer application`
     - **Website**: `https://github.com/Ahmet-Ozbay/RePlayList` (optional)
     - **Redirect URI**: `http://127.0.0.1:8888/callback`
     - **API/SDKs**: Check "Web API"
   - Click "Save"

3. **Get Your Credentials**
   - After creating the app, you'll see your app dashboard
   - Click "Settings" (gear icon)
   - Copy your **Client ID** and **Client Secret**

### Step 2: Configure Redirect URIs

1. **Add Redirect URIs**
   - In your app settings, scroll to "Redirect URIs"
   - Add the following URIs:
     - `http://127.0.0.1:8888/callback`
     - `http://localhost:8888/callback`
   - Click "Add" for each URI
   - Click "Save"

### Step 3: Update Configuration

Add your Spotify credentials to `config.json`:

```json
{
  "spotify": {
    "client_id": "your_spotify_client_id_here",
    "client_secret": "your_spotify_client_secret_here",
    "redirect_uri": "http://127.0.0.1:8888/callback"
  }
}
```

## 🎬 YouTube Music API Setup

**⚠️ Important:** YouTube Music API requires additional setup steps as it's not a publicly available API. This guide covers the YouTube Data API v3 workaround.

### Step 1: Create a Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Log in with your Google account

2. **Create a New Project**
   - Click "Select a project" → "New Project"
   - Enter project name: `RePlayList` (or your preferred name)
   - Click "Create"

### Step 2: Enable YouTube Data API v3

1. **Navigate to APIs & Services**
   - In the Google Cloud Console, go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click on it and then click "Enable"

2. **Create Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

### Step 3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - In "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Click "Create"

2. **Fill in App Information**
   - **App name**: `RePlayList`
   - **User support email**: Your email
   - **Developer contact information**: Your email
   - Click "Save and Continue"

3. **Add Scopes**
   - Click "Add or Remove Scopes"
   - Add these scopes:
     - `https://www.googleapis.com/auth/youtube.readonly`
     - `https://www.googleapis.com/auth/youtube.force-ssl`
   - Click "Update" → "Save and Continue"

4. **Add Test Users**
   - Add your Google account email as a test user
   - Click "Save and Continue"

### Step 4: Create OAuth 2.0 Credentials

1. **Create OAuth Client ID**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - **Name**: `RePlayList Web Client`
   - **Authorized redirect URIs**:
     - `http://127.0.0.1:8889/callback`
     - `http://localhost:8889/callback`
   - Click "Create"

2. **Download Credentials**
   - Download the JSON file containing your credentials
   - Note down the `client_id` and `client_secret`

### Step 5: Update Configuration

Add your YouTube credentials to `config.json`:

```json
{
  "youtube": {
    "client_id": "your_youtube_client_id_here",
    "client_secret": "your_youtube_client_secret_here",
    "redirect_uri": "http://127.0.0.1:8889/callback"
  }
}
```

## 🔧 Complete Configuration Example

Here's a complete `config.json` example:

```json
{
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
}
```

## ⚠️ Important Notes

### YouTube API Limitations

- **Not Official YouTube Music API**: We're using YouTube Data API v3 as a workaround
- **Limited Functionality**: Some features may not work as expected
- **Rate Limits**: YouTube API has strict rate limits
- **Test Users Only**: The app will only work for users added as test users

### Security Considerations

- **Never commit credentials**: Keep your `config.json` file private
- **Use environment variables**: For production, consider using environment variables
- **Rotate credentials**: Regularly rotate your API keys
- **Monitor usage**: Keep track of API usage in both consoles

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**
   - Ensure redirect URIs match exactly in both the app and configuration
   - Check for typos in the URIs

2. **"Access denied"**
   - Make sure you've added yourself as a test user in Google Cloud Console
   - Check that all required scopes are added

3. **"API key not valid"**
   - Verify your API key is correct
   - Ensure YouTube Data API v3 is enabled

4. **"Client ID not found"**
   - Double-check your client ID and secret
   - Ensure they're in the correct format

### Getting Help

- Check the [Spotify Web API documentation](https://developer.spotify.com/documentation/web-api/)
- Check the [YouTube Data API documentation](https://developers.google.com/youtube/v3)
- Open an issue on [GitHub](https://github.com/Ahmet-Ozbay/RePlayList/issues)

## 📚 Additional Resources

- [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- [Google Cloud Console](https://console.cloud.google.com/)
- [YouTube Data API v3 Reference](https://developers.google.com/youtube/v3/reference)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
