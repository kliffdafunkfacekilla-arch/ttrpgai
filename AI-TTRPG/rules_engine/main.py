from fastapi import FastAPI

app = FastAPI()

ABILITY_DATA = {
    "Strength": {},
    "Dexterity": {},
    "Constitution": {},
    "Intelligence": {},
    "Wisdom": {},
    "Charisma": {}
}

@app.get("/v1/lookup/all_ability_schools")
def get_all_ability_schools():
    return list(ABILITY_DATA.keys())
