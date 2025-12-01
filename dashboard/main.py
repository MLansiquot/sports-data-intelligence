import streamlit as st

st.set_page_config(page_title="Sports Data Intelligence", page_icon="🏀", layout="wide")

st.title("🏀 Sports Data Intelligence Dashboard")
st.subheader("Welcome to the analytics control center.")

st.markdown("""
Select a module from the sidebar on the left to start analyzing.

### 📊 Active Analytics Modules
| Tool | Purpose |
|------|---------|
| 🔮 Win Predictor | Predict game outcomes using ML |
| 🆚 Player Comparison | Compare two players head-to-head |
| 📈 Live Player Stats | View latest player game logs |
| 📅 Game Log Explorer *(Coming Next)* | Trend charts across time |
| 🏆 League Leaders *(Next Option)* | Top players by category |

---

### 🚀 Vision Roadmap
| Feature | ETA |
|--------|-----|
| AI Win Predictions | **Done** |
| Player Comparison Engine | **Now Active** |
| League Trend Analyzer | Next |
| Season Simulation Engine | On deck |
""")
