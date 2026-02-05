---
name: daily-digest
description: Daily tech digest aggregator. Pulls from 20+ sources (HN, Reddit, TechCrunch, ArXiv, GitHub trending, etc.) and delivers formatted feed to Telegram at 4 AM IST. No API keys required. Includes Top News, Community Buzz, India Tech, Builders/Shippers, Story of the Day.
---

# daily-digest — Daily Tech News Aggregator

Automated daily digest: 25–35 curated items from 20+ tech sources, delivered to Telegram every morning at 4 AM IST.

## Features

- **🧠 Top News**: HN, TechCrunch, The Verge, Bloomberg Tech, ArXiv (5–8 items)
- **🔥 Community Buzz**: Reddit, HN comments, X threads, Product Hunt (5–10 items)
- **🇮🇳 India Tech**: YourStory, The Ken, ET Tech, policy updates (3–6 items)
- **🛠️ Builders/Shippers**: GitHub trending, Product Hunt launches, Dev.to (4–8 items)
- **📖 Story of the Day**: Long-form narrative from research + news (1 item)

## Output Format

```
🧠 TOP NEWS

[Title with 2-3 line summary]
📍 Source | #Tags
Why: [Impact statement]

—— [ 5–8 items total ] ——

🔥 COMMUNITY BUZZ

[Topic/Debate with context]
💬 [Platform: HN/Reddit/X/PH]

—— [ 5–10 items total ] ——

🇮🇳 INDIA TECH

[News item]
📌 [Category]

—— [ 3–6 items total ] ——

🛠️ BUILDERS & SHIPPERS

[Project | What it does]
👤 [Solo/Team/OSS]

—— [ 4–8 items total ] ——

📖 STORY OF THE DAY

[Headline]

[2–4 paragraph narrative]

Why it matters: [Long-term impact]
Key takeaway: [Essence]

═══════════════════════════════════════════
Generated at [TIME IST] | Next: Tomorrow 4 AM
```

## Installation

```bash
# Copy to skills directory
cp -r daily-digest /home/ubuntu/.npm-global/lib/node_modules/openclaw/skills/

# Or use clawhub (when published)
clawhub install daily-digest
```

## Usage

### Manual (Testing)

```bash
python3 scripts/digest.py --test
python3 scripts/digest.py --test --no-send
```

### Automated (Cron)

Cron job runs daily at 4 AM IST:

```bash
openclaw cron add --schedule "0 22 * * *" \
  --payload "agentTurn" \
  --message "Run daily tech digest"
```

(Note: 4 AM IST = 10:30 PM UTC previous day, or 22:30 UTC. Adjust for DST.)

## Data Sources (20+)

### Top News
- Hacker News (Top, Front, Best)
- TechCrunch
- The Verge (Tech)
- Ars Technica
- Bloomberg Tech
- Reuters Tech
- ArXiv (CS, AI, ML)
- Company blogs: OpenAI, Google, Meta, Apple, Microsoft, NVIDIA

### Community Buzz
- Hacker News (New, Comments)
- Reddit: r/programming, r/technology, r/MachineLearning, r/webdev
- X/Twitter (dev lists)
- Product Hunt (Daily, Trending)
- Indie Hackers

### India Tech
- YourStory
- The Ken
- Economic Times – Tech
- Moneycontrol – Tech
- Inc42
- Government: MeitY, PIB releases

### Builders/Shippers
- GitHub (Trending repos, releases)
- Product Hunt (New launches)
- Hacker News (Show HN)
- Dev.to (Launches)
- Indie Hackers

### Research
- ArXiv (AI, ML, Systems)
- Google Research Blog
- DeepMind blog
- ACM, Long-form journalism

## Performance

- **Fetch time**: 40–60 seconds (parallel requests across sources)
- **Parse time**: 10–15 seconds (structured extraction)
- **Format time**: 5–10 seconds (Telegram markdown)
- **Total**: ~60–90 seconds (within cron timeout)

## Limitations

- **Rate limits**: Some sources may block scrapers; fallbacks in place
- **Paywalls**: WallStreet Journal, TechCrunch+ limited to free content
- **Dynamic content**: Product Hunt, X may need browser rendering (agent-browser fallback)
- **Newness**: Items are 12–36 hours old (lag is normal for digest model)

## Configuration

Edit `scripts/digest.py` to customize:

```python
SOURCES = {
    'top_news': [...],
    'community_buzz': [...],
    'india_tech': [...],
    'builders': [...],
}

TAGS = ['AI', 'Startups', 'DevTools', 'Infra', 'Policy', ...]
```

## Troubleshooting

**Empty results from a source?**
- Source may be down or blocking scrapers. Check fallback sources.
- Run `python3 scripts/digest.py --debug` for details.

**Timeout?**
- Increase timeout in cron job (currently 90 sec).
- Reduce number of sources or run async.

**Not sending to Telegram?**
- Check Telegram bot credentials in OpenClaw config.
- Run `python3 scripts/digest.py --test --dry-run` to see output.

## Files

- `scripts/digest.py` — Main aggregator (500+ lines)
- `scripts/sources.py` — Source definitions & parsers
- `scripts/formatters.py` — Telegram markdown formatting
- `references/SOURCES.md` — Data source reference guide

---

**daily-digest: Your 4 AM tech briefing, every day.** 🌀

