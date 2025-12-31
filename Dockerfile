# Multi-process container: FastAPI (uvicorn) + Streamlit + Nginx reverse proxy
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \ 
    && apt-get install -y --no-install-recommends \
       build-essential \
       nginx \
       supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Nginx and Supervisor configs
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisor.conf /etc/supervisor/conf.d/supervisor.conf

# Default ports and API URLs (override in runtime env)
ENV API_PORT=8000 \
    STREAMLIT_PORT=8501 \
    API_BASE_URL=http://localhost:8000/api/pipeline \
    ANALYSIS_API_URL=http://localhost:8000/api/analysis

EXPOSE 80

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisor.conf"]
