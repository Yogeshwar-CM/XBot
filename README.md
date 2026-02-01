<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/X_API-v2-000000?style=for-the-badge&logo=x&logoColor=white" alt="X API">
  <img src="https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge" alt="Groq">
  <img src="https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions">
</p>

<h1 align="center">🤖 XBot</h1>

<p align="center">
  <strong>AI-powered X (Twitter) bot that auto-posts trending AI & Dev content daily</strong>
</p>

<p align="center">
  Fetches real developer discussions from Hacker News & GitHub, generates authentic tweets using Groq AI, and posts to X automatically via GitHub Actions.
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔥 **Real Trending Topics** | Fetches hot discussions from Hacker News (with upvotes), GitHub trending repos, and tech RSS feeds |
| 🤖 **AI-Generated Content** | Uses Groq (free tier) to generate authentic, developer-style tweets — not robotic marketing speak |
| 📤 **Auto-Post to X** | Posts directly to your X account using the official API v2 |
| ⏰ **Scheduled Automation** | Runs daily at 7PM IST via GitHub Actions — fully hands-off |
| 🧪 **Dry Run Mode** | Test the full pipeline without actually posting |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- X Developer Account ([Apply here](https://developer.x.com))
- Groq API Key ([Get free key](https://console.groq.com))

### Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/XBot.git
cd XBot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Verify your API credentials
python main.py --verify

# Test run (doesn't post)
DRY_RUN=true python main.py --now

# Post immediately
python main.py --now

# Start scheduler (runs daily at 7PM)
python main.py
```

---

## 🔑 API Setup

### X (Twitter) API

1. Go to [X Developer Portal](https://developer.x.com/en/portal/dashboard)
2. Create a **Project** → Create an **App**
3. Navigate to **Keys and Tokens**
4. Generate and save:
   - `API Key` & `API Key Secret`
   - `Access Token` & `Access Token Secret`

> ⚠️ **Important**: Enable **Read and Write** permissions in User Authentication Settings

### Groq API (Free)

1. Sign up at [console.groq.com](https://console.groq.com)
2. Go to **API Keys** → **Create API Key**
3. Copy and save your key

---

## ☁️ Deploy with GitHub Actions

The bot runs automatically at **7PM IST daily** using GitHub Actions.

### Setup

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/XBot.git
   git push -u origin main
   ```

2. **Add Repository Secrets**
   
   Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**
   
   | Secret Name | Description |
   |-------------|-------------|
   | `X_API_KEY` | Your X API Key |
   | `X_API_SECRET` | Your X API Key Secret |
   | `X_ACCESS_TOKEN` | Your X Access Token |
   | `X_ACCESS_TOKEN_SECRET` | Your X Access Token Secret |
   | `GROQ_API_KEY` | Your Groq API Key |

3. **Done!** The bot will run daily at 7PM IST.

   To trigger manually: **Actions** → **Daily X Post** → **Run workflow**

---

## 📁 Project Structure

```
XBot/
├── config/
│   └── settings.py           # Configuration & environment management
├── modules/
│   ├── news_fetcher.py       # HN, GitHub, RSS aggregation
│   ├── content_generator.py  # Groq AI tweet generation
│   └── x_poster.py           # X API v2 integration
├── .github/
│   └── workflows/
│       └── daily-post.yml    # GitHub Actions workflow
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md
```

---

## ⚙️ Configuration

### Change Post Time

Edit `.env`:
```env
POST_HOUR=19    # 24-hour format
POST_MINUTE=0
TIMEZONE=Asia/Kolkata
```

### Add News Sources

Edit `config/settings.py`:
```python
RSS_FEEDS = [
    {"name": "Your Source", "url": "https://example.com/feed", "category": "Tech"},
    # Add more...
]
```

### Customize Tweet Style

Modify the prompt in `modules/content_generator.py` to change the AI's writing style.

---

## 🛠️ Tech Stack

- **Python 3.11+** — Core runtime
- **Tweepy** — X API v2 client
- **Groq** — Fast, free LLM inference
- **APScheduler** — Task scheduling
- **Feedparser** — RSS parsing
- **GitHub Actions** — CI/CD automation

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by <a href="https://x.com/yogeshwarcodes">@yogeshwarcodes</a>
</p>
