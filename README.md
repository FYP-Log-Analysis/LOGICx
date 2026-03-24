# LOGIC - Local Development and Production Run Guide

LOGIC is a Windows log forensics project with:
- FastAPI backend on port 4000
- Streamlit dashboard on port 8501
- Data processing and detection pipelines

## Prerequisites

- Python 3.9+
- pip
- Optional: PostgreSQL (only if your API/database workflows require it)

## Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create or update `.env` in the project root.

Required/commonly used values:

```env
GROQ_API_KEY=your_key_here
API_BASE_URL=http://localhost:4000
ANALYSIS_API_URL=http://localhost:4000/api/analysis
DATABASE_URL=postgresql://forensic:forensicpass@localhost:5432/fyp
```

## Run Scripts

Two launcher scripts are provided:

- `dev.sh`: starts API (with `--reload`) and dashboard for development
- `prod.sh`: starts API and dashboard without reload

Make scripts executable once:

```bash
chmod +x dev.sh prod.sh
```

Start development mode:

```bash
./dev.sh
```

Start production mode:

```bash
./prod.sh
```

## Service URLs

- Dashboard: http://localhost:8501
- API root: http://localhost:4000/
- API docs: http://localhost:4000/docs

## Optional Pipeline Commands

Run steps manually from project root:

```bash
python ingestion/src/ingest_evtx.py
python parser/src/parse_xml.py
python -m normalizer.src.normalize
python analysis/sigma_pipeline.py
python ml/ml_pipeline.py
```

## Troubleshooting

- If `streamlit` or `uvicorn` is not found, activate your virtual environment and reinstall dependencies.
- If port 4000 or 8501 is already in use, stop the conflicting process and rerun the script.
- If dashboard API checks fail, verify the backend is running at `http://localhost:4000`.