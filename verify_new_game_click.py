from playwright.sync_api import sync_playwright, expect
import os

# Configuration
BASE_URL = "http://127.0.0.1:5173"
SCREENSHOT_DIR = "/home/jules/verification"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            print("Navigating to the main menu...")
            page.goto(BASE_URL)

            # Wait for the main menu to be fully loaded
            expect(page.locator("h1:has-text('SHADOWFALL CHRONICLES')")).to_be_visible(timeout=10000)
            print("Main menu loaded.")

            # Take a screenshot of the main menu
            screenshot_path_before = os.path.join(SCREENSHOT_DIR, "verify_click_before.png")
            page.screenshot(path=screenshot_path_before)
            print(f"Screenshot taken before click: {screenshot_path_before}")

            # Click the "New Game" button
            print("Clicking 'New Game' button...")
            page.locator("button:has-text('New Game')").click()
            print("'New Game' button clicked.")

            # Wait for the Character Creation screen to appear by looking for its title
            creation_title_locator = page.locator("h2:has-text('Step 1: Choose your Kingdom')")
            expect(creation_title_locator).to_be_visible(timeout=5000)
            print("Character Creation screen loaded successfully.")

            # Take a screenshot of the success state
            screenshot_path_success = os.path.join(SCREENSHOT_DIR, "verify_click_success.png")
            page.screenshot(path=screenshot_path_success)
            print(f"Verification successful! Screenshot: {screenshot_path_success}")

        except Exception as e:
            print(f"An error occurred during verification: {e}")
            screenshot_path_failure = os.path.join(SCREENSHOT_DIR, "verify_click_failure.png")
            page.screenshot(path=screenshot_path_failure)
            print(f"Failure screenshot saved to {screenshot_path_failure}")
            raise # Re-raise the exception to fail the step

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
