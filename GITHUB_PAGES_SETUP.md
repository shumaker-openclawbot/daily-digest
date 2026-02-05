# GitHub Pages Setup Instructions

## To Enable GitHub Pages for Daily Tech Digest

### Step 1: Go to Repository Settings
1. Navigate to: https://github.com/shumaker-openclawbot/daily-digest
2. Click on **Settings** tab (top right)
3. On the left sidebar, click **Pages**

### Step 2: Configure GitHub Pages
1. Under "Source", select **Deploy from a branch**
2. Under "Branch", select:
   - Branch: `master`
   - Folder: `/public`
3. Click **Save**

### Step 3: Wait for Deployment
- GitHub will automatically deploy the site
- You'll get a live URL like: `https://shumaker-openclawbot.github.io/daily-digest/`
- Green checkmark = deployment complete

### Step 4: Auto-Updates (Already Working!)
- Every time the cron job runs at 4 AM IST
- digest.json gets updated and pushed to GitHub
- GitHub Pages automatically rebuilds the site
- Your website shows fresh digest automatically! ✅

## How It Works

1. **Cron Job** (4 AM IST daily)
   - Fetches 40+ RSS feeds
   - Generates digest.json
   - Commits and pushes to GitHub

2. **GitHub Pages** (Automatic)
   - Detects the push to `/public` folder
   - Rebuilds the site
   - Deploys live within seconds

3. **Website** (Always Fresh)
   - Loads index.html
   - Fetches digest.json dynamically
   - Shows current digest with live timestamp
   - Updates automatically with each cron run

## Benefits

✅ No build process needed (static site)
✅ Auto-updates with every cron push
✅ Free hosting (GitHub Pages)
✅ Live URL for sharing
✅ Custom domain support (optional)

## Your Site URL

Once enabled: `https://shumaker-openclawbot.github.io/daily-digest/`

That's it! The cron job will automatically update your live digest every morning at 4 AM IST.
