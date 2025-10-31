# NPC Generator Service

## 1. Overview

The NPC Generator is a stateless FastAPI service designed to procedurally generate NPC (Non-Player Character) templates. It combines a set of pre-defined rules and parameters to create a wide variety of NPCs on the fly.

-   **Stateless:** The service does not have a database. It loads its generation rules from a JSON file (`generation_rules.json`) on startup.
-   **Procedural Generation:** Its core function is to generate NPC stat blocks based on a combination of inputs.

## 2. Core Responsibilities

-   **NPC Template Generation:** The service's primary responsibility is to generate a complete NPC template, including stats, skills, HP, behavior tags, and a unique ID.
-   **Rule-Based Logic:** It applies a series of rules from `generation_rules.json` to determine the final NPC. This includes:
    -   Selecting base stats based on the NPC's "kingdom" (e.g., mammal, insectoid).
    -   Applying stat modifiers based on "styles" (e.g., offense: heavy, defense: evasive).
    -   Scaling HP based on a "difficulty" rating.
    -   Assigning skill ranks based on styles and difficulty.
-   **Rules Integration:** It ensures that generated NPCs are compatible with the game's master skill list by fetching it from the `rules_engine`.

## 3. Key API Endpoints

-   `POST /v1/generate`: The sole endpoint for generating an NPC.
    -   **Request Body:** `NpcGenerationRequest` (kingdom, offense_style, defense_style, difficulty, behavior, etc.).
    -   **Process:**
        1.  Fetches the master skill list from the `rules_engine`.
        2.  Applies the logic from `generation_rules.json` to the request parameters.
        3.  Calculates final stats, skills, and HP.
        4.  Constructs and returns a complete NPC template.
    -   **Response Body:** `NpcTemplateResponse` (a full NPC stat block ready to be spawned by the `story_engine`).

## 4. Data Sources

-   `generation_rules.json`: A comprehensive JSON file that contains all the data and rules for the generation process. This includes base stats, style modifiers, HP scaling factors, and skill assignments.

## 5. Dependencies

-   **`rules_engine`:** The NPC Generator makes a critical API call on each generation request to the `rules_engine`'s `/v1/lookup/all_skills` endpoint. This ensures that the skills assigned to the generated NPC are always valid according to the current game rules, preventing data drift between the services.
