#!/usr/bin/env python3
"""
daily-digest v4 - Rich feed aggregator with RSS feeds
- Fetches from 40+ diverse sources
- RSS feeds for consistent, fresh content
- Tech blogs, news sites, podcasts, research
- No limitation to GitHub/HN - full web coverage
"""

import subprocess
import json
import time
import sys
import feedparser
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import urllib.parse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIG - RICH DIVERSE SOURCES
# ============================================================================

# RSS Feeds - primary source for variety
RSS_FEEDS = [
    # Tech News
    ('https://feeds.arstechnica.com/arstechnica/index', 'Ars Technica', 'ars-technica'),
    ('https://www.theverge.com/rss/index.xml', 'The Verge', 'the-verge'),
    ('https://feeds.techcrunch.com/techcrunch/', 'TechCrunch', 'techcrunch'),
    ('https://feeds.bloomberg.com/markets/technology.rss', 'Bloomberg Tech', 'bloomberg-tech'),
    ('https://feeds.wired.com/feed/rss', 'WIRED', 'wired'),
    ('https://news.ycombinator.com/rss', 'Hacker News', 'hn'),
    
    # Dev & Open Source
    ('https://github.blog/feed/', 'GitHub Blog', 'github-blog'),
    ('https://dev.to/feed/', 'Dev.to', 'devto'),
    ('https://lobste.rs/rss', 'Lobsters', 'lobsters'),
    ('https://www.smashingmagazine.com/feed/', 'Smashing Magazine', 'smashing'),
    
    # AI & Research
    ('https://feeds.openai.com/openai-blog.rss', 'OpenAI', 'openai'),
    ('https://www.anthropic.com/feed.xml', 'Anthropic', 'anthropic'),
    ('https://feeds.deepmind.com/blog.xml', 'DeepMind', 'deepmind'),
    ('https://www.infoq.com/feed/ai-machine-learning', 'InfoQ AI', 'infoq-ai'),
    
    # Indie & Startups
    ('https://www.producthunt.com/feed.xml', 'Product Hunt', 'ph'),
    ('https://news.ycombinator.com/rss', 'YC News', 'yc-news'),
    ('https://www.indiehackers.com/feed.xml', 'Indie Hackers', 'indie-hackers'),
    
    # India Tech
    ('https://yourstory.com/feed', 'YourStory', 'yourstory'),
    ('https://www.inc42.com/feed/', 'Inc42', 'inc42'),
    ('https://www.moneycontrol.com/rss/tech.xml', 'Moneycontrol Tech', 'moneycontrol'),
    
    # Security & Privacy
    ('https://feeds.arstechnica.com/arstechnica/security', 'Ars Security', 'ars-security'),
    ('https://feeds.bleepingcomputer.com/feed/', 'Bleeping Computer', 'bleeping-computer'),
    
    # Cloud & Infrastructure
    ('https://www.docker.com/feed.xml', 'Docker', 'docker'),
    ('https://www.hashicorp.com/feed.xml', 'HashiCorp', 'hashicorp'),
    ('https://www.serverless.com/feed.xml', 'Serverless', 'serverless'),
    
    # Programming & Languages
    ('https://feeds.rust-lang.org/all.xml', 'Rust Lang', 'rust-lang'),
    ('https://go.dev/blog/feed.atom', 'Go Blog', 'go-blog'),
    ('https://www.python.org/jobs/feed/', 'Python.org', 'python'),
    
    # Web Development
    ('https://www.webkit.org/feed.xml', 'WebKit', 'webkit'),
    ('https://blog.chromium.org/feeds/posts/default', 'Chromium Blog', 'chromium'),
    
    # Data & Databases
    ('https://www.mongodb.com/blog/feed', 'MongoDB Blog', 'mongodb'),
    ('https://www.postgresql.org/message-id/latest@postgresql.org', 'PostgreSQL', 'postgresql'),
    
    # Community & Culture
    ('https://feeds.npr.org/1019/rss.xml', 'NPR Tech', 'npr-tech'),
    ('https://www.wired.com/feed/rss', 'WIRED Culture', 'wired-culture'),
]

