# Frequently Asked Questions

## 🔧 General Questions

### What is RePlayList?
RePlayList is a modern desktop application that allows you to transfer playlists between Spotify and YouTube Music. It features intelligent track matching, a beautiful user interface, and both desktop and command-line interfaces.

### Is RePlayList free?
Yes! RePlayList is completely free and open-source. It's licensed under the MIT License, which means you can use, modify, and distribute it freely.

### Which platforms are supported?
- **Desktop**: Windows, macOS, Linux
- **Music Platforms**: Spotify, YouTube Music
- **Interfaces**: Desktop app (Tauri), Command-line interface

### Do I need to create accounts?
You need accounts on the music platforms you want to use:
- **Spotify account** for Spotify access
- **Google account** for YouTube Music access
- **GitHub account** (optional) for contributing

## 🔐 Authentication & API

### Do I need API keys?
Yes, you need API credentials for both platforms:
- **Spotify**: Client ID and Client Secret
- **YouTube**: Client ID and Client Secret

See our [API Setup Guide](API-Setup) for detailed instructions.

### Are my credentials safe?
Yes! Your credentials are:
- Stored locally in `config.json`
- Never transmitted to our servers
- Only used to access your own playlists
- Protected by OAuth2 security

### What permissions does RePlayList need?
- **Spotify**: Read playlists, read user profile, create playlists
- **YouTube**: Read playlists, read user profile, create playlists

### Can I revoke access?
Yes! You can revoke access at any time:
- **Spotify**: Go to [Spotify Account Settings](https://www.spotify.com/account/apps/)
- **YouTube**: Go to [Google Account Settings](https://myaccount.google.com/permissions)

## 🎵 Playlist Transfer

### How accurate is track matching?
RePlayList uses intelligent fuzzy matching with multiple algorithms:
- **Exact matches**: 100% accuracy
- **Fuzzy matches**: 85%+ similarity threshold
- **Partial matches**: Title matches, artist differs
- **Overall success rate**: Typically 80-95%

### What happens to unmatched tracks?
Unmatched tracks are:
- Listed in the transfer summary
- Skipped during transfer
- Available for manual review
- Can be retried with different settings

### Can I transfer private playlists?
Yes! You can transfer:
- Your own private playlists
- Collaborative playlists you have access to
- Public playlists from other users

### How long do transfers take?
Transfer time depends on:
- **Playlist size**: Larger playlists take longer
- **Network speed**: Faster internet = faster transfers
- **Match complexity**: Complex matching takes more time
- **Typical time**: 1-2 minutes per 100 tracks

### Can I transfer playlists in both directions?
Yes! RePlayList supports:
- **Spotify → YouTube Music**
- **YouTube Music → Spotify**
- **Bidirectional transfers**

## 🖥️ Desktop Application

### How do I install the desktop app?
1. Clone the repository
2. Install dependencies
3. Run `npm run dev:tauri` for development
4. Run `npm run build:app` for production

See our [Installation Guide](Installation) for detailed steps.

### Why does the app open in a browser?
RePlayList uses a web-based interface that runs in a desktop window. This provides:
- Cross-platform compatibility
- Modern web technologies
- Easy updates and maintenance
- Familiar user interface

### Can I use the app offline?
No, RePlayList requires an internet connection to:
- Access music platforms
- Search for tracks
- Transfer playlists
- Authenticate with services

### How do I update the app?
To update RePlayList:
1. Pull the latest changes: `git pull origin main`
2. Update dependencies: `npm install` and `pip install -r requirements.txt`
3. Rebuild the app: `npm run build:app`

## 💻 Command Line Interface

### How do I use the CLI?
The CLI provides powerful command-line tools:

```bash
# List playlists
python cli.py playlists list

# Transfer playlist
python cli.py transfer start --source spotify --target youtube --playlist "My Playlist"

# Get help
python cli.py --help
```

See our [CLI Usage Guide](CLI-Usage) for complete documentation.

### Can I automate transfers?
Yes! You can:
- Use the CLI in scripts
- Set up scheduled transfers
- Create batch operations
- Use configuration files

### Is the CLI available on all platforms?
Yes! The CLI works on:
- Windows (PowerShell, Command Prompt)
- macOS (Terminal)
- Linux (Bash, Zsh, etc.)

## 🔧 Technical Questions

### What programming languages are used?
- **Backend**: Python (FastAPI, Pydantic)
- **Frontend**: TypeScript (SvelteKit, Tailwind CSS)
- **Desktop**: Rust (Tauri)
- **CLI**: Python (argparse)

### How is the project structured?
RePlayList uses a modular architecture:
- **Backend**: Python API server
- **Frontend**: SvelteKit web application
- **Desktop**: Tauri desktop wrapper
- **CLI**: Python command-line interface

See our [Architecture Guide](Architecture) for details.

### Can I contribute to the project?
Yes! We welcome contributions:
- **Code**: Bug fixes, new features
- **Documentation**: Wiki, guides, examples
- **Testing**: Bug reports, test cases
- **Design**: UI/UX improvements

See our [Contributing Guide](Contributing) for details.

### How do I report bugs?
Report bugs by:
1. Checking existing [GitHub Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)
2. Creating a new issue with detailed information
3. Including logs and steps to reproduce

### How do I request features?
Request features by:
1. Checking existing [GitHub Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)
2. Creating a new feature request
3. Providing detailed use cases and examples

## 🚨 Troubleshooting

### The app won't start
Common solutions:
1. **Check dependencies**: Ensure Python, Node.js, and Rust are installed
2. **Update packages**: Run `npm install` and `pip install -r requirements.txt`
3. **Check logs**: Enable debug mode for detailed error information
4. **Clear cache**: Delete cache files and restart

### Authentication fails
Common solutions:
1. **Check credentials**: Verify API keys in `config.json`
2. **Check redirect URIs**: Ensure they match exactly
3. **Re-authenticate**: Log out and log back in
4. **Check permissions**: Ensure required permissions are granted

### Transfers fail or are slow
Common solutions:
1. **Check internet connection**: Ensure stable connection
2. **Check API limits**: Respect rate limits
3. **Adjust settings**: Lower match threshold or enable parallel processing
4. **Check logs**: Enable debug mode for detailed information

### Tracks don't match
Common solutions:
1. **Lower match threshold**: Try 0.7 instead of 0.8
2. **Check track metadata**: Ensure titles and artists are correct
3. **Manual review**: Review and approve matches manually
4. **Different search terms**: Try alternative search terms

## 📚 Getting Help

### Where can I get help?
- **GitHub Issues**: [Report bugs and request features](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/Ahmet-Ozbay/RePlayList/discussions)
- **Wiki**: [Browse documentation](https://github.com/Ahmet-Ozbay/RePlayList/wiki)
- **Email**: Contact the maintainers directly

### How do I ask a good question?
When asking for help, include:
- **What you're trying to do**
- **What you expected to happen**
- **What actually happened**
- **Steps to reproduce the issue**
- **System information** (OS, versions, etc.)
- **Error messages or logs**

### Is there a community?
Yes! Join our community:
- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs and request features
- **Contributing**: Help improve the project
- **Documentation**: Help improve the wiki

## 🔮 Future Plans

### What features are planned?
- **More music platforms**: Apple Music, Amazon Music, etc.
- **Advanced matching**: Machine learning-based matching
- **Scheduled transfers**: Automatic playlist synchronization
- **Mobile app**: iOS and Android applications
- **Cloud sync**: Sync settings across devices

### How can I stay updated?
- **Watch the repository**: Get notifications for updates
- **Check releases**: See new versions and changelog
- **Follow discussions**: Stay updated on development
- **Read the wiki**: Keep up with documentation

---

**Still have questions?** Check out our [Getting Help](Getting-Help) page or [ask the community](https://github.com/Ahmet-Ozbay/RePlayList/discussions)! 🚀
