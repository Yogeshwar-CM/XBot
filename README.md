<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/X_API-v2-000000?style=for-the-badge&logo=x&logoColor=white" alt="X API">
  <img src="https://img.shields.io/badge/Groq-LLM-F55036?style=for-the-badge" alt="Groq">
  <img src="https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" alt="GitHub Actions">
</p>

# XBot

**Automated X (Twitter) bot for trending AI & Dev content.**

XBot fetches developer discussions from Hacker News and GitHub, generates concise summaries using Groq AI, and automatically posts to X via GitHub Actions.

---

## Features

- **Trending Content Aggregation**: Fetches top discussions from Hacker News, GitHub trending repositories, and tech RSS feeds.
- **AI-Generated Content**: Utilizes Groq to generate relevant, developer-focused tweets.
- **Automated Posting**: Posts directly to X using the official API v2.
- **Scheduled Execution**: Configured to run daily via GitHub Actions.
- **Dry Run Mode**: Test the pipeline without posting to live accounts.

---

## Quick Start

### Prerequisites

- Python 3.11+
- X Developer Account ([Apply here](https://developer.x.com))
- Groq API Key ([Get free key](https://console.groq.com))

### Installation

```bash
# Clone the repository
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
# Verify API credentials
python main.py --verify

# Test run (dry run, does not post)
DRY_RUN=true python main.py --now

# Post immediately
python main.py --now

# Start local scheduler
python main.py
```

---

## API Setup

### X (Twitter) API

1. Go to the [X Developer Portal](https://developer.x.com/en/portal/dashboard).
2. Create a **Project** and an **App**.
3. Navigate to **Keys and Tokens**.
4. Generate the following:
   - `API Key` & `API Key Secret`
   - `Access Token` & `Access Token Secret`
5. Ensure **Read and Write** permissions are enabled in User Authentication Settings.

### Groq API

1. Sign up at [console.groq.com](https://console.groq.com).
2. Create a new API Key.
3. Save the key for configuration.

---

## Deploy with GitHub Actions

The bot is configured to run automatically using GitHub Actions.

### Setup

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/yourusername/XBot.git
   git push -u origin main
   ```

2. **Configure Secrets**
   
   Navigate to **Settings** → **Secrets and variables** → **Actions** → **New repository secret** in your GitHub repository.
   
   | Secret Name | Description |
   |-------------|-------------|
   | `X_API_KEY` | Your X API Key |
   | `X_API_SECRET` | Your X API Key Secret |
   | `X_ACCESS_TOKEN` | Your X Access Token |
   | `X_ACCESS_TOKEN_SECRET` | Your X Access Token Secret |
   | `GROQ_API_KEY` | Your Groq API Key |

3. **Validation**
   The workflow will trigger automatically based on the schedule defined in `.github/workflows/daily-post.yml`.
   To trigger manually: Go to **Actions** → **Daily X Post** → **Run workflow**.

---

## Project Structure

```
XBot/
├── config/
│   └── settings.py           # Configuration settings
├── modules/
│   ├── news_fetcher.py       # Content aggregation logic
│   ├── content_generator.py  # AI generation logic
│   └── x_poster.py           # X API integration
├── .github/
│   └── workflows/
│       └── daily-post.yml    # CI/CD configuration
├── main.py                   # Application entry point
├── requirements.txt          # Dependencies
├── .env.example              # Environment variable template
└── README.md
```

---

## Configuration

### Schedule

To change the posting time, modify the `.env` file or update the cron schedule in `.github/workflows/daily-post.yml` for GitHub Actions.

```env
POST_HOUR=19
POST_MINUTE=0
TIMEZONE=Asia/Kolkata
```

### News Sources

Add or remove sources in `config/settings.py`:

```python
RSS_FEEDS = [
    {"name": "Your Source", "url": "https://example.com/feed", "category": "Tech"},
]
```

---

## Tech Stack

- **Python 3.11+**
- **Tweepy** (X API v2)
- **Groq** (LLM Inference)
- **APScheduler**
- **Feedparser**
- **GitHub Actions**

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.