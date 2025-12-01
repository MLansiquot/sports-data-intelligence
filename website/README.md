# NBA Sports Data Intelligence Website

A modern, interactive web application showcasing comprehensive NBA statistics and analytics.

## 🎯 Features

### Overview Dashboard
- **Total Teams**: Display count of all NBA teams in the dataset
- **Total Players**: Show number of players tracked
- **Average Win Percentage**: League-wide win percentage statistics
- **Average Points**: Team scoring averages
- **Most Wins**: Highlight top-performing teams
- **Player Statistics**: Average points per game across all players

### Team Performance Section
- **Top 10 Teams Chart**: Interactive horizontal bar chart showing teams with highest win percentages
- **Team Standings Table**: 
  - Searchable team list
  - Sortable by win %, wins, points, or team name
  - Shows wins, losses, win percentage, points, assists, and rebounds
  - Top 3 teams highlighted with gold, silver, and bronze badges

### Player Statistics Section
- **Top Players Chart**: Visual representation of leading scorers
- **Player Performance Table**: Detailed stats including:
  - Games played, minutes, points, assists, rebounds
  - Field goal percentage, 3-point percentage, free throw percentage

### Advanced Analytics
- **Wins vs Losses Scatter Plot**: Visual correlation between team wins and losses
- **Points Distribution Chart**: Histogram showing how teams are distributed across point ranges

## 🚀 How to Use

### Initial Setup
1. Run the data conversion script to generate JSON files:
   ```bash
   python website/convert_data.py
   ```
   This creates:
   - `team_stats.json` - All team statistics
   - `player_stats.json` - All player statistics
   - `summary.json` - Aggregated summary data

2. Open `index.html` in your web browser:
   - Double-click the file, or
   - Right-click and select "Open with" your preferred browser, or
   - Use a local web server (recommended for best performance)

### Using a Local Web Server (Recommended)
For better performance and to avoid CORS issues:

**Option 1: Python**
```bash
cd website
python -m http.server 8000
```
Then open: `http://localhost:8000`

**Option 2: Node.js (with npx)**
```bash
cd website
npx http-server -p 8000
```
Then open: `http://localhost:8000`

**Option 3: VS Code Live Server**
- Install "Live Server" extension in VS Code
- Right-click `index.html` and select "Open with Live Server"

## 📊 Data Sources

The website uses data from:
- `data/nba_team_stats/nba_team_stats.csv` - Historical NBA team statistics
- `data/nba_player_stats/nba_player_stats.csv` - Player performance data

## 🎨 Features & Interactions

### Navigation
- Smooth scrolling between sections
- Active section highlighting in navigation bar
- Responsive design for mobile and desktop

### Team Table Features
- **Search**: Type in the search box to filter teams by name
- **Sort**: Use the dropdown to sort by different metrics
- **Ranking**: Top 3 teams get special badge colors

### Charts
- All charts are interactive with hover tooltips
- Built using Chart.js for smooth animations
- Responsive and mobile-friendly

## 🛠️ Technology Stack

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **JavaScript (ES6+)**: Vanilla JS for data handling and interactivity
- **Chart.js**: Professional data visualization library
- **Python**: Data processing and conversion

## 📁 File Structure

```
website/
├── index.html          # Main HTML file
├── styles.css          # All styling
├── app.js             # JavaScript logic and charts
├── convert_data.py    # Data conversion script
├── team_stats.json    # Generated team data
├── player_stats.json  # Generated player data
├── summary.json       # Generated summary statistics
└── README.md          # This file
```

## 🎯 Key Metrics Explained

- **Win %**: Percentage of games won (wins / total games)
- **PPG**: Points Per Game
- **FG%**: Field Goal Percentage
- **3P%**: Three-Point Percentage
- **FT%**: Free Throw Percentage

## 🔄 Updating Data

To update the website with new data:
1. Update the CSV files in the `data/` directory
2. Run `python website/convert_data.py` again
3. Refresh the website in your browser

## 🌐 Browser Compatibility

Tested and working on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📝 Notes

- The website works entirely client-side (no server required for basic viewing)
- All data is loaded from JSON files for fast performance
- Charts are rendered dynamically based on the data
- Fully responsive design adapts to all screen sizes

## 🎨 Color Scheme

The website uses NBA-inspired colors:
- Primary Blue: `#1d428a`
- Secondary Red: `#c8102e`
- Accent Gold: `#fdb927`
- Dark Background: `#0a1929`

Enjoy exploring your NBA data! 🏀

