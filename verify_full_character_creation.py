import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Capture and print console logs
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        try:
            print("Assuming backend services are running...")
            await page.goto("http://localhost:5173", timeout=15000)

            print("Navigated to the main menu.")
            await expect(page.locator("h1:text('SHADOWFALL CHRONICLES')")).to_be_visible(timeout=10000)

            await page.click("button:text('New Game')")
            print("Clicked 'New Game'.")

            await expect(page.locator("h2:text('Choose your Kingdom')")).to_be_visible(timeout=10000)

            await page.click("button:text('Mammal')")
            print("Selected Kingdom: Mammal.")
            await page.click("button:text('Next')")

            # Features F1-F8
            for i in range(1, 9):
                await expect(page.locator(f"h3:text('Choose your F{i} Feature')")).to_be_visible(timeout=10000)
                await page.locator(".stone-panel button").first.click()
                print(f"Selected first choice for feature F{i}.")
                await page.click("button:text('Next')")

            # Origin
            await expect(page.locator("h2:text('Choose Origin')")).to_be_visible(timeout=10000)
            await page.locator(".stone-panel button").first.click()
            print("Selected first Origin.")
            await page.click("button:text('Next')")

            # Childhood
            await expect(page.locator("h2:text('Choose Childhood')")).to_be_visible(timeout=10000)
            await page.locator(".stone-panel button").first.click()
            print("Selected first Childhood.")
            await page.click("button:text('Next')")

            # Coming of Age
            await expect(page.locator("h2:text('Choose Coming of Age')")).to_be_visible(timeout=10000)
            await page.locator(".stone-panel button").first.click()
            print("Selected first Coming of Age.")
            await page.click("button:text('Next')")

            # Training
            await expect(page.locator("h2:text('Choose Training')")).to_be_visible(timeout=10000)
            await page.locator(".stone-panel button").first.click()
            print("Selected first Training.")
            await page.click("button:text('Next')")

            # Devotion
            await expect(page.locator("h2:text('Choose Devotion')")).to_be_visible(timeout=10000)
            await page.locator(".stone-panel button").first.click()
            print("Selected first Devotion.")
            await page.click("button:text('Next')")

            # Ability School
            await expect(page.locator("h2:text('Choose Ability School')")).to_be_visible(timeout=10000)
            await page.locator("button:not([disabled])").nth(1).click()
            print("Selected first available Ability School.")
            await page.click("button:text('Next')")

            # Talent
            await expect(page.locator("h2:text('Choose Ability Talent')")).to_be_visible(timeout=15000)
            await page.locator(".stone-panel button").first.click()
            print("Selected first available Talent.")
            await page.click("button:text('Next')")

            # Name
            await expect(page.locator("h2:text('Choose Your Name')")).to_be_visible(timeout=10000)
            await page.fill("input[type='text']", "Jules")
            print("Entered character name and proceeded to review.")
            await page.click("button:text('Next')")

            # Review
            await expect(page.locator("h2:text('Review & Create')")).to_be_visible(timeout=10000)
            await page.locator("h4:text('Capstone') + div button").first.click()
            print("Selected first Capstone (F9) choice.")

            await page.click("button:text('Create Character')")
            print("Clicked 'Create Character'.")

            # Check for the exploration screen
            await expect(page.locator("h3:text('Event Log')")).to_be_visible(timeout=25000)
            print("Successfully navigated to the exploration screen!")

        except Exception as e:
            print(f"An error occurred: {e}")
            await page.screenshot(path="/home/jules/verification/character_creation_error.png")
            print("Error screenshot saved to /home/jules/verification/character_creation_error.png")
            raise e
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