# ============================================================================
# HTTP HELPERS
# ============================================================================

def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch URL with curl."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-L', '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', url],
            capture_output=True,
            timeout=timeout,
            text=True
        )
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        print(f"Fetch error {url}: {e}", file=sys.stderr)
        return None

# ============================================================================
# RSS PARSER
# ============================================================================

def parse_rss_feed(feed_url: str, source_name: str, source_id: str, limit: int = 8) -> List[Dict]:
    """Parse RSS feed."""
    try:
        print(f"Fetching {source_name}...", file=sys.stderr)
        feed = feedparser.parse(feed_url)
        items = []
        
        for entry in feed.entries[:limit]:
            title = entry.get('title', '')
            link = entry.get('link', '')
            summary = entry.get('summary', '')
            
            # Clean HTML from summary
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary[:200].strip()
            
            if title and link:
                items.append({
                    'title': title,
                    'url': link,
                    'source': source_name,
                    'source_id': source_id,
                    'summary': summary,
                    'type': 'article'
                })
        
        print(f"  Got {len(items)} items from {source_name}", file=sys.stderr)
        return items
    except Exception as e:
        print(f"RSS parse error {source_id}: {e}", file=sys.stderr)
        return []

# ============================================================================
# AGGREGATOR
# ============================================================================

def fetch_all_feeds(parallel: int = 12, timeout: int = 60) -> List[Dict]:
    """Fetch all RSS feeds in parallel."""
    all_items = []
    
    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = {
            executor.submit(parse_rss_feed, url, name, sid, limit=6): (name, sid)
            for url, name, sid in RSS_FEEDS
        }
        
        for future in as_completed(futures, timeout=timeout):
            try:
                items = future.result()
                all_items.extend(items)
            except Exception as e:
                name, sid = futures[future]
                print(f"Feed error {name}: {e}", file=sys.stderr)
    
    return all_items

def classify_article(title: str, summary: str, source_name: str) -> str:
    """Classify article into a category."""
    text = (title + ' ' + summary + ' ' + source_name).lower()
    
    # AI/ML
    if any(x in text for x in ['ai', 'gpt', 'llm', 'neural', 'machine learning', 'deep learning', 'model', 'transformer', 'copilot']):
        return 'AI/ML'
    
    # Cloud/Infrastructure
    if any(x in text for x in ['cloud', 'aws', 'kubernetes', 'docker', 'infrastructure', 'devops', 'serverless']):
        return 'Cloud/Infrastructure'
    
    # Web Development
    if any(x in text for x in ['web', 'frontend', 'react', 'javascript', 'typescript', 'css', 'html', 'vue']):
        return 'Web Development'
    
    # Security
    if any(x in text for x in ['security', 'breach', 'vulnerability', 'privacy', 'encryption', 'hack']):
        return 'Security'
    
    # DevTools & Languages
    if any(x in text for x in ['rust', 'golang', 'python', 'tool', 'cli', 'framework', 'library']):
        return 'DevTools'
    
    # Startups & Business
    if any(x in text for x in ['startup', 'funding', 'raise', 'series', 'vc', 'venture', 'billion']):
        return 'Startups/Funding'
    
    # Open Source
    if any(x in text for x in ['open source', 'github', 'repository', 'release']):
        return 'Open Source'
    
    # Research
    if any(x in text for x in ['research', 'paper', 'study', 'announcement']):
        return 'Research'
    
    # India Tech
    if any(x in text for x in ['india', 'yourstory', 'inc42', 'moneycontrol']):
        return 'India Tech'
    
    # Community
    if 'community' in text or 'discussion' in text:
        return 'Community'
    
    return 'Tech News'

