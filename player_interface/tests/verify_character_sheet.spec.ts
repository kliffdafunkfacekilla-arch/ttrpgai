
// player_interface/tests/verify_character_sheet.spec.ts
import { test, expect } from '@playwright/test';
import * as fs from 'fs';

test('should create a character and display all character sheet sections', async ({ page }) => {
  // Increase the default timeout for this complex test
  test.setTimeout(60000);

  // Listen for all console events and log them to the test's output
  page.on('console', msg => {
      console.log(`Browser Console [${msg.type()}]: ${msg.text()}`);
  });

  try {
    // 1. Navigate to the main menu
    await page.goto('http://localhost:5173');
    // --- FIX: Use the correct title ---
    await expect(page).toHaveTitle(/player_interface/);

    // 2. Start a new game to enter character creation
    await page.getByRole('button', { name: 'New Game' }).click();

    // Wait for the creation screen to load, identified by the first step's title
    await expect(page.getByRole('heading', { name: 'Step 1: Choose your Kingdom' })).toBeVisible({ timeout: 10000 });

    // --- AUTOMATE CHARACTER CREATION ---

    // Step 1: Kingdom
    await page.getByRole('button', { name: 'Mammal' }).click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 2: Features (8 steps)
    for (let i = 1; i <= 8; i++) {
        await expect(page.getByRole('heading', { name: `Step 2: Features (${i} / 8)` })).toBeVisible();
        // Click the first available feature choice
        await page.locator('.stone-panel button').first().click();
        await page.getByRole('button', { name: 'Next' }).click();
    }

    // Step 3: Origin
    await expect(page.getByRole('heading', { name: 'Step 3: Choose Origin' })).toBeVisible();
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 4: Childhood
    await expect(page.getByRole('heading', { name: 'Step 4: Choose Childhood' })).toBeVisible();
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 5: Coming of Age
    await expect(page.getByRole('heading', { name: 'Step 5: Choose Coming of Age' })).toBeVisible();
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 6: Training
    await expect(page.getByRole('heading', { name: 'Step 6: Choose Training' })).toBeVisible();
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 7: Devotion
    await expect(page.getByRole('heading', { name: 'Step 7: Choose Devotion' })).toBeVisible();
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 8: Ability School
    await expect(page.getByRole('heading', { name: 'Step 8: Choose Ability School' })).toBeVisible();
    // Click the first school that is NOT disabled
    await page.locator('button.stone-button:not([disabled])').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 9: Talent
    await expect(page.getByRole('heading', { name: 'Step 9: Choose Ability Talent' })).toBeVisible({ timeout: 15000 }); // Talent fetching can be slow
    // Wait for talents to be loaded and click the first one
    await page.locator('.stone-panel button').first().waitFor();
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 10: Name
    await expect(page.getByRole('heading', { name: 'Step 10: Choose Your Name' })).toBeVisible();
    await page.getByPlaceholder('Enter character name').fill('Jules the Tester');
    await page.getByRole('button', { name: 'Next' }).click();

    // Step 11: Review
    await expect(page.getByRole('heading', { name: 'Step 11: Review & Create' })).toBeVisible();
    // Select the capstone feature required to enable creation
    await page.locator('.stone-panel button').first().click();
    await page.getByRole('button', { name: 'Create Character' }).click();

    // --- VERIFY IN-GAME ---

    // Wait for the game world to load by looking for the map container
    await expect(page.locator('.map-container')).toBeVisible({ timeout: 10000 });

    // Press 'c' to open the character sheet
    await page.keyboard.press('c');

    // Wait for the sheet to appear
    await expect(page.getByRole('heading', { name: "Jules the Tester's Character Sheet" })).toBeVisible();

    // --- VERIFY NEW SECTIONS EXIST ---
    await expect(page.getByRole('heading', { name: 'Talents' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Equipment' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Status Effects' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Injuries' })).toBeVisible();

    // Final verification screenshot
    await page.screenshot({ path: '/home/jules/verification/final_character_sheet.png', fullPage: true });

  } catch (error) {
    console.error(error);
    await page.screenshot({ path: '/home/jules/verification/failure_screenshot_creation_flow.png', fullPage: true });
    // --- FIX: Use imported fs module ---
    const html = await page.content();
    fs.writeFileSync('/home/jules/verification/failure_page_creation_flow.html', html);
    throw error; // Re-throw the error to fail the test
  }
});
