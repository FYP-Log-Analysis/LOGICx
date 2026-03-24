# API

FastAPI backend for LOGIC.

## Run Locally

From the project root:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 4000 --reload
```

API docs:

- http://localhost:4000/docs

Health endpoint:

- `GET /`

## Key Routes

- `POST /api/upload`
- `POST /api/pipeline/run`
- `POST /api/pipeline/run/{step_id}`
- `POST /api/pipeline/run-sequence`
- `GET /api/pipeline/steps`
- `POST /api/analysis/threat-insights`
- `GET /api/logs`
- `GET /api/logs/{log_type}`

## Configuration

Environment variables commonly used:

- `GROQ_API_KEY`
- `DATABASE_URL` (example: `postgresql://forensic:forensicpass@localhost:5432/fyp`)

## Notes

- API defaults to port `4000`.
- This service is documented for direct local execution.