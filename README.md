# Weather vs IPL Match Scores Dashboard 🌦️🏏

This project is built for **AI for Bharat – Week 3: The Data Weaver**.

It combines **two unrelated data sources**:

- **Weather data** (temperature, humidity, weather type)
- **IPL match data** (total runs, city, teams, venue, season)

and visualizes how **weather conditions** might relate to **match scores**.

---

## 🧱 Tech Stack

- **Python**
- **Streamlit** for the dashboard UI
- **Pandas** for data wrangling
- **Plotly** for interactive charts
- **Kiro** to accelerate development (code generation, debugging, refactoring)

---

## 📂 Project Structure

```text
.
├── .kiro/                 # Kiro-related metadata / exports
│   └── README.md
├── data/
│   ├── ipl_matches_sample.csv
│   └── weather_sample.csv
├── src/
│   ├── data_prep.py
│   └── dashboard.py
├── .gitignore
├── requirements.txt
└── README.md