def build_sections(items: List[Dict]) -> Dict[str, List[Dict]]:
    """Classify and organize into sections."""
    sections = {
        'TOP NEWS': [],
        'TRENDING NOW': [],
        'RESEARCH & INNOVATION': [],
        'DEVELOPMENT': [],
        'COMMUNITY': []
    }
    
    # Classify
    classified = []
    for item in items:
        category = classify_article(item['title'], item.get('summary', ''), item['source'])
        classified.append({**item, 'category': category})
    
    # Group by category
    categories = {}
    for item in classified:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    # Distribute to sections
    top = (categories.get('AI/ML', [])[:2] + 
           categories.get('Research', [])[:1] +
           categories.get('Cloud/Infrastructure', [])[:2] +
           categories.get('Startups/Funding', [])[:2] +
           categories.get('Tech News', [])[:2])[:8]
    sections['TOP NEWS'] = top
    
    trending = (categories.get('Community', [])[:2] +
                categories.get('Open Source', [])[:2] +
                categories.get('India Tech', [])[:2] +
                categories.get('Tech News', [])[2:4])[:6]
    sections['TRENDING NOW'] = trending
    
    research = (categories.get('Research', [])[1:] +
                categories.get('AI/ML', [])[2:] +
                categories.get('Security', []))[:5]
    sections['RESEARCH & INNOVATION'] = research
    
    dev = (categories.get('Web Development', []) +
           categories.get('DevTools', []) +
           categories.get('Cloud/Infrastructure', [])[2:])[:6]
    sections['DEVELOPMENT'] = dev
    
    community = (categories.get('Community', [])[2:] +
                 categories.get('India Tech', [])[2:] +
                 categories.get('Tech News', [])[4:])[:5]
    sections['COMMUNITY'] = community
    
    # Deduplicate by URL
    all_seen_urls = set()
    for section_name in sections:
        unique = []
        for item in sections[section_name]:
            url = item['url']
            if url not in all_seen_urls:
                all_seen_urls.add(url)
                unique.append(item)
        sections[section_name] = unique
    
    return sections

def push_to_github(digest_json: Dict) -> bool:
    """Commit and push digest to GitHub."""
    try:
        with open('/home/ubuntu/.openclaw/workspace/public/digest.json', 'w') as f:
            json.dump(digest_json, f, indent=2)
        
        subprocess.run(['git', 'add', 'public/digest.json'], 
                      cwd='/home/ubuntu/.openclaw/workspace', check=True)
        
        commit_msg = f"Update digest: {digest_json['generated_at']}"
        subprocess.run(['git', 'commit', '-m', commit_msg], 
                      cwd='/home/ubuntu/.openclaw/workspace', check=True)
        
        subprocess.run(['git', 'push', 'origin', 'master'], 
                      cwd='/home/ubuntu/.openclaw/workspace', check=True)
        
        print("✓ Pushed to GitHub", file=sys.stderr)
        return True
    except Exception as e:
        print(f"GitHub push error: {e}", file=sys.stderr)
        return False

def main():
    print("Starting rich digest aggregation (RSS feeds)...", file=sys.stderr)
    start = time.time()
    
    # Fetch all RSS feeds
    all_items = fetch_all_feeds(parallel=12, timeout=70)
    elapsed = time.time() - start
    print(f"Fetched {len(all_items)} items in {elapsed:.1f}s", file=sys.stderr)
    
    # Classify and organize
    sections = build_sections(all_items)
    
    # Get IST time
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    ist_time = utc_now + timedelta(hours=5, minutes=30)
    
    # Build JSON output
    digest_data = {
        'generated_at': ist_time.strftime("%Y-%m-%d %H:%M IST"),
        'total_sources': len(RSS_FEEDS),
        'sections': {}
    }
    
    for section_name, items in sections.items():
        digest_data['sections'][section_name] = []
        for item in items:
            digest_data['sections'][section_name].append({
                'title': item['title'],
                'summary': item.get('summary', item['title'][:90]),
                'source': item['source'],
                'category': item.get('category', 'News'),
                'link': item['url']
            })
    
    # Print JSON
    print(json.dumps(digest_data, indent=2))
    
    # Push to GitHub
    push_to_github(digest_data)
    
    # Stats
    total = sum(len(v) for v in sections.values())
    print(f"Total items: {total} from {digest_data['total_sources']} sources | Total time: {time.time() - start:.1f}s", file=sys.stderr)

if __name__ == '__main__':
    main()
