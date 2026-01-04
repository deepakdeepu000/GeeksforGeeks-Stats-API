"""
GeeksforGeeks Profile API - Main Application

This FastAPI application exposes endpoints to retrieve user profile data,
solved problems statistics, and detailed problem lists from GeeksforGeeks.
It supports JSON output for data consumption and SVG generation for profile cards.
"""

import uvicorn
from fastapi import FastAPI, Query, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal
from contextlib import asynccontextmanager

# Internal imports
from scraper import get_gfg_data, fetch_user_profile, fetch_problem_list, close_browser
from svg import generate_stats_svg


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        await close_browser()


app = FastAPI(
    title="GeeksforGeeks Scraper API",
    description="API to scrape GeeksforGeeks user profiles, stats, and solved problems.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "GFG Scraper"}

# --- 1. User Profile & Summary ---
@app.get("/profile/{userName}", tags=["User Data"])
async def get_user_profile(userName: str):
    """
    Get comprehensive profile info: 
    Coding Score, Rank, Streaks, and overall stats.
    """
    data = await fetch_user_profile(userName)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data

@app.get("/stats/{userName}", tags=["User Data"])
async def get_user_stats(
    userName: str,
    format: Literal["json", "svg"] = Query("json", description="Output format")
    ):
    """
        Get problem solving stats broken down by difficulty.
        Supports JSON or SVG format.
    """
    
    data = await get_gfg_data(userName)
        
    if "error" in data:
         raise HTTPException(status_code=404, detail=data["error"])

    if format == "svg":
        svg_content = generate_stats_svg(data)
        # Cache SVG for 4 hours
        return Response(content=svg_content, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=14400"})
        
    return data


# --- 2. Solved Problems Details ---
@app.get("/problems/{userName}", tags=["Problem Lists"])
async def get_solved_problems(userName: str):
    """
    Get a detailed list of ALL solved problems.
    (Includes links and titles for every problem).
    """
    data = await fetch_problem_list(userName)
    if "error" in data:
        raise HTTPException(status_code=404, detail=data["error"])
    return data


# --- 3. Shortcuts / Image Links ---

@app.get("/{userName}", tags=["Widgets"])
async def get_stats_card(userName: str):
    """
    Direct endpoint for the SVG Stats Card.
    Useful for embedding in GitHub READMEs.
    """
    data = await get_gfg_data(userName)
    if "error" in data:
         # Return a generic error SVG or 404 (404 breaks broken image icons)
         raise HTTPException(status_code=404, detail=data["error"])
     
    print(data)
         
    svg_content = generate_stats_svg(data)
    return Response(content=svg_content, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=14400"})



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)

