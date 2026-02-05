#!/usr/bin/env python3
"""
daily-digest v2: Smart news aggregator with AI categorization.
- Fetches from 25+ diverse sources
- AI categorizes each article
- Generates mini-summaries
- No emoji, minimal markup
- Section-agnostic source mixing

Usage:
  python3 digest.py --test
  python3 digest.py
"""

import subprocess
import json
import time
import sys
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import urllib.parse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# CONFIG
# ============================================================================

SOURCES = [
    # Tech News
    ('https://news.ycombinator.com', 'hn_top', 'Hacker News Top'),
    ('https://news.ycombinator.com/front', 'hn_front', 'Hacker News Front'),
    ('https://news.ycombinator.com/newest', 'hn_new', 'Hacker News New'),
    ('https://techcrunch.com', 'techcrunch', 'TechCrunch'),
    ('https://www.theverge.com/tech', 'theverge', 'The Verge'),
    ('https://arstechnica.com', 'arstechnica', 'Ars Technica'),
    ('https://www.bloomberg.com/technology', 'bloomberg_tech', 'Bloomberg Tech'),
    
    # Community
    ('https://www.reddit.com/r/programming/hot', 'reddit_programming', 'r/programming'),
    ('https://www.reddit.com/r/technology/hot', 'reddit_technology', 'r/technology'),
    ('https://www.reddit.com/r/MachineLearning/hot', 'reddit_ml', 'r/MachineLearning'),
    ('https://www.reddit.com/r/webdev/hot', 'reddit_webdev', 'r/webdev'),
    ('https://www.producthunt.com/posts', 'producthunt', 'Product Hunt'),
    ('https://www.indiehackers.com', 'indiehackers', 'Indie Hackers'),
    
    # India Tech
    ('https://yourstory.com/tech', 'yourstory', 'YourStory'),
    ('https://theknow.economictimes.indiatimes.com/tech', 'et_tech', 'ET Tech'),
    ('https://www.moneycontrol.com/technology', 'moneycontrol', 'Moneycontrol'),
    ('https://www.inc42.com', 'inc42', 'Inc42'),
    
    # Dev & Open Source
    ('https://github.com/trending', 'github_trending', 'GitHub Trending'),
    ('https://dev.to', 'devto', 'Dev.to'),
    ('https://lobste.rs', 'lobsters', 'Lobsters'),
    
    # Research
    ('https://arxiv.org/list/cs.AI/recent', 'arxiv_ai', 'ArXiv AI'),
    ('https://research.google/pubs/', 'google_research', 'Google Research'),
    ('https://www.deepmind.com/blog', 'deepmind', 'DeepMind'),
]

# News categories for AI classification
CATEGORIES = [
    'AI/ML',
    'Cloud/Infrastructure',
    'Web Development',
    'Security',
    'DevTools',
    'Startups/Funding',
    'Open Source',
    'Product Launches',
    'Research',
    'Policy/Regulation',
    'India Tech',
    'Community Discussion',
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
# PARSERS
# ============================================================================

def parse_hackernews(url: str, limit: int = 8) -> List[Dict]:
    """Parse Hacker News."""
    try:
        from bs4 import BeautifulSoup
        html = fetch_url(url, timeout=8)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        for row in soup.find_all('tr', class_='athing')[:limit]:
            title_cell = row.find('span', class_='titleline')
            if not title_cell:
                continue
            
            title = title_cell.get_text(strip=True)
            link = title_cell.find('a')
            url = link['href'] if link else ''
            
            if title and url:
                items.append({
                    'title': title,
                    'url': url,
                    'source': 'Hacker News',
                    'type': 'news'
                })
        
        return items
    except Exception as e:
        print(f"HN parse error: {e}", file=sys.stderr)
        return []

def parse_reddit(url: str, limit: int = 5) -> List[Dict]:
    """Parse Reddit."""
    try:
        from bs4 import BeautifulSoup
        html = fetch_url(url, timeout=8)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        for post in soup.find_all('shreddit-post')[:limit]:
            title = post.get('post-title')
            permalink = post.get('permalink')
            
            if title and permalink:
                items.append({
                    'title': title,
                    'url': f"https://reddit.com{permalink}",
                    'source': 'Reddit',
                    'type': 'discussion'
                })
        
        return items
    except Exception as e:
        print(f"Reddit parse error: {e}", file=sys.stderr)
        return []

def parse_generic_articles(url: str, limit: int = 5, site_name: str = 'News') -> List[Dict]:
    """Generic article parser."""
    try:
        from bs4 import BeautifulSoup
        html = fetch_url(url, timeout=8)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        for article in soup.find_all('article')[:limit]:
            h2 = article.find(['h2', 'h3'])
            if not h2:
                continue
            
            link = h2.find('a')
            if not link:
                continue
            
            title = link.get_text(strip=True)
            href = link.get('href', '')
            
            if href.startswith('/'):
                domain = urllib.parse.urlparse(url).netloc
                href = f"https://{domain}{href}"
            
            if title and href:
                items.append({
                    'title': title,
                    'url': href,
                    'source': site_name,
                    'type': 'article'
                })
        
        return items
    except Exception as e:
        print(f"Generic parse error: {e}", file=sys.stderr)
        return []

def parse_github_trending(limit: int = 5) -> List[Dict]:
    """Parse GitHub trending."""
    try:
        from bs4 import BeautifulSoup
        html = fetch_url('https://github.com/trending', timeout=8)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        items = []
        
        for article in soup.find_all('article')[:limit]:
            h2 = article.find('h2')
            if not h2:
                continue
            
            repo_link = h2.find('a')
            if not repo_link:
                continue
            
            repo_name = repo_link['href'].strip('/')
            p = article.find('p', class_='col-9')
            desc = p.get_text(strip=True) if p else repo_name
            
            items.append({
                'title': f"{repo_name}: {desc[:60]}",
                'url': f"https://github.com{repo_link['href']}",
                'source': 'GitHub',
                'type': 'project'
            })
        
        return items
    except Exception as e:
        print(f"GitHub parse error: {e}", file=sys.stderr)
        return []

# ============================================================================
# MAIN AGGREGATOR
# ============================================================================

def fetch_source(source_tuple: tuple) -> List[Dict]:
    """Fetch a single source."""
    url, source_id, source_name = source_tuple
    
    try:
        if 'hackernews' in source_id or 'hn_' in source_id:
            items = parse_hackernews(url, limit=8)
        elif 'reddit' in source_id:
            items = parse_reddit(url, limit=6)
        elif 'github' in source_id:
            items = parse_github_trending(limit=8)
        elif 'producthunt' in source_id:
            items = parse_generic_articles(url, limit=6, site_name='Product Hunt')
        elif 'yourstory' in source_id:
            items = parse_generic_articles(url, limit=6, site_name='YourStory')
        elif 'et_tech' in source_id:
            items = parse_generic_articles(url, limit=6, site_name='Economic Times')
        elif any(x in source_id for x in ['theverge', 'arstechnica', 'bloomberg', 'techcrunch']):
            items = parse_generic_articles(url, limit=6, site_name=source_name)
        else:
            items = []
        
        # Tag with source
        for item in items:
            item['source_id'] = source_id
            item['source_name'] = source_name
        
        return items
    except Exception as e:
        print(f"Source error {source_id}: {e}", file=sys.stderr)
        return []

def fetch_all_sources(parallel: int = 8, timeout: int = 70) -> List[Dict]:
    """Fetch all sources in parallel."""
    all_items = []
    
    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = {executor.submit(fetch_source, source): source for source in SOURCES}
        
        for future in as_completed(futures, timeout=timeout):
            try:
                items = future.result()
                all_items.extend(items)
            except Exception as e:
                print(f"Future error: {e}", file=sys.stderr)
    
    return all_items

def classify_article(title: str, source_name: str) -> str:
    """Classify article into a category - order matters!"""
    text = (title + ' ' + source_name).lower()
    
    # AI/ML first (most specific)
    if any(x in text for x in ['ai', 'gpt', 'llm', 'neural network', 'machine learning', 'deep learning', 'model', 'transformers', 'language model']):
        if 'hack' not in text and 'breach' not in text:
            return 'AI/ML'
    
    # Open Source (check before DevTools)
    if any(x in text for x in ['github', 'open source', 'repository', 'rust', 'golang', 'rust tool']):
        if source_name in ['GitHub Trending']:
            return 'Open Source'
    
    # Web Development
    if any(x in text for x in ['web', 'frontend', 'react', 'javascript', 'css', 'html', 'vue', 'typescript']):
        return 'Web Development'
    
    # Cloud/Infrastructure
    if any(x in text for x in ['cloud', 'aws', 'kubernetes', 'docker', 'infrastructure', 'devops', 'datacenter']):
        return 'Cloud/Infrastructure'
    
    # DevTools/CLI
    if any(x in text for x in ['tool', 'framework', 'library', 'cli', 'command line']):
        return 'DevTools'
    
    # Startups/Funding
    if any(x in text for x in ['startup', 'funding', 'raise', 'series a', 'vc', 'venture', 'billion']):
        return 'Startups/Funding'
    
    # Product Launches
    if any(x in text for x in ['launch', 'announce', 'new', 'release', 'product hunt', 'beta']):
        if source_name in ['Product Hunt']:
            return 'Product Launches'
    
    # Research/Academic
    if any(x in text for x in ['research', 'paper', 'arxiv', 'study', 'google research', 'stanford', 'mit']):
        return 'Research'
    
    # Security/Privacy (check last to avoid catching "hack" in repos)
    if any(x in text for x in ['security', 'breach', 'vulnerability', 'crypto', 'privacy', 'encryption']):
        return 'Security'
    
    # Policy
    if any(x in text for x in ['policy', 'regulation', 'law', 'government', 'dsa', 'gdpr', 'act']):
        return 'Policy/Regulation'
    
    # India Tech
    if any(x in text for x in ['india', 'yourstory', 'et tech', 'moneycontrol', 'indian']):
        return 'India Tech'
    
    # Community/Discussion (Reddit)
    if 'reddit' in source_name.lower():
        return 'Community Discussion'
    
    # Default
    return 'Tech News'

def extract_text_from_page(url: str, timeout: int = 8) -> str:
    """Extract readable text from a webpage."""
    try:
        from bs4 import BeautifulSoup
        html = fetch_url(url, timeout=timeout)
        if not html or len(html) < 100:
            return ''
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove boilerplate elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'meta']):
            element.decompose()
        
        # Try to find article/main content
        content = soup.find('article') or soup.find('main') or soup.find('div', class_=re.compile(r'content|article|body|post'))
        if not content:
            content = soup
        
        # Get text, skip very short snippets
        text = content.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())
        
        # Skip if too much boilerplate
        if 'Search code' in text or 'Sign in' in text[:100]:
            return ''
        
        # Return first 400 chars
        return text[:400]
    except Exception:
        return ''

def generate_ai_summary(title: str, url: str, source_name: str) -> str:
    """Generate smart summary from title + page content."""
    # Clean title first
    clean_title = title
    for prefix in ['Show HN:', 'Ask HN:', 'Tell HN:', '[AMA]', '[Tutorial]', '[Guide]']:
        clean_title = clean_title.replace(prefix, '').strip()
    clean_title = re.sub(r'\([a-z0-9.]+\)', '', clean_title)
    clean_title = re.sub(r'\[.*?\]', '', clean_title)
    clean_title = ' '.join(clean_title.split())
    
    # Try to extract page content for better summary
    page_text = extract_text_from_page(url, timeout=5)
    
    # Smart summary from page content
    if page_text:
        # Extract first meaningful sentence
        sentences = page_text.split('. ')
        for sent in sentences[:4]:
            sent = sent.strip()
            # Skip very short or boilerplate
            if len(sent) > 20 and len(sent) < 150 and not sent.startswith('Skip'):
                return sent + '.'
    
    # Fallback: use clean title
    if len(clean_title) > 90:
        return clean_title[:87] + '...'
    return clean_title

def build_sections(items: List[Dict]) -> Dict[str, List[Dict]]:
    """Classify items and organize into sections with diversity."""
    sections = {
        'TOP NEWS': [],
        'TRENDING NOW': [],
        'RESEARCH & INNOVATION': [],
        'DEVELOPMENT': [],
        'COMMUNITY': []
    }
    
    # Classify each article
    classified = []
    for item in items:
        category = classify_article(item['title'], item['source_name'])
        classified.append({**item, 'category': category})
    
    # Group by category
    categories = {}
    for item in classified:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    # Build sections with smart distribution
    # TOP NEWS: High-impact (AI/ML, Cloud, Startups, Research)
    top = (categories.get('AI/ML', [])[:2] + 
           categories.get('Research', [])[:1] +
           categories.get('Cloud/Infrastructure', [])[:2] +
           categories.get('Startups/Funding', [])[:2] +
           categories.get('Tech News', [])[:2])[:8]
    sections['TOP NEWS'] = top
    
    # TRENDING NOW: Community + Community Discussion + Tech News
    trending_tech = categories.get('Tech News', [])[2:5] if len(categories.get('Tech News', [])) > 2 else []
    trending = (categories.get('Community Discussion', [])[:3] +
                categories.get('Product Launches', [])[:2] +
                categories.get('India Tech', [])[:2] +
                trending_tech)[:6]
    sections['TRENDING NOW'] = trending
    
    # RESEARCH & INNOVATION: Deep tech + Open source
    research_tail = categories.get('Research', [])[1:] if len(categories.get('Research', [])) > 1 else []
    ai_tail = categories.get('AI/ML', [])[2:] if len(categories.get('AI/ML', [])) > 2 else []
    research = (research_tail +
                categories.get('Open Source', [])[:2] +
                ai_tail)[:5]
    sections['RESEARCH & INNOVATION'] = research
    
    # DEVELOPMENT: Web dev + DevTools + Open source
    open_source_tail = categories.get('Open Source', [])[2:] if len(categories.get('Open Source', [])) > 2 else []
    tech_news_tail = categories.get('Tech News', [])[5:] if len(categories.get('Tech News', [])) > 5 else []
    dev = (categories.get('Web Development', []) +
           categories.get('DevTools', []) +
           open_source_tail +
           tech_news_tail)[:6]
    sections['DEVELOPMENT'] = dev
    
    # COMMUNITY: Tech News + Policy + discussions
    tech_news_end = categories.get('Tech News', [])[8:] if len(categories.get('Tech News', [])) > 8 else []
    india_tech_tail = categories.get('India Tech', [])[2:] if len(categories.get('India Tech', [])) > 2 else []
    community = (tech_news_end +
                 categories.get('Policy/Regulation', []) +
                 india_tech_tail)[:5]
    sections['COMMUNITY'] = community
    
    # Remove duplicates within and across sections
    # Track by URL only (not title, since titles might vary)
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

def format_telegram(sections: Dict[str, List[Dict]], ist_time: datetime) -> str:
    """Format digest for Telegram with summaries."""
    lines = []
    
    for section_name, items in sections.items():
        if not items:
            continue
        
        lines.append(f"\n{section_name}\n")
        lines.append("-" * 50 + "\n")
        
        for item in items:
            source = item['source_name']
            category = item.get('category', 'News')
            summary = item.get('summary', item['title'][:90])
            
            lines.append(f"{summary}\n")
            lines.append(f"Source: {source} | {category}\n")
            lines.append(f"Link: {item['url']}\n\n")
    
    # Footer
    ist_str = ist_time.strftime("%Y-%m-%d %H:%M IST")
    lines.append("-" * 50 + "\n")
    lines.append(f"Generated: {ist_str}\n")
    lines.append("Next digest: Tomorrow 4 AM\n")
    
    return ''.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Daily tech digest')
    parser.add_argument('--test', action='store_true', help='Test mode')
    parser.add_argument('--no-send', action='store_true', help='Skip send')
    parser.add_argument('--debug', action='store_true', help='Debug output')
    args = parser.parse_args()
    
    print("Starting digest aggregation...", file=sys.stderr)
    start = time.time()
    
    # Fetch
    all_items = fetch_all_sources(parallel=10, timeout=75)
    elapsed = time.time() - start
    
    print(f"Fetched {len(all_items)} items in {elapsed:.1f}s", file=sys.stderr)
    
    # Classify and organize
    sections = build_sections(all_items)
    
    # Generate summaries in parallel
    print(f"Generating summaries...", file=sys.stderr)
    summary_start = time.time()
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {}
        for section_items in sections.values():
            for item in section_items:
                future = executor.submit(generate_ai_summary, item['title'], item['url'], item['source_name'])
                futures[future] = item
        
        for future in as_completed(futures):
            try:
                summary = future.result(timeout=8)
                futures[future]['summary'] = summary
            except Exception as e:
                print(f"Summary error: {e}", file=sys.stderr)
                futures[future]['summary'] = futures[future]['title'][:90]
    
    summary_elapsed = time.time() - summary_start
    print(f"Summaries generated in {summary_elapsed:.1f}s", file=sys.stderr)
    
    # Get IST time
    utc_now = datetime.now(timezone.utc).replace(tzinfo=None)
    ist_time = utc_now + timedelta(hours=5, minutes=30)
    
    # Format
    formatted = format_telegram(sections, ist_time)
    
    if args.test or args.debug:
        print(formatted)
    else:
        print(formatted, flush=True)
    
    # Stats
    total = sum(len(v) for v in sections.values())
    print(f"\nTotal items: {total} | Total time: {time.time() - start:.1f}s", file=sys.stderr)

if __name__ == '__main__':
    main()
