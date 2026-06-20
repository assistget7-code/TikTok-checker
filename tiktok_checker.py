import asyncio
import os
from playwright.async_api import async_playwright

# This runs the async function in a sync context for Flask
def check_credentials(email: str, password: str) -> dict:
    try:
        return asyncio.run(_check_credentials_async(email, password))
    except RuntimeError:
        # If running in an event loop already
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(_check_credentials_async(email, password))

async def _check_credentials_async(email: str, password: str) -> dict:
    async with async_playwright() as p:
        # Launch browser in headless mode (no UI)
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # Go to TikTok login page
            await page.goto("https://www.tiktok.com/login/email", timeout=30000)
            
            # Wait for the page to load
            await page.wait_for_load_state("networkidle")
            
            # Fill in email
            await page.fill('input[type="email"]', email)
            
            # Fill in password
            await page.fill('input[type="password"]', password)
            
            # Click login button
            await page.click('button[type="submit"]')
            
            # Wait for response (5-10 seconds)
            await page.wait_for_timeout(8000)
            
            # Check current URL to determine login status
            current_url = page.url
            
            if "feed" in current_url or "following" in current_url or "user" in current_url:
                return {
                    "success": True,
                    "status": "valid",
                    "message": "Credentials are valid",
                    "account": {"username": email}
                }
            else:
                # Check for error messages on the page
                error_text = await page.text_content('.error-message, .error, [class*="error"]')
                if error_text and "password" in error_text.lower():
                    return {
                        "success": False,
                        "status": "bad_password",
                        "message": "Incorrect password"
                    }
                elif error_text and "captcha" in error_text.lower():
                    return {
                        "success": False,
                        "status": "captcha_required",
                        "message": "CAPTCHA required. Please try again later."
                    }
                else:
                    return {
                        "success": False,
                        "status": "error",
                        "message": "Login failed. TikTok may have blocked this request."
                    }
                
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "message": f"Error: {str(e)[:100]}"
            }
        finally:
            await browser.close()
