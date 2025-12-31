from fastapi import FastAPI
from routes import pipeline, upload, analysis

# Create the FastAPI application
app = FastAPI(
    title="Log Analysis API",
    description="Forensics log analysis with automated pipeline",
    version="1.0"
)

# Include routes
app.include_router(pipeline.router, prefix="/api/pipeline")
app.include_router(upload.router, prefix="/api")
app.include_router(analysis.router, prefix="/api/analysis")

@app.get("/")
def root():
    return {"message": "Forensics Analysis API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
