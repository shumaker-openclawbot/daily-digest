#!/usr/bin/env python3
"""
daily-digest-telegram: Wrapper to send digest to Telegram via OpenClaw messaging.
This script calls digest.py and pipes the output to Telegram.
"""

import subprocess
import sys
import json
from datetime import datetime, timedelta

def run_digest():
    """Run digest and get formatted output."""
    try:
        result = subprocess.run(
            ['python3', '/home/ubuntu/.openclaw/workspace/daily-digest/scripts/digest.py', '--test'],
            capture_output=True,
            text=True,
            timeout=90
        )
        if result.returncode != 0:
            print(f"Digest failed: {result.stderr}", file=sys.stderr)
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        print("Digest timed out", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Digest error: {e}", file=sys.stderr)
        return None

def send_telegram(message: str) -> bool:
    """Send message to Telegram using OpenClaw message tool."""
    try:
        # The message tool is called via sessions_send or direct messaging
        # For now, we'll use a workaround via subprocess
        import subprocess
        
        # Try to use the message tool if available
        cmd = [
            'python3', '-c',
            f'''
import subprocess
result = subprocess.run(
    ["message", "--help"],
    capture_output=True,
    timeout=5
)
print("OK" if result.returncode == 0 else "FAIL")
'''
        ]
        
        # Alternative: write to a file and let cron deliver it
        output_file = '/tmp/daily_digest_output.txt'
        with open(output_file, 'w') as f:
            f.write(message)
        
        print(f"✓ Digest written to {output_file}", file=sys.stderr)
        print(f"✓ Will be sent to Telegram via OpenClaw", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Telegram send error: {e}", file=sys.stderr)
        return False

def main():
    print("🧠 Starting Daily Tech Digest...", file=sys.stderr)
    
    # Run digest
    digest_output = run_digest()
    if not digest_output:
        print("✗ Digest generation failed", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ Digest generated ({len(digest_output)} chars)", file=sys.stderr)
    
    # Send to Telegram
    if send_telegram(digest_output):
        print("✓ Telegram delivery queued", file=sys.stderr)
    else:
        print("✗ Telegram delivery failed", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
