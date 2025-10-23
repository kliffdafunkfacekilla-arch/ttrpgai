# AI-TTRPG: Rules Engine Module

This is the stateless "calculator" for the Fulcrum System. It knows all the rules and performs all calculations.

## How to Install and Run

1.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    ```

2.  **Activate the Environment:**
    * **Windows:** `.\\venv\\Scripts\\activate`
    * **Mac/Linux:** `source venv/bin/activate`

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create the Data Files:**
    * Create the `/data/` folder.
    * Copy the JSON data provided in the plan into the four files:
        * `data/stats_and_skills.json`
        * `data/kingdom_features.json`
        * `data/talents.json`
        * `data/abilities.json`

5.  **Run the Server:**
    ```bash
    uvicorn main:app --reload
    ```
    * The `--reload` flag means the server will auto-restart when you save changes.

6.  **Test the API:**
    * Open your browser and go to `http://127.0.0.1:8000/docs`
    * You will see a full, interactive API documentation page. You can test every endpoint from here.
