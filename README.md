# Daily Tech Digest

A minimalist, glassmorphic website for curated tech news delivered daily.

## Features

- **Minimalist Design**: Black background, white text, extreme simplicity
- **Glassmorphic UI**: Frosted glass cards with blur effects
- **Responsive**: Works perfectly on desktop, tablet, and mobile
- **No Dependencies**: Pure HTML, CSS, and vanilla JavaScript
- **Fast**: Single file, ~15KB

## Design

- **Typography**: Merriweather serif for articles (elegant news feel), Inter sans-serif for headers
- **Color**: Absolute black (#000000) background with white text
- **Mobile Nav**: Bottom floating navigation bar for mobile devices
- **Smooth Scrolling**: Section navigation with smooth scroll behavior

## Sections

1. **TOP NEWS** - High-impact tech stories
2. **TRENDING NOW** - Community discussions and launches
3. **RESEARCH & INNOVATION** - Deep tech and open source
4. **DEVELOPMENT** - Web dev, DevTools, infrastructure
5. **COMMUNITY** - Commentary and analysis

## Deployment

### Vercel (Recommended)

```bash
vercel
```

### GitHub Pages

1. Enable Pages in repo settings
2. Select `/public` as source
3. Live at: `https://username.github.io/daily-digest/`

### Local

Simply open `public/index.html` in a browser.

## API Integration

To connect with live data:

```javascript
// Fetch from backend API
const response = await fetch('/api/digest');
const data = await response.json();
renderDigest(data);
```

## License

MIT
