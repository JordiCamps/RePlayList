# Security Policy

## 🔒 Supported Versions

We provide security updates for the following versions of RePlayList:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## 🚨 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. **DO NOT** create a public GitHub issue
Security vulnerabilities should be reported privately to avoid exposing users to potential risks.

### 2. **Email us directly**
Send an email to: **security@replaylist.app** (or use the contact information in the repository)

### 3. **Include the following information:**
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Suggested fix (if any)
- Your contact information

### 4. **Response timeline:**
- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 7 days
- **Resolution**: Depends on severity and complexity

## 🔍 Security Best Practices

### For Users:
- **Keep RePlayList updated** to the latest version
- **Never share your API credentials** (`config.json`)
- **Use strong, unique passwords** for your Spotify/YouTube accounts
- **Review permissions** when authorizing the app
- **Report suspicious behavior** immediately

### For Developers:
- **Follow secure coding practices**
- **Validate all user inputs**
- **Use HTTPS for all API communications**
- **Implement proper error handling**
- **Keep dependencies updated**
- **Follow the principle of least privilege**

## 🛡️ Security Features

RePlayList implements several security measures:

- **OAuth 2.0** for secure authentication
- **HTTPS-only** API communications
- **No credential storage** in plain text
- **Input validation** and sanitization
- **Rate limiting** to prevent abuse
- **Secure token handling**

## 🔐 Data Privacy

- **No data collection**: RePlayList doesn't collect or store personal data
- **Local processing**: All playlist operations happen locally
- **API credentials**: Stored locally in `config.json` (not transmitted)
- **Temporary data**: Playlist data is only held in memory during transfers

## 📋 Vulnerability Disclosure

We follow responsible disclosure practices:

1. **Private reporting** of vulnerabilities
2. **Timely acknowledgment** of reports
3. **Collaborative resolution** with reporters
4. **Public disclosure** after fixes are available
5. **Credit attribution** to security researchers

## 🏆 Security Acknowledgments

We appreciate security researchers who help keep RePlayList secure. Contributors will be acknowledged in our security advisories.

## 📞 Contact

For security-related questions or concerns:
- **Email**: security@replaylist.app
- **GitHub**: Create a private security advisory
- **Response time**: Within 48 hours

---

**Thank you for helping keep RePlayList secure!** 🛡️
