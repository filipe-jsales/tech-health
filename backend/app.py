"""
Main application file for Tech Health API
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from api.github import router as github_router
from analyzer.code_analyzer import router as analyzer_router
from report_generator.generator import router as report_router

load_dotenv()

app = FastAPI(
    title="Tech Health API",
    description="API for analyzing GitHub repositories and generating tech health reports",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(github_router, prefix="/api/github", tags=["GitHub"])
app.include_router(analyzer_router, prefix="/api/analyze", tags=["Code Analysis"])
app.include_router(report_router, prefix="/api/report", tags=["Report Generation"])

@app.get("/", tags=["Health Check"])
async def root():
    """
    Root endpoint for health check
    """
    return {"status": "healthy", "version": "0.1.0"}

@app.get("/api/info", tags=["Information"])
async def get_info():
    """
    Get application information
    """
    return {
        "name": "Tech Health",
        "description": "A tool to analyze GitHub repositories and generate tech health reports",
        "endpoints": {
            "github": "/api/github",
            "analyze": "/api/analyze",
            "report": "/api/report"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)