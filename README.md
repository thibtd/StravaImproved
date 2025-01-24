# 🏃 Strava Activity Analyzer

Transform your Strava running data into actionable insights with interactive visualizations.

## ✨ Features

- **Analytics Dashboard**
  - Activity overview (distance, runs, pace)
  - Heart rate zone analysis
  - Pace distribution charts
  - Monthly progression tracking

- **Interactive Maps**
  - Activity route visualization
  - Multi-activity overlay
  - Start/end markers
  - Elevation profiles

## 🚀 Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Set Strava API credentials in .env:
You can find those in your Strava account settings.

```bash
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
```
3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py
```
## 🔧 Tech Stack 
- Streamlit (UI)
- Plotly (Charts)
- Folium (Maps)
- Pandas (Data)

## 📝 License  
This project is licensed under the Apache License 2.0 - see the LICENSE file for details.