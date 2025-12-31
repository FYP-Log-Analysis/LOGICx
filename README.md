# LOGIC - Single-Container Deployment

This project packages FastAPI (backend) and Streamlit (frontend) behind Nginx in one container.

## Build
```
docker build -t logic-all-in-one .
```

## Run
```
docker run \
	-p 80:80 \
	--env-file .env \
	-e API_BASE_URL=http://localhost:8000/api/pipeline \
	-e ANALYSIS_API_URL=http://localhost:8000/api/analysis \
	logic-all-in-one
```

- UI: http://localhost
- API: http://localhost/api/

## Notes
- Nginx proxies `/api/` to uvicorn on 8000 and `/` to Streamlit on 8501.
- Set `GROQ_API_KEY` (and other envs) in `.env` before running.
- To persist data: `-v $(pwd)/data:/app/data`.