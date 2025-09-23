# Getting Help

Need help with RePlayList? Here's where to find support and how to get the best assistance.

## 🆘 Quick Help

### Before Asking for Help

1. **Check the FAQ** - [Frequently Asked Questions](FAQ)
2. **Search existing issues** - [GitHub Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)
3. **Read the documentation** - [Wiki Home](Home)
4. **Try troubleshooting** - [Troubleshooting Guide](Troubleshooting)

### Common Solutions

**App won't start:**
- Check dependencies are installed
- Verify Python, Node.js, and Rust versions
- Clear cache and restart

**Authentication fails:**
- Verify API credentials in `config.json`
- Check redirect URIs match exactly
- Re-authenticate your accounts

**Transfers fail:**
- Check internet connection
- Verify playlist permissions
- Try with debug mode enabled

## 📞 Support Channels

### GitHub Issues
**Best for:** Bug reports, feature requests, technical problems

- **Create an issue**: [New Issue](https://github.com/Ahmet-Ozbay/RePlayList/issues/new)
- **Search issues**: [All Issues](https://github.com/Ahmet-Ozbay/RePlayList/issues)
- **Bug report template**: Use the bug report template
- **Feature request template**: Use the feature request template

### GitHub Discussions
**Best for:** Questions, ideas, general discussion

- **Ask a question**: [New Discussion](https://github.com/Ahmet-Ozbay/RePlayList/discussions/new)
- **Browse discussions**: [All Discussions](https://github.com/Ahmet-Ozbay/RePlayList/discussions)
- **Categories**: Q&A, Ideas, General, Show and Tell

### Documentation
**Best for:** Learning how to use RePlayList

- **Wiki**: [Complete documentation](Home)
- **API Setup**: [Detailed API configuration](API-Setup)
- **Quick Start**: [Get started quickly](Quick-Start)
- **User Guides**: [Desktop App](Desktop-Application), [CLI](CLI-Usage)

## 🐛 Reporting Bugs

### Before Reporting

1. **Search existing issues** - Don't create duplicates
2. **Try the latest version** - Update to the latest release
3. **Check the FAQ** - Your issue might be common
4. **Enable debug mode** - Gather detailed logs

### Bug Report Checklist

- [ ] **Clear title** - Describe the problem briefly
- [ ] **Detailed description** - What happened vs. what you expected
- [ ] **Steps to reproduce** - Exact steps to recreate the issue
- [ ] **System information** - OS, versions, configuration
- [ ] **Error messages** - Copy/paste any error messages
- [ ] **Logs** - Include relevant log output
- [ ] **Screenshots** - Visual evidence if applicable

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. Windows 11, macOS 14, Ubuntu 22.04]
- RePlayList Version: [e.g. 1.0.0]
- Python Version: [e.g. 3.11.0]
- Node.js Version: [e.g. 18.17.0]

**Additional Context**
Any other context about the problem.
```

## 💡 Requesting Features

### Before Requesting

1. **Search existing requests** - Check if already requested
2. **Consider the scope** - Is it within RePlayList's purpose?
3. **Think about implementation** - How might it work?
4. **Consider alternatives** - Are there workarounds?

### Feature Request Checklist

- [ ] **Clear title** - Describe the feature briefly
- [ ] **Detailed description** - What you want to achieve
- [ ] **Use cases** - Specific scenarios where it's needed
- [ ] **Motivation** - Why is this feature important?
- [ ] **Alternatives** - What you've tried instead
- [ ] **Mockups** - Visual examples if applicable

### Feature Request Template

```markdown
**Feature Description**
A clear description of what you want to happen.

**Motivation**
Why is this feature needed? What problem does it solve?

**Use Cases**
Describe specific use cases for this feature.

**Alternatives Considered**
What alternatives have you considered?

**Additional Context**
Any other context, mockups, or examples.
```

## 🔍 Asking Good Questions

### Question Structure

1. **Title** - Brief, descriptive summary
2. **Context** - What you're trying to accomplish
3. **Problem** - What's not working
4. **Attempts** - What you've tried
5. **Details** - System info, logs, etc.

### Good Question Example

```markdown
**Title**: Authentication fails with "Invalid redirect URI" error

**Context**: I'm trying to set up RePlayList for the first time and connect my Spotify account.

**Problem**: When I click "Connect Spotify", I get an error saying "Invalid redirect URI".

**What I've tried**:
- Checked my config.json file
- Verified my Spotify app settings
- Tried different redirect URIs

**System Info**:
- OS: Windows 11
- Python: 3.11.0
- RePlayList: 1.0.0

**Error Message**:
```
Error: Invalid redirect URI
Expected: http://127.0.0.1:8888/callback
Actual: http://localhost:8888/callback
```

**Config**:
```json
{
  "spotify": {
    "redirect_uri": "http://127.0.0.1:8888/callback"
  }
}
```
```

### Bad Question Example

```markdown
**Title**: It doesn't work

**Problem**: RePlayList is broken, please fix it.

**Details**: I'm on Windows and it's not working.
```

## 📊 Providing Information

### System Information

Include these details when asking for help:

**Operating System:**
- Windows version (e.g., Windows 11 22H2)
- macOS version (e.g., macOS 13.0 Ventura)
- Linux distribution (e.g., Ubuntu 22.04 LTS)

**Software Versions:**
- Python version: `python --version`
- Node.js version: `node --version`
- Rust version: `rustc --version`
- RePlayList version: Check package.json or git tag

**Configuration:**
- API credentials configured (without revealing them)
- Transfer settings
- Any custom modifications

### Logs and Debug Information

**Enable debug mode:**
```bash
# CLI
python cli.py --debug playlists list

# Desktop app
# Set "debug": true in config.json
```

**Common log locations:**
- Console output
- Application logs
- Error messages
- Network requests

**Include relevant logs:**
- Error messages
- Stack traces
- Network errors
- Authentication failures

## ⏰ Response Times

### Expected Response Times

- **Critical bugs**: 24-48 hours
- **Feature requests**: 1-2 weeks
- **General questions**: 2-3 days
- **Documentation issues**: 1 week

### Factors Affecting Response Time

- **Issue complexity** - More complex issues take longer
- **Information provided** - Complete information gets faster responses
- **Community activity** - Busy periods may cause delays
- **Maintainer availability** - Personal schedules affect response times

## 🤝 Community Guidelines

### Be Respectful

- Use polite, professional language
- Be patient with responses
- Respect different skill levels
- Avoid personal attacks

### Be Helpful

- Provide complete information
- Search before asking
- Help others when you can
- Share solutions you find

### Be Constructive

- Focus on the problem, not the person
- Suggest improvements
- Provide feedback
- Contribute to discussions

## 📚 Self-Help Resources

### Documentation

- **[Installation Guide](Installation)** - Setup instructions
- **[Quick Start](Quick-Start)** - Get started quickly
- **[Desktop App](Desktop-Application)** - GUI usage
- **[CLI Usage](CLI-Usage)** - Command-line usage
- **[API Setup](API-Setup)** - API configuration
- **[Troubleshooting](Troubleshooting)** - Common issues

### External Resources

- **Spotify Web API**: [Developer Documentation](https://developer.spotify.com/documentation/web-api/)
- **YouTube Data API**: [Developer Documentation](https://developers.google.com/youtube/v3)
- **Tauri Documentation**: [Desktop App Framework](https://tauri.app/)
- **SvelteKit Documentation**: [Frontend Framework](https://kit.svelte.dev/)

### Search Tips

- **GitHub Issues**: Use keywords, labels, and filters
- **Discussions**: Search by category and tags
- **Wiki**: Use the search function
- **Google**: Site-specific search with `site:github.com/Ahmet-Ozbay/RePlayList`

## 🎯 Getting the Best Help

### Do Your Research

1. **Read the documentation** - Check relevant guides
2. **Search existing issues** - Look for similar problems
3. **Try troubleshooting** - Follow troubleshooting steps
4. **Enable debug mode** - Gather detailed information

### Provide Complete Information

1. **Clear description** - What you're trying to do
2. **Exact steps** - How to reproduce the issue
3. **System details** - OS, versions, configuration
4. **Error messages** - Copy/paste exact errors
5. **Logs** - Include relevant log output

### Be Patient and Persistent

1. **Wait for responses** - Don't bump too frequently
2. **Provide updates** - Share new information
3. **Try suggestions** - Test proposed solutions
4. **Follow up** - Let us know if issues are resolved

---

**Ready to get help?** Choose the right channel and provide complete information for the best assistance! 🚀
