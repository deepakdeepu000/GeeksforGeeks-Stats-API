
import re
import asyncio
import os
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Playwright

# Configuration
# Ensure BROWSERLESS_TOKEN is in your .env or environment variables
BROWSERLESS_TOKEN = os.environ.get("BROWSERLESS_TOKEN", "")
BROWSER_URL = f"wss://chrome.browserless.io?token={BROWSERLESS_TOKEN}"

GFG_BASE_URL = "https://www.geeksforgeeks.org/profile"
TIMEOUT_STD = 45000 
TIMEOUT_SHORT = 30000

# Global State
_PLAYWRIGHT: Optional[Playwright] = None
_BROWSER: Optional[Browser] = None
_LOCK = asyncio.Lock()
_REQUEST_COUNT = 0
_MAX_REQUESTS_PER_BROWSER = 100

async def get_browser() -> Browser:
    """Connects to Browserless via CDP and reuses the connection."""
    global _PLAYWRIGHT, _BROWSER, _REQUEST_COUNT
    
    async with _LOCK:
        # Refresh browser connection after threshold to keep session clean
        if _BROWSER and _REQUEST_COUNT >= _MAX_REQUESTS_PER_BROWSER:
            await _BROWSER.close()
            _BROWSER = None
            _REQUEST_COUNT = 0
        
        if _BROWSER is None:
            print("🚀 Connecting to Remote Browserless...")
            if _PLAYWRIGHT is None:
                _PLAYWRIGHT = await async_playwright().start()
            
            # Browserless uses Chromium for its CDP interface
            _BROWSER = await _PLAYWRIGHT.chromium.connect_over_cdp(BROWSER_URL)
            
        _REQUEST_COUNT += 1
    return _BROWSER

async def close_browser():
    """Cleanup resources on shutdown."""
    global _PLAYWRIGHT, _BROWSER
    async with _LOCK:
        if _BROWSER:
            await _BROWSER.close()
            _BROWSER = None
        if _PLAYWRIGHT:
            await _PLAYWRIGHT.stop()
            _PLAYWRIGHT = None
    print("🛑 Remote Browser Disconnected")

# --- Scraper Functions ---

async def fetch_user_profile(username: str) -> Dict[str, Any]:
    url = f"{GFG_BASE_URL}/{username}"
    browser = await get_browser()
    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_SHORT)
        if "auth" in page.url:
            return {"error": "User not found or private profile", "userName": username}

        data = {
            "userName": username,
            "fullName": username,
            "designation": "",
            "codingScore": 0,
            "problemsSolved": 0,
            "instituteRank": 0,
            "articlesPublished": 0,
            "potdStreak": 0,
            "longestStreak": 0,
            "potdsSolved": 0
        }

        # Safe extraction
        name = await page.locator(".NewProfile_name__N_Nlw").first.text_content() if await page.locator(".NewProfile_name__N_Nlw").count() > 0 else username
        data["fullName"] = name.strip()
        
        designation = await page.locator(".NewProfile_designation__fujtZ").first.text_content() if await page.locator(".NewProfile_designation__fujtZ").count() > 0 else ""
        data["designation"] = designation.strip()

        # Score Cards
        cards = page.locator(".ScoreContainer_score-card__zI4vG")
        for i in range(await cards.count()):
            card = cards.nth(i)
            label = await card.locator(".ScoreContainer_label__aVpLE").text_content()
            val = await card.locator(".ScoreContainer_value__7yy7h").text_content()
            if label and val and val.strip() != "__":
                num = int(val.strip())
                if "Coding Score" in label: data["codingScore"] = num
                elif "Problems Solved" in label: data["problemsSolved"] = num
                elif "Institute Rank" in label: data["instituteRank"] = num
                elif "Articles Published" in label: data["articlesPublished"] = num

        return data
    except Exception as e:
        return {"error": str(e), "userName": username}
    finally:
        await page.close()
        await context.close()

async def get_gfg_data(username: str) -> Dict[str, Any]:
    """Retrieves quick stats by difficulty."""
    url = f"{GFG_BASE_URL}/{username}?tab=activity"
    browser = await get_browser()
    context = await browser.new_context()
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_SHORT)
        navbar = page.locator('.ProblemNavbar_head__6ptDV')
        if await navbar.count() == 0:
            return {"error": "Stats not found", "userName": username}

        text = await navbar.inner_text()
        numbers = re.findall(r'\((\d+)\)', text)
        tags = ["School", "Basic", "Easy", "Medium", "Hard"]
        
        stats = {tags[i]: int(numbers[i]) for i in range(min(len(numbers), 5))}
        return {
            "userName": username,
            "totalProblemsSolved": sum(stats.values()),
            "problemsByDifficulty": stats
        }
    except Exception as e:
        return {"error": str(e), "userName": username}
    finally:
        await page.close()
        await context.close()
        
        
async def fetch_problem_list(username: str) -> Dict[str, Any]:
    """
    Scrapes the detailed list of solved problems for each difficulty level.
    This function interacts with UI tabs to load dynamic content.

    Args:
        username (str): The GeeksforGeeks username.

    Returns:
        Dict: A dictionary mapping difficulty levels to lists of problem objects.
    """
    url = f"{GFG_BASE_URL}/{username}?tab=activity"

    async with async_playwright() as p:
        try:
            # browser, page = await _get_browser_page(p)
            browser = await get_browser() 
            context = await browser.new_context()       
            page = await context.new_page()
            # Use domcontentloaded for faster initial render, we wait for specific elements later
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_STD)

            difficulties = ["SCHOOL", "BASIC", "EASY", "MEDIUM", "HARD"]
            all_problems = {}
            total_problems = {}
            
            # Check if the main navbar exists before iterating
            if await page.locator(".ProblemNavbar_head__6ptDV").count() == 0:
                 return {"error": "Activity tab content not found", "userName": username}

            for diff in difficulties:
                # Selector for the specific difficulty tab (e.g., "MEDIUM (50)")
                tab_selector = f".ProblemNavbar_head_nav__OqbEt:has-text('{diff}')"
                tab = page.locator(tab_selector)
                
                # Default to 0 if tab not found
                count = 0
                if await tab.count() > 0:
                    tab_text = await tab.inner_text()
                    # Extract count from text like "MEDIUM (12)"
                    match = re.search(r'\((\d+)\)', tab_text)
                    if match:
                        count = int(match.group(1))
                
                total_problems[diff.capitalize()] = count

                # If count is 0, skip clicking and extraction
                if count == 0:
                    all_problems[diff.capitalize()] = []
                    continue

                # Click the tab to load the problem list
                await tab.click()

                # Selector for the list of problems
                list_selector = "ul.SolvedProblemsContainer_problemList__8Ua09"
                
                try:
                    # Wait for the list to appear in the DOM
                    await page.wait_for_selector(list_selector, timeout=TIMEOUT_SHORT)
                    
                    # Optimization: Use page.evaluate to extract all links in one JS execution.
                    # This is significantly faster than iterating through locators in Python.
                    problems = await page.evaluate("""
                        (selector) => {
                            const container = document.querySelector(selector);
                            if (!container) return [];
                            const links = container.querySelectorAll("li a");
                            return Array.from(links).map(a => ({
                                question: a.innerText.trim(),
                                questionUrl: a.href
                            }));
                        }
                    """, list_selector)
                    
                    all_problems[diff.capitalize()] = problems

                except Exception:
                    # Fallback if list selector doesn't appear (e.g., UI glitch or loading error)
                    print(f"Warning: Could not load problem list for {diff}")
                    all_problems[diff.capitalize()] = []

            return {
                "userName": username,
                "problemsByDifficulty": total_problems,
                "Problems": all_problems
            }

        except Exception as e:
            return {"error": f"Failed to fetch problem list: {str(e)}", "userName": username}
        finally:
             await context.close() 

