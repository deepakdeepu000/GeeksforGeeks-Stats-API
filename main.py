"""
GeeksforGeeks Profile API - Main Application

This FastAPI application exposes endpoints to retrieve user profile data,
solved problems statistics, and detailed problem lists from GeeksforGeeks.
"""

import uvicorn
from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Literal
from contextlib import asynccontextmanager

# Internal imports
from scraper import get_gfg_data, fetch_user_profile, fetch_problem_list, close_browser
from svg import generate_stats_svg

# ==================== Lifecycle Management ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    try:
        yield
    finally:
        # Ensures the Playwright/Selenium browser instance closes on app exit
        await close_browser()

app = FastAPI(
    title="GeeksforGeeks Scraper API",
    description="API to scrape GeeksforGeeks user profiles, stats, and solved problems.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js or other frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Pydantic Models ====================

class UserProfile(BaseModel):
    userName: str = Field(..., description="GeeksforGeeks username")
    fullName: str = Field(default="", description="User's full name")
    designation: str = Field(default="", description="User's designation/title")
    codingScore: int = Field(default=0, description="Total coding score")
    problemsSolved: int = Field(default=0, description="Total problems solved")
    instituteRank: int = Field(default=0, description="Rank in institute")
    articlesPublished: int = Field(default=0, description="Number of articles published")
    potdStreak: int = Field(default=0, description="Current POTD streak")
    longestStreak: int = Field(default=0, description="Longest POTD streak achieved")
    potdsSolved: int = Field(default=0, description="Total POTDs solved")

class UserStats(BaseModel):
    userName: str
    School: int = 0
    Basic: int = 0
    Easy: int = 0
    Medium: int = 0
    Hard: int = 0
    totalProblemsSolved: int = 0

class Problem(BaseModel):
    question: str
    questionUrl: str

class SolvedProblems(BaseModel):
    userName: str
    problemsByDifficulty: Dict[str, int]
    Problems: Dict[str, List[Problem]]

# ==================== API Endpoints ====================

@app.get("/", tags=["System"])
def health_check():
    return {"status": "ok", "service": "GFG Scraper"}

@app.get("/docs", include_in_schema=False)
def custom_docs():
    from docs import get_custom_docs_html
    return Response(content=get_custom_docs_html(), media_type="text/html")

@app.get("/profile/{userName}", tags=["User Data"], response_model=UserProfile)
async def get_user_profile_endpoint(userName: str):
    """Get comprehensive profile info: Score, Rank, and Streaks."""
    data = await fetch_user_profile(userName)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.get("/stats/{userName}", tags=["User Data"])
async def get_user_stats_endpoint(
    userName: str,
    format: Literal["json", "svg"] = Query("json", description="Output format")
):
    """Get problem solving stats broken down by difficulty. Supports JSON or SVG."""
    data = await get_gfg_data(userName)
    
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])

    if format == "svg":
        svg_content = generate_stats_svg(data)
        return Response(
            content=svg_content, 
            media_type="image/svg+xml", 
            headers={"Cache-Control": "public, max-age=14400"}
        )
        
    return data

@app.get("/problems/{userName}", tags=["Problem Lists"], response_model=SolvedProblems)
async def get_solved_problems_endpoint(userName: str):
    """Get a detailed list of ALL solved problems with URLs."""
    data = await fetch_problem_list(userName)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.get("/{userName}", tags=["Widgets"])
async def get_stats_card(userName: str):
    """Direct SVG Stats Card endpoint for GitHub READMEs."""
    data = await get_gfg_data(userName)
    if "error" in data:
         raise HTTPException(status_code=404, detail=data["error"])
         
    svg_content = generate_stats_svg(data)
    return Response(
        content=svg_content, 
        media_type="image/svg+xml", 
        headers={"Cache-Control": "public, max-age=14400"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
