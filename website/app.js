// Global data storage
let teamStats = [];
let playerStats = [];
let summary = {};

// Team logos from ESPN
const teamLogos = {
    "Atlanta Hawks": "https://a.espncdn.com/i/teamlogos/nba/500/atl.png",
    "Boston Celtics": "https://a.espncdn.com/i/teamlogos/nba/500/bos.png",
    "Brooklyn Nets": "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "Charlotte Hornets": "https://a.espncdn.com/i/teamlogos/nba/500/cha.png",
    "Chicago Bulls": "https://a.espncdn.com/i/teamlogos/nba/500/chi.png",
    "Cleveland Cavaliers": "https://a.espncdn.com/i/teamlogos/nba/500/cle.png",
    "Dallas Mavericks": "https://a.espncdn.com/i/teamlogos/nba/500/dal.png",
    "Denver Nuggets": "https://a.espncdn.com/i/teamlogos/nba/500/den.png",
    "Detroit Pistons": "https://a.espncdn.com/i/teamlogos/nba/500/det.png",
    "Golden State Warriors": "https://a.espncdn.com/i/teamlogos/nba/500/gs.png",
    "Houston Rockets": "https://a.espncdn.com/i/teamlogos/nba/500/hou.png",
    "Indiana Pacers": "https://a.espncdn.com/i/teamlogos/nba/500/ind.png",
    "LA Clippers": "https://a.espncdn.com/i/teamlogos/nba/500/lac.png",
    "Los Angeles Lakers": "https://a.espncdn.com/i/teamlogos/nba/500/lal.png",
    "Memphis Grizzlies": "https://a.espncdn.com/i/teamlogos/nba/500/mem.png",
    "Miami Heat": "https://a.espncdn.com/i/teamlogos/nba/500/mia.png",
    "Milwaukee Bucks": "https://a.espncdn.com/i/teamlogos/nba/500/mil.png",
    "Minnesota Timberwolves": "https://a.espncdn.com/i/teamlogos/nba/500/min.png",
    "New Orleans Pelicans": "https://a.espncdn.com/i/teamlogos/nba/500/no.png",
    "New York Knicks": "https://a.espncdn.com/i/teamlogos/nba/500/ny.png",
    "Oklahoma City Thunder": "https://a.espncdn.com/i/teamlogos/nba/500/okc.png",
    "Orlando Magic": "https://a.espncdn.com/i/teamlogos/nba/500/orl.png",
    "Philadelphia 76ers": "https://a.espncdn.com/i/teamlogos/nba/500/phi.png",
    "Phoenix Suns": "https://a.espncdn.com/i/teamlogos/nba/500/phx.png",
    "Portland Trail Blazers": "https://a.espncdn.com/i/teamlogos/nba/500/por.png",
    "Sacramento Kings": "https://a.espncdn.com/i/teamlogos/nba/500/sac.png",
    "San Antonio Spurs": "https://a.espncdn.com/i/teamlogos/nba/500/sa.png",
    "Toronto Raptors": "https://a.espncdn.com/i/teamlogos/nba/500/tor.png",
    "Utah Jazz": "https://a.espncdn.com/i/teamlogos/nba/500/utah.png",
    "Washington Wizards": "https://a.espncdn.com/i/teamlogos/nba/500/wsh.png",
    // Historical teams
    "New Jersey Nets": "https://a.espncdn.com/i/teamlogos/nba/500/bkn.png",
    "Seattle SuperSonics": "https://a.espncdn.com/i/teamlogos/nba/500/sea.png",
    "Vancouver Grizzlies": "https://a.espncdn.com/i/teamlogos/nba/500/mem.png",
    "Charlotte Bobcats": "https://a.espncdn.com/i/teamlogos/nba/500/cha.png",
    "New Orleans Hornets": "https://a.espncdn.com/i/teamlogos/nba/500/no.png"
};

// Load all data on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    initializeApp();
});

// Load JSON data
async function loadData() {
    try {
        const [teamsResponse, playersResponse, summaryResponse] = await Promise.all([
            fetch('team_stats.json'),
            fetch('player_stats.json'),
            fetch('summary.json')
        ]);

        teamStats = await teamsResponse.json();
        playerStats = await playersResponse.json();
        summary = await summaryResponse.json();

        console.log('Data loaded successfully:', { teamStats, playerStats, summary });
    } catch (error) {
        console.error('Error loading data:', error);
        alert('Error loading data. Please make sure all JSON files are present.');
    }
}

// Initialize the application
function initializeApp() {
    renderOverviewStats();
    renderTopTeamsLogos();
    renderTopTeamsChart();
    renderTeamsTable();
    renderTopPlayersChart();
    renderPlayersTable();
    renderWinsLossesChart();
    renderPointsDistributionChart();
    setupEventListeners();
    setupNavigation();
}

// Render overview statistics
function renderOverviewStats() {
    const overviewStats = document.getElementById('overview-stats');

    const stats = [
        { icon: '🏀', value: summary.teams.total_teams, label: 'Total Teams' },
        { icon: '👥', value: summary.players.total_players, label: 'Total Players' },
        { icon: '🎯', value: (summary.teams.avg_win_pct * 100).toFixed(1) + '%', label: 'Avg Win %' },
        { icon: '📊', value: summary.teams.avg_points.toFixed(1), label: 'Avg Points' },
        { icon: '🏆', value: summary.teams.max_wins, label: 'Most Wins' },
        { icon: '⭐', value: summary.players.avg_points.toFixed(1), label: 'Avg Player PPG' }
    ];

    overviewStats.innerHTML = stats.map(stat => `
        <div class="stat-card">
            <div class="stat-icon">${stat.icon}</div>
            <div class="stat-value">${stat.value}</div>
            <div class="stat-label">${stat.label}</div>
        </div>
    `).join('');
}

// Render top teams with logos
function renderTopTeamsLogos() {
    const container = document.getElementById('topTeamsLogos');
    const topTeams = summary.teams.top_10_teams.slice(0, 5);

    container.innerHTML = topTeams.map((team, index) => {
        const logoUrl = teamLogos[team.team_name];
        const rank = index + 1;
        const rankClass = rank <= 3 ? `rank-${rank}` : 'rank-other';

        return `
            <div class="top-team-card">
                <div class="top-team-rank">
                    <span class="rank-badge ${rankClass}">${rank}</span>
                </div>
                ${logoUrl ? `<img src="${logoUrl}" alt="${team.team_name}" class="team-logo-large">` : '<div class="team-logo-placeholder">🏀</div>'}
                <h4 class="top-team-name">${team.team_name}</h4>
                <div class="top-team-stats">
                    <div class="top-team-stat">
                        <span class="stat-value">${(team.win_pct * 100).toFixed(1)}%</span>
                        <span class="stat-label">Win %</span>
                    </div>
                    <div class="top-team-stat">
                        <span class="stat-value">${team.wins}-${team.losses}</span>
                        <span class="stat-label">Record</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Render top teams chart
function renderTopTeamsChart() {
    const ctx = document.getElementById('topTeamsChart').getContext('2d');
    const topTeams = summary.teams.top_10_teams;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topTeams.map(t => t.team_name),
            datasets: [{
                label: 'Win Percentage',
                data: topTeams.map(t => (t.win_pct * 100).toFixed(2)),
                backgroundColor: 'rgba(29, 66, 138, 0.8)',
                borderColor: 'rgba(29, 66, 138, 1)',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => `Win %: ${context.parsed.x}%`
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Win Percentage (%)' }
                }
            }
        }
    });
}

// Render teams table
function renderTeamsTable(filteredData = null) {
    const data = filteredData || teamStats;
    const tbody = document.getElementById('teamsTableBody');

    // Sort by win percentage by default
    const sortedData = [...data].sort((a, b) => b.win_pct - a.win_pct);

    tbody.innerHTML = sortedData.slice(0, 50).map((team, index) => {
        const rank = index + 1;
        const rankClass = rank <= 3 ? `rank-${rank}` : 'rank-other';
        const logoUrl = teamLogos[team.team_name];

        return `
            <tr>
                <td><span class="rank-badge ${rankClass}">${rank}</span></td>
                <td>
                    <div class="team-cell">
                        ${logoUrl ? `<img src="${logoUrl}" alt="${team.team_name}" class="team-logo-small">` : ''}
                        <strong>${team.team_name}</strong>
                    </div>
                </td>
                <td>${team.wins}</td>
                <td>${team.losses}</td>
                <td><strong>${(team.win_pct * 100).toFixed(1)}%</strong></td>
                <td>${team.points.toFixed(1)}</td>
                <td>${team.assists.toFixed(1)}</td>
                <td>${team.rebounds.toFixed(1)}</td>
            </tr>
        `;
    }).join('');
}

// Render top players chart
function renderTopPlayersChart() {
    if (playerStats.length === 0) {
        document.getElementById('topPlayersChart').parentElement.innerHTML =
            '<p class="text-center text-secondary">No player data available</p>';
        return;
    }

    const ctx = document.getElementById('topPlayersChart').getContext('2d');
    const topPlayers = [...playerStats].sort((a, b) => b.POINTS - a.POINTS).slice(0, 10);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topPlayers.map(p => p.PLAYER_NAME),
            datasets: [{
                label: 'Points Per Game',
                data: topPlayers.map(p => p.POINTS),
                backgroundColor: 'rgba(200, 16, 46, 0.8)',
                borderColor: 'rgba(200, 16, 46, 1)',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Render players table
function renderPlayersTable() {
    if (playerStats.length === 0) {
        document.getElementById('playersTable').parentElement.innerHTML =
            '<p class="text-center text-secondary">No player data available</p>';
        return;
    }

    const tbody = document.getElementById('playersTableBody');

    tbody.innerHTML = playerStats.map(player => `
        <tr>
            <td><strong>${player.PLAYER_NAME}</strong></td>
            <td>${player.TEAM_NAME}</td>
            <td>${player.SEASON}</td>
            <td>${player.GAMES_PLAYED}</td>
            <td>${player.MINUTES}</td>
            <td><strong>${player.POINTS}</strong></td>
            <td>${player.ASSISTS}</td>
            <td>${player.REBOUNDS}</td>
            <td>${(player.FG_PERCENT * 100).toFixed(1)}%</td>
            <td>${(player.THREE_PERCENT * 100).toFixed(1)}%</td>
            <td>${(player.FT_PERCENT * 100).toFixed(1)}%</td>
        </tr>
    `).join('');
}

// Render wins vs losses scatter chart
function renderWinsLossesChart() {
    const ctx = document.getElementById('winsLossesChart').getContext('2d');
    const sampleData = teamStats.slice(0, 40);

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Teams',
                data: sampleData.map(t => ({ x: t.wins, y: t.losses })),
                backgroundColor: 'rgba(253, 185, 39, 0.6)',
                borderColor: 'rgba(253, 185, 39, 1)',
                borderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const team = sampleData[context.dataIndex];
                            return `${team.team_name}: ${context.parsed.x}W - ${context.parsed.y}L`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Wins' },
                    beginAtZero: true
                },
                y: {
                    title: { display: true, text: 'Losses' },
                    beginAtZero: true
                }
            }
        }
    });
}

// Render points distribution chart
function renderPointsDistributionChart() {
    const ctx = document.getElementById('pointsDistChart').getContext('2d');

    // Create bins for histogram
    const bins = [0, 85, 90, 95, 100, 105, 110];
    const binCounts = new Array(bins.length - 1).fill(0);
    const binLabels = bins.slice(0, -1).map((b, i) => `${b}-${bins[i + 1]}`);

    teamStats.forEach(team => {
        for (let i = 0; i < bins.length - 1; i++) {
            if (team.points >= bins[i] && team.points < bins[i + 1]) {
                binCounts[i]++;
                break;
            }
        }
    });

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: binLabels,
            datasets: [{
                label: 'Number of Teams',
                data: binCounts,
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
                borderColor: 'rgba(16, 185, 129, 1)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Points Range' }
                },
                y: {
                    title: { display: true, text: 'Number of Teams' },
                    beginAtZero: true
                }
            }
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    // Team search
    const teamSearch = document.getElementById('teamSearch');
    if (teamSearch) {
        teamSearch.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const filtered = teamStats.filter(team =>
                team.team_name.toLowerCase().includes(searchTerm)
            );
            renderTeamsTable(filtered);
        });
    }

    // Team sort
    const sortBy = document.getElementById('sortBy');
    if (sortBy) {
        sortBy.addEventListener('change', (e) => {
            const sortField = e.target.value;
            const sorted = [...teamStats].sort((a, b) => {
                if (sortField === 'team_name') {
                    return a[sortField].localeCompare(b[sortField]);
                }
                return b[sortField] - a[sortField];
            });
            renderTeamsTable(sorted);
        });
    }
}

// Setup smooth scrolling navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

                // Update active link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });

    // Update active link on scroll
    window.addEventListener('scroll', () => {
        const sections = document.querySelectorAll('.section');
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (window.pageYOffset >= sectionTop - 100) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

