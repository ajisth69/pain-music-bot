# 🎵 PAIN !! Music Bot

A next-generation, ultra-fast, lag-free Telegram Music Bot built with **Pyrogram v2** and **PyTgCalls**. Designed to deliver the smoothest audio experience on low-resource servers like Render.

---

## ✨ Features

- ⚡️ **Lag-Free Streaming**: Songs are pre-downloaded and converted to WAV locally before playing to eliminate network stuttering and high CPU usage.
- 🎨 **God-Level Aesthetic UI**: Beautifully formatted messages with custom fonts and smooth progress bars.
- 🎵 **JioSaavn Integration**: Search and stream millions of songs directly from JioSaavn.
- 🎛 **Full VC Controls**: Interactive buttons for Play, Pause, Skip, and Stop.
- 🚀 **Mini App Support**: Direct link to launch a mini app interface.
- 🔄 **Auto-Queue System**: Plays the next song automatically when the current one ends.

---

## 🛠 Prerequisites

Before running the bot, ensure you have the following installed:
- **Python 3.10** or higher
- **FFmpeg**: Required for audio conversion and streaming.

---

## 🚀 Quick Deploy

### Deploy to Render

Click the button below to deploy directly to Render. The repo includes a `Dockerfile` to automatically handle FFmpeg installation!

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/ajisth69/pain-music-bot)

---

## 💻 Manual Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ajisth69/pain-music-bot.git
   cd pain-music-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and fill in your credentials (see configuration section below).

4. **Run the Bot**:
   ```bash
   python main.py
   ```

---

## ⚙️ Configuration

Create a `.env` file or set these variables in your hosting provider:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
SESSION_STRING=your_pyrogram_session_string
OWNER_ID=your_telegram_user_id
OWNER_USERNAME=your_telegram_username
BOT_USERNAME=your_bot_username
```

---

## 🎮 Commands

- `/play <song name>` - Search and play a song in voice chat.
- `/pause` - Pause the current stream.
- `/resume` - Resume the paused stream.
- `/skip` - Skip to the next song in queue.
- `/stop` - Stop streaming and leave the voice chat.
- `/ping` - Check bot's latency and system stats.
- `/owner` - Get owner and support information.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to read the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛡 Security

If you discover any security-related issues, please refer to our [SECURITY.md](SECURITY.md) for reporting guidelines.

---
*Made with ❤️ by [ajisth69](https://github.com/ajisth69)*
