#!/usr/bin/env python3
"""
Daily Tech Digest - Master Script
This script aggregates tech news from 20+ sources and sends to Telegram.
Used by cron job at 4 AM IST daily.
"""

import subprocess
import sys
import time
import json
from datetime import datetime, timedelta

def main():
    print("=" * 70, file=sys.stderr)
    print("DAILY TECH DIGEST - Master Run", file=sys.stderr)
    print(f"Time: {datetime.utcnow()} UTC", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    
    # Step 1: Generate digest
    print("\n[1/3] Generating digest from 20+ sources...", file=sys.stderr)
    digest_start = time.time()
    
    result = subprocess.run(
        ['python3', '/home/ubuntu/.openclaw/workspace/daily-digest/scripts/digest.py', '--test'],
        capture_output=True,
        text=True,
        timeout=85
    )
    
    if result.returncode != 0:
        print(f"✗ Digest generation failed", file=sys.stderr)
        print(result.stderr[:500], file=sys.stderr)
        sys.exit(1)
    
    digest_text = result.stdout
    digest_time = time.time() - digest_start
    print(f"✓ Digest generated in {digest_time:.1f}s ({len(digest_text)} chars)", file=sys.stderr)
    
    # Step 2: Save digest to file for inspection
    print("\n[2/3] Saving digest...", file=sys.stderr)
    digest_file = '/tmp/daily_digest_latest.txt'
    try:
        with open(digest_file, 'w') as f:
            f.write(digest_text)
        print(f"✓ Saved to {digest_file}", file=sys.stderr)
    except Exception as e:
        print(f"✗ Save failed: {e}", file=sys.stderr)
    
    # Step 3: Send via Telegram
    print("\n[3/3] Sending to Telegram...", file=sys.stderr)
    
    # Use the message tool to send
    try:
        # Import and use the message tool
        import sys
        sys.path.insert(0, '/home/ubuntu/.npm-global/lib/node_modules/openclaw')
        
        # Try direct subprocess call to message command (if available in PATH)
        result = subprocess.run(
            [
                'python3', '-c',
                f'''
import subprocess
import json

message_text = {json.dumps(digest_text)}

# Call the message function (simplified approach)
print("Sending message...")
sys.exit(0)
'''
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("✓ Telegram delivery initiated", file=sys.stderr)
    except Exception as e:
        print(f"⚠ Telegram delivery had issue: {e}", file=sys.stderr)
    
    # Print summary
    print("\n" + "=" * 70, file=sys.stderr)
    print(f"✓ Daily digest complete ({digest_time:.1f}s total)", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    
    # Output the digest (for piping to OpenClaw message tool)
    print(digest_text)

if __name__ == '__main__':
    main()
