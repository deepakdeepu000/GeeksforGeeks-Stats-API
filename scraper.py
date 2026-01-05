import re
import asyncio
import os
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Playwright, Error as PlaywrightError


# Configuration
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
_MAX_REQUESTS_PER_BROWSER = 50  # Lower threshold for stability

async def is_browser_connected(browser: Browser) -> bool:
    """Check if browser is still connected and usable"""
    try:
        # Try to get contexts - will fail if browser is closed
        contexts = browser.contexts
        return len(contexts) >= 0  # If we can access contexts, browser is alive
    except Exception:
        return False

async def get_browser() -> Browser:
    """Connects to Browserless via CDP with health check and auto-recovery"""
    global _PLAYWRIGHT, _BROWSER, _REQUEST_COUNT
    
    async with _LOCK:
        # Check if browser needs refresh
        needs_new_browser = (
            _BROWSER is None or
            _REQUEST_COUNT >= _MAX_REQUESTS_PER_BROWSER or
            not await is_browser_connected(_BROWSER)
        )
        
        if needs_new_browser:
            # Clean up old browser if exists
            if _BROWSER:
                try:
                    await _BROWSER.close()
                except Exception as e:
                    print(f"⚠️ Error closing old browser: {e}")
                _BROWSER = None
            
            _REQUEST_COUNT = 0
            
            # Create new connection
            print("🚀 Connecting to Remote Browserless...")
            try:
                if _PLAYWRIGHT is None:
                    _PLAYWRIGHT = await async_playwright().start()
                
                _BROWSER = await _PLAYWRIGHT.chromium.connect_over_cdp(
                    BROWSER_URL,
                    timeout=30000  # 30 second connection timeout
                )
                print("✅ Browser connected successfully")
            except Exception as e:
                print(f"❌ Failed to connect to browser: {e}")
                _BROWSER = None
                raise
        
        _REQUEST_COUNT += 1
    
    return _BROWSER

async def close_browser():
    """Cleanup resources on shutdown"""
    global _PLAYWRIGHT, _BROWSER, _REQUEST_COUNT
    async with _LOCK:
        if _BROWSER:
            try:
                await _BROWSER.close()
            except Exception as e:
                print(f"⚠️ Error during browser cleanup: {e}")
            _BROWSER = None
        
        if _PLAYWRIGHT:
            try:
                await _PLAYWRIGHT.stop()
            except Exception as e:
                print(f"⚠️ Error during playwright cleanup: {e}")
            _PLAYWRIGHT = None
        
        _REQUEST_COUNT = 0
    print("🛑 Remote Browser Disconnected")

# --- Scraper Functions with Better Error Handling ---

async def fetch_user_profile(username: str) -> Dict[str, Any]:
    """Fetch user profile with retry logic"""
    url = f"{GFG_BASE_URL}/{username}"
    
    max_retries = 2
    for attempt in range(max_retries):
        context = None
        page = None
        
        try:
            browser = await get_browser()
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()

            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_SHORT)
            
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

            # Safe extraction with null checks
            if await page.locator(".NewProfile_name__N_Nlw").count() > 0:
                name = await page.locator(".NewProfile_name__N_Nlw").first.text_content()
                data["fullName"] = name.strip() if name else username
            
            if await page.locator(".NewProfile_designation__fujtZ").count() > 0:
                designation = await page.locator(".NewProfile_designation__fujtZ").first.text_content()
                data["designation"] = designation.strip() if designation else ""

            # Score Cards
            cards = page.locator(".ScoreContainer_score-card__zI4vG")
            for i in range(await cards.count()):
                card = cards.nth(i)
                label = await card.locator(".ScoreContainer_label__aVpLE").text_content()
                val = await card.locator(".ScoreContainer_value__7yy7h").text_content()
                if label and val and val.strip() != "__":
                    try:
                        num = int(val.strip())
                        if "Coding Score" in label: data["codingScore"] = num
                        elif "Problems Solved" in label: data["problemsSolved"] = num
                        elif "Institute Rank" in label: data["instituteRank"] = num
                        elif "Articles Published" in label: data["articlesPublished"] = num
                    except ValueError:
                        continue

            return data
            
        except PlaywrightError as e:
            error_msg = str(e)
            if "Target" in error_msg and "closed" in error_msg and attempt < max_retries - 1:
                print(f"⚠️ Browser connection lost, retrying... (attempt {attempt + 1}/{max_retries})")
                # Force browser reconnection
                global _BROWSER
                _BROWSER = None
                await asyncio.sleep(1)  # Brief delay before retry
                continue
            return {"error": f"Browser error: {error_msg}", "userName": username}
        except Exception as e:
            return {"error": f"Scraping failed: {str(e)}", "userName": username}
        finally:
            # Always clean up context and page
            try:
                if page:
                    await page.close()
                if context:
                    await context.close()
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")

async def get_gfg_data(username: str) -> Dict[str, Any]:
    """Retrieves quick stats by difficulty with retry logic"""
    url = f"{GFG_BASE_URL}/{username}?tab=activity"
    
    max_retries = 2
    for attempt in range(max_retries):
        context = None
        page = None
        
        try:
            browser = await get_browser()
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_SHORT)
            
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
                **stats  # Flatten stats into response
            }
            
        except PlaywrightError as e:
            error_msg = str(e)
            if "Target" in error_msg and "closed" in error_msg and attempt < max_retries - 1:
                print(f"⚠️ Browser connection lost, retrying... (attempt {attempt + 1}/{max_retries})")
                global _BROWSER
                _BROWSER = None
                await asyncio.sleep(1)
                continue
            return {"error": f"Browser error: {error_msg}", "userName": username}
        except Exception as e:
            return {"error": f"Stats fetch failed: {str(e)}", "userName": username}
        finally:
            try:
                if page:
                    await page.close()
                if context:
                    await context.close()
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")

async def fetch_problem_list(username: str) -> Dict[str, Any]:
    """Fetch problem list with retry logic"""
    url = f"{GFG_BASE_URL}/{username}?tab=activity"
    
    max_retries = 2
    for attempt in range(max_retries):
        context = None
        page = None
        
        try:
            browser = await get_browser()
            context = await browser.new_context()
            page = await context.new_page()
            
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_STD)

            difficulties = ["SCHOOL", "BASIC", "EASY", "MEDIUM", "HARD"]
            all_problems = {}
            total_problems = {}
            
            if await page.locator(".ProblemNavbar_head__6ptDV").count() == 0:
                return {"error": "Activity tab content not found", "userName": username}

            for diff in difficulties:
                tab_selector = f".ProblemNavbar_head_nav__OqbEt:has-text('{diff}')"
                tab = page.locator(tab_selector)
                
                count = 0
                if await tab.count() > 0:
                    tab_text = await tab.inner_text()
                    match = re.search(r'\((\d+)\)', tab_text)
                    if match:
                        count = int(match.group(1))
                
                total_problems[diff.capitalize()] = count

                if count == 0:
                    all_problems[diff.capitalize()] = []
                    continue

                await tab.click()
                list_selector = "ul.SolvedProblemsContainer_problemList__8Ua09"
                
                try:
                    await page.wait_for_selector(list_selector, timeout=TIMEOUT_SHORT)
                    
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
                    print(f"⚠️ Could not load problem list for {diff}")
                    all_problems[diff.capitalize()] = []

            return {
                "userName": username,
                "problemsByDifficulty": total_problems,
                "Problems": all_problems
            }
            
        except PlaywrightError as e:
            error_msg = str(e)
            if "Target" in error_msg and "closed" in error_msg and attempt < max_retries - 1:
                print(f"⚠️ Browser connection lost, retrying... (attempt {attempt + 1}/{max_retries})")
                global _BROWSER
                _BROWSER = None
                await asyncio.sleep(1)
                continue
            return {"error": f"Browser error: {error_msg}", "userName": username}
        except Exception as e:
            return {"error": f"Failed to fetch problem list: {str(e)}", "userName": username}
        finally:
            try:
                if page:
                    await page.close()
                if context:
                    await context.close()
            except Exception as e:
                print(f"⚠️ Cleanup error: {e}")




