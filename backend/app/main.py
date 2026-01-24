# FastAPI entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
app=FastAPI(title=settings.PROJECT_NAME)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
  return {"status": "ok", "project": settings.PROJECT_NAME}