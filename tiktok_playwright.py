import asyncio
from playwright.async_api import async_playwright

async def check_tiktok_credentials(email: str, password: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto("https://www.tiktok.com/login/email")
            await page.fill('input[name="email"]', email)
            await page.fill('input[name="password"]', password)
            await page.click('button[type="submit"]')
            
            # Wait for redirect or error
            await page.wait_for_timeout(5000)
            
            # Check if login was successful
            if "feed" in page.url or "following" in page.url:
                return {"success": True, "status": "valid", "message": "Credentials are valid"}
            else:
                # Check for error messages
                error_text = await page.text_content('.error-message') or "Login failed"
                return {"success": False, "status": "error", "message": error_text}
                
        except Exception as e:
            return {"success": False, "status": "error", "message": str(e)}
        finally:
            await browser.close()

# Wrapper function for Flask
def check_credentials(email: str, password: str) -> dict:
    return asyncio.run(check_tiktok_credentials(email, password))
