# Team Logos Information

## ✅ Team Logos Added!

Team logos have been integrated into the website and are displayed in multiple places.

## 📍 Where You'll See Logos

### 1. **Top 5 Teams Showcase** (New!)
- Large team logos (80x80px)
- Featured at the top of the Teams section
- Shows rank badge, team name, win %, and record
- Beautiful cards with hover effects

### 2. **Team Standings Table**
- Small logos (32x32px) next to each team name
- Appears in the searchable/sortable table
- Shows for all teams that have logos available

## 🎨 Logo Source

All logos are loaded from **ESPN's CDN**:
- High-quality PNG images
- 500x500 resolution (scaled down for display)
- Automatically loaded from the internet

**Example URL**: `https://a.espncdn.com/i/teamlogos/nba/500/gs.png`

## 🏀 Teams with Logos (30 Modern Teams)

✅ Atlanta Hawks
✅ Boston Celtics
✅ Brooklyn Nets
✅ Charlotte Hornets
✅ Chicago Bulls
✅ Cleveland Cavaliers
✅ Dallas Mavericks
✅ Denver Nuggets
✅ Detroit Pistons
✅ Golden State Warriors
✅ Houston Rockets
✅ Indiana Pacers
✅ LA Clippers
✅ Los Angeles Lakers
✅ Memphis Grizzlies
✅ Miami Heat
✅ Milwaukee Bucks
✅ Minnesota Timberwolves
✅ New Orleans Pelicans
✅ New York Knicks
✅ Oklahoma City Thunder
✅ Orlando Magic
✅ Philadelphia 76ers
✅ Phoenix Suns
✅ Portland Trail Blazers
✅ Sacramento Kings
✅ San Antonio Spurs
✅ Toronto Raptors
✅ Utah Jazz
✅ Washington Wizards

## 🕰️ Historical Teams (Also Supported)

✅ New Jersey Nets (now Brooklyn Nets)
✅ Seattle SuperSonics (now Oklahoma City Thunder)
✅ Vancouver Grizzlies (now Memphis Grizzlies)
✅ Charlotte Bobcats (now Charlotte Hornets)
✅ New Orleans Hornets (now New Orleans Pelicans)

## 🔍 What If a Team Doesn't Have a Logo?

If a team name in your data doesn't match the logo database:
- The team name will still display
- A basketball emoji (🏀) placeholder appears instead
- All functionality still works normally

## 🌐 Internet Connection Required

**Important**: Team logos require an internet connection because they're loaded from ESPN's servers. This keeps the website lightweight and ensures you always have the latest logos.

If you're offline:
- Logos won't display
- Everything else works fine
- Team names and data still show

## 🎨 Logo Sizes Used

- **Large**: 80x80px (Top 5 showcase)
- **Medium**: 48x48px (not currently used, but available)
- **Small**: 32x32px (team table)

## 🔧 Technical Details

Logos are defined in `app.js` in the `teamLogos` object:

```javascript
const teamLogos = {
    "Golden State Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "Los Angeles Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    // ... etc
};
```

## 📝 To Refresh and See Logos

1. Make sure the server is running: `http://localhost:8000`
2. Refresh your browser (F5 or Ctrl+R)
3. Logos should appear immediately!

## 🎯 Features

- **Responsive**: Logos scale properly on all devices
- **Fast Loading**: Cached by browser after first load
- **Hover Effects**: Cards with logos have nice hover animations
- **Fallback**: Basketball emoji if logo unavailable

Enjoy your logo-enhanced NBA website! 🏀

