# Security Policy

## Supported Versions

Only the latest version of this bot is supported. If you are running an older version, please update to the latest commit on the `main` branch before reporting any security issues.

## Reporting a Vulnerability

We take security seriously. If you find a security vulnerability in this project, please do not open a public issue. Instead, report it directly to the maintainer.

You can contact the maintainer at:
- **Telegram**: [@ajisth69](https://t.me/ajisth69)

Please provide a detailed description of the vulnerability and steps to reproduce it. We will try to address it as soon as possible.

## Best Practices

To keep your bot secure, please follow these guidelines:
1. **Keep Secrets Secret**: Never commit your `API_ID`, `API_HASH`, or `BOT_TOKEN` to a public repository. Use environment variables (like in a `.env` file or Render config).
2. **Update Dependencies**: Regularly update the Python packages listed in `requirements.txt` to patch known vulnerabilities.
3. **Review Permissions**: Ensure your bot only has the permissions it needs in groups and channels.
