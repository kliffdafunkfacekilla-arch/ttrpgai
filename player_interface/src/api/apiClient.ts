// src/api/apiClient.ts
import {
  type CharacterContextResponse,
  type InteractionRequest,
  type InteractionResponse,
  type CombatEncounterResponse,
  // --- MODIFIED: Renamed CombatActionRequest to align with story_engine ---
  type PlayerActionRequest as CombatActionRequest,
  type CharacterCreateRequest,
  type KingdomFeaturesData,
  type TalentInfo,
  // --- ADDED: New types needed for the missing functions ---
  type LocationContextResponse,
  type PlayerActionResponse,
  type CombatStartRequestPayload,
  type PlayerActionRequestPayload,
} from "../types/apiTypes";

// --- Base URLs are unchanged ---
const BASE_URL = "/api/story"; // Story Engine
const CHARACTER_API_URL = "/api/character"; // Character Engine
const RULES_API_URL = "/api/rules"; // Rules Engine

// --- api helper function is unchanged ---
async function api<T>(url: string, options: RequestInit = {}): Promise<T> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorBody;
      try {
        errorBody = await response.json();
      } catch {
        errorBody = { detail: response.statusText };
      }
      console.error(
        `API Error ${response.status}: ${JSON.stringify(errorBody)}`,
      );
      throw new Error(
        errorBody.detail || `HTTP error! status: ${response.status}`,
      );
    }

    // Handle cases where response might be empty
    const text = await response.text();
    return text ? (JSON.parse(text) as T) : ({} as T);
  } catch (err) {
    console.error("API request failed:", err);
    throw err;
  }
}

// --- Character Engine Functions ---
// Renamed from fetchCharacters to match old import
export const fetchCharacters = (): Promise<CharacterContextResponse[]> => {
  return api<CharacterContextResponse[]>(`${CHARACTER_API_URL}/v1/characters/`);
};

// Renamed from fetchCharacterContext to match old import
export const fetchCharacterContext = (
  characterId: string,
): Promise<CharacterContextResponse> => {
  return api<CharacterContextResponse>(
    `${CHARACTER_API_URL}/v1/characters/${characterId}`,
  );
};

export const createCharacter = (
  payload: CharacterCreateRequest,
): Promise<CharacterContextResponse> => {
  return api<CharacterContextResponse>(`${CHARACTER_API_URL}/v1/characters/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
};

export const updateCharacterContext = (
  characterId: string,
  context: CharacterContextResponse,
): Promise<CharacterContextResponse> => {
  return api<CharacterContextResponse>(
    `${CHARACTER_API_URL}/v1/characters/${characterId}`,
    {
      method: "PUT",
      body: JSON.stringify(context),
    },
  );
};

// --- ADDED: Missing function for ExplorationScreen ---
export const updatePlayerLocation = (
  characterId: string,
  locationId: string,
  coordinates: [number, number],
): Promise<CharacterContextResponse> => {
  return api<CharacterContextResponse>(
    `${CHARACTER_API_URL}/v1/characters/${characterId}/location`,
    {
      method: "PUT",
      body: JSON.stringify({
        location_id: locationId,
        coordinates: coordinates,
      }),
    },
  );
};

// --- Story Engine Functions ---
// --- ADDED: Missing function for ExplorationScreen & CombatScreen ---
export const getLocationContext = (
  locationId: string,
): Promise<LocationContextResponse> => {
  return api<LocationContextResponse>(
    `${BASE_URL}/v1/context/location/${locationId}`,
  );
};

export const postInteraction = (
  request: InteractionRequest,
): Promise<InteractionResponse> => {
  // Assuming InteractionRequest is the correct payload type for /v1/actions/interact
  return api<InteractionResponse>(`${BASE_URL}/v1/actions/interact`, {
    method: "POST",
    body: JSON.stringify(request),
  });
};

export const startCombat = (
  payload: CombatStartRequestPayload,
): Promise<CombatEncounterResponse> => {
  return api<CombatEncounterResponse>(`${BASE_URL}/v1/combat/start`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
};

export const getCombatState = (
  encounterId: string,
): Promise<CombatEncounterResponse> => {
  // This endpoint doesn't seem to exist on story_engine/main.py, but we'll leave the function
  return api<CombatEncounterResponse>(
    `${BASE_URL}/v1/combat/state/${encounterId}`,
  );
};

// Renamed from postCombatAction to match old import
export const postCombatAction = (
  encounterId: number, // Changed to number to match CombatScreen
  action: PlayerActionRequestPayload, // Changed to match CombatScreen
): Promise<PlayerActionResponse> => {
  // Changed to match CombatScreen
  return api<PlayerActionResponse>(
    `${BASE_URL}/v1/combat/${encounterId}/player_action`,
    {
      method: "POST",
      body: JSON.stringify(action),
    },
  );
};

// --- ADDED: Missing function for CombatScreen ---
export const postNpcAction = (
  encounterId: number,
): Promise<PlayerActionResponse> => {
  return api<PlayerActionResponse>(
    `${BASE_URL}/v1/combat/${encounterId}/npc_action`,
    {
      method: "POST",
    },
  );
};

// --- Rules Engine Functions ---
export const getKingdomFeatures = (): Promise<KingdomFeaturesData> => {
  return api<KingdomFeaturesData>(
    `${RULES_API_URL}/v1/lookup/creation/kingdom_features`,
  );
};

export const getBackgroundTalents = (): Promise<TalentInfo[]> => {
  return api<TalentInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/background_talents`,
  );
};

export const getAbilityTalents = (): Promise<TalentInfo[]> => {
  return api<TalentInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/ability_talents`,
  );
};

export const getAbilitySchools = (): Promise<string[]> => {
  return api<string[]>(`${RULES_API_URL}/v1/lookup/all_ability_schools`);
};
