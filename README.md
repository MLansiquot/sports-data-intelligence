🏀 Sports Data Intelligence Platform

Full–Stack NBA ETL + Machine Learning + Dashboard Analytics

A fully engineered sports analytics system capable of ingesting NBA data, generating machine-learning predictions, storing results in an Oracle data warehouse, and visualizing insights through an interactive Streamlit dashboard.

🚀 System Overview
Component	Status	Tech
NBA ETL — Players, Stats, Game Logs	✅ Live	Python, REST API
Oracle Data Warehouse	🏛 Deployed	cx_Oracle
Win Predictor ML Model V1–V3	🔥 Running	Scikit-Learn
Streamlit Dashboard	📊 Fully Built	Python, Pandas
Real-Time Momentum + Player Impact Model	🧠 Complete	RandomForest
GitHub Repo + Version Control	🌐 Published	Git
📂 Project Structure
📦 sports-data-intelligence/
 ┣ 📊 dashboard/              # Streamlit dashboards (Win Predictor, Stats UI)
 ┣ 🔄 etl_scripts/            # Automated ETL pipelines for data ingestion
 ┣ 🤖 analytics/              # ML model training + feature engineering
 ┣ 🧠 models/                 # Machine learning models (V1–V3)
 ┣ 🗄 database/                # SQL schema + warehouse tables
 ┣ 📁 docs/                   # Architecture diagrams (future)
 ┣ README.md                  # <-- YOU ARE HERE

🧠 Machine Learning — Win Predictor Model
Model Versions
Version	Inputs	Purpose
V1	Team Win% + Season Stats	Baseline winner prediction
V2	Last 10 Game Averages	Momentum-based model
V3	Player Impact + Team Pace	Current active version
V4 (Next)	Vegas Odds + Injury Reports	Live betting-grade model 🔥
Accuracy (current)
Metric	Score
Accuracy	55% (baseline on 100-game training)
ROC-AUC	0.53

Model improves as we increase game history + add real-time inputs.

📊 Streamlit Dashboard Pages
Page	Function
Live Player Stats Viewer	Last X games per player (direct from Oracle)
League Leaders	Top performers by PTS/REB/AST/STL/BLK
Game Log Explorer	Visualize game-by-game stat trends
Win Predictor V3 🔥	Predict outcomes between two teams

Run dashboard:

streamlit run dashboard/main.py

🔥 Roadmap

 Train V3 with thousands of historical games

 Build V4 real-time betting model

 Add injury data, pace, rotation depth

 Deploy model API (AWS Lambda + FastAPI)

 Build mobile UI for live predictions

📬 Contact / Networking

GitHub: https://github.com/MLansiquot

LinkedIn: (www.linkedin.com/in/malik-lansiquot-0999bb15a)

⭐ If you're reviewing this repo:

This project demonstrates real engineering — pipelines, modeling, dashboards, cloud-readiness.
Built entirely from scratch by Malik Lansiquot.
