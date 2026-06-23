from fastapi import FastAPI
from app.api.webhooks import router as webhook_router

app = FastAPI(
    title="Shiplog",
    description="AI-powered build-in-public automation for developers",
    version="0.1.0",
)

app.include_router(webhook_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}