from fastapi import FastAPI

app = FastAPI(
    title="Shiplog",
    description="AI-powered build-in-public automation for developers",
    version="0.1.0",
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}