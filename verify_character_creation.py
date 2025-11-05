
import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto("http://localhost:5173", timeout=60000)
            print("Successfully navigated to http://localhost:5173")

            # Click the "New Game" button
            new_game_button_selector = "button:has-text('New Game')"
            print(f"Waiting for selector: '{new_game_button_selector}'")
            await page.wait_for_selector(new_game_button_selector, timeout=15000)
            await page.click(new_game_button_selector)
            print("Clicked 'New Game' button.")

            # Wait for the next screen to load and check for the "Next" button
            next_button_selector = "button:has-text('Next')"
            print(f"Waiting for selector: '{next_button_selector}'")
            await expect(page.locator(next_button_selector)).to_be_visible(timeout=15000)
            print("Character creation screen loaded successfully, 'Next' button is visible.")

            # Take a final screenshot
            screenshot_path = "/home/jules/verification/character_creation_screen.png"
            await page.screenshot(path=screenshot_path)
            print(f"Successfully captured screenshot to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
            debug_screenshot_path = "/home/jules/verification/debug_creation_failure.png"
            await page.screenshot(path=debug_screenshot_path)
            print(f"Saved debug screenshot to {debug_screenshot_path}")

        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
