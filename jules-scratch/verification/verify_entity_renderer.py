from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("file:///app/player_interface/dist/index.html")
        page.wait_for_selector("text=Playing as: Jules")
        page.screenshot(path="jules-scratch/verification/verification.png")
        browser.close()

run()
