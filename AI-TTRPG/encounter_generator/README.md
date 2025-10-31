# Encounter Generator Service

## 1. Overview

The Encounter Generator is a stateless FastAPI service designed to provide pre-defined encounter templates based on a set of tags. It serves as a simple content library for the `story_engine`.

-   **Stateless:** The service has no database and loads all encounter data from JSON files on startup.
-   **Content Library:** Its primary purpose is to return structured encounter data that can be used to initiate combat or skill challenges.

## 2. Core Responsibilities

-   **Encounter Selection:** Selects a suitable encounter from its data files based on a list of input tags (e.g., `["forest", "medium", "combat"]`).
-   **Data Serving:** Returns the structured data for the selected encounter, which includes the necessary NPC template IDs for a combat encounter or the parameters for a skill challenge.

## 3. Key API Endpoints

-   `POST /v1/generate`: The sole endpoint for fetching an encounter.
    -   **Request Body:** `EncounterGenerationRequest` (a list of `tags`).
    -   **Process:** Finds and returns an encounter from its loaded data that matches the given tags.
    -   **Response Body:** `EncounterResponse` (details of the encounter, such as a list of NPC template IDs to be spawned).

## 4. Data Sources

-   `combat_encounters.json`: Contains pre-defined combat encounters, including the specific NPC templates involved.
-   `skill_challenges.json`: (Not fully utilized) Intended to contain definitions for non-combat skill challenges.

## 5. Current Status & Dependencies

-   The service is functionally complete for its simple, defined scope.
-   The Encounter Generator is a self-contained service and has **no dependencies** on other services.
