# LOGIC Dashboard

A **Streamlit-based dashboard** for the LOGIC log analysis and threat detection system.

## Features

### 🏠 Overview Dashboard
- Real-time system status and metrics
- Recent anomaly alerts
- Quick system health indicators

### 📊 Anomaly Analysis
- Interactive timeline of anomaly detections
- Anomaly score distribution charts
- Detailed anomaly data tables

### 🔍 Sigma Detection Results
- Security rule detection results
- Severity-based filtering and visualization
- Timeline analysis of threats

### 📈 Log Statistics
- Processing statistics by log source
- Data size and event count metrics
- Visual breakdowns of log data

### ⚙️ Pipeline Control
- Manual pipeline execution
- API status monitoring
- Real-time pipeline status updates

## Quick Start

### Using Docker (Recommended)
```bash
# Build and start the dashboard
docker-compose up -d dashboard

# Access at http://localhost:8501
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run main.py
```

## Architecture

```
dashboard/
├── main.py                 # Main dashboard application
├── pages/                  # Individual dashboard pages
│   ├── log_stats.py       # Log statistics page
│   └── sigma_detection.py # Sigma detection page
├── utils/                  # Utility modules
│   └── api_client.py      # API communication
├── .streamlit/            # Streamlit configuration
│   └── config.toml        # Dashboard theme and settings
├── Dockerfile             # Container configuration
└── requirements.txt       # Python dependencies
```

## API Integration

The dashboard integrates with the LOGIC API for:
- Pipeline execution triggers
- Real-time data fetching
- System status monitoring

## Data Sources

- **Anomaly Detection**: `/data/detection_results/isolation_forest_scores.json`
- **Log Statistics**: `/data/processed/json/*.json`
- **Sigma Results**: Future integration with Sigma analysis output

## Configuration

Dashboard settings can be modified in [.streamlit/config.toml](.streamlit/config.toml):
- Theme colors
- Server settings
- Performance options

## Why Streamlit?

✅ **Perfect for Data Science**: Built specifically for data analysis dashboards  
✅ **Rapid Development**: 10x faster than React for analytical interfaces  
✅ **Python Native**: Seamless integration with existing Python pipeline  
✅ **Rich Visualizations**: Built-in support for Plotly, charts, and metrics  
✅ **Real-time Updates**: Automatic data refresh and interactive widgets  
✅ **Minimal Complexity**: Single technology stack, easy maintenance
