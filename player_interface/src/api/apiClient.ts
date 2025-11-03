// src/api/apiClient.ts
import {
  type CharacterContextResponse,
  // --- MODIFIED: Use InteractionRequestPayload ---
  type InteractionRequestPayload as InteractionRequest,
  type InteractionResponse,
  type CombatEncounterResponse,
  type PlayerActionRequest as CombatActionRequest, // This seems unused, but we'll leave it
  type CharacterCreateRequest,
  type KingdomFeaturesData,
  type TalentInfo,
  type LocationContextResponse,
  type PlayerActionResponse,
  type CombatStartRequestPayload,
  type PlayerActionRequestPayload,
  type BackgroundChoiceInfo, // --- ADDED ---
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
export const fetchCharacters = (): Promise<CharacterContextResponse[]> => {
  return api<CharacterContextResponse[]>(`${CHARACTER_API_URL}/v1/characters/`);
};

// --- Character Engine Functions (UNCHANGED) ---
export const fetchCharacters = (): Promise<CharacterContextResponse[]> => {
  return api<CharacterContextResponse[]>(`${CHARACTER_API_URL}/v1/characters/`);
};
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

export const updatePlayerLocation = (
  characterId: string,
  locationId: string,
  coordinates: [number, number],
): Promise<CharacterContextResponse> => {
  return api<CharacterContextResponse>(
    // --- MODIFIED: Use character ID from context ---
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
// --- Story Engine Functions (UNCHANGED) ---
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
  return api<CombatEncounterResponse>(
    `${BASE_URL}/v1/combat/state/${encounterId}`,
  );
};

export const postCombatAction = (
  encounterId: number,
  action: PlayerActionRequestPayload,
): Promise<PlayerActionResponse> => {
  return api<PlayerActionResponse>(
    `${BASE_URL}/v1/combat/${encounterId}/player_action`,
    {
      method: "POST",
      body: JSON.stringify(action),
    },
  );
};

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

// --- REMOVED: getBackgroundTalents ---

// --- REMOVED: getBackgroundTalents ---
export const getAbilityTalents = (): Promise<TalentInfo[]> => {
  return api<TalentInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/ability_talents`,
  );
};
export const getAbilitySchools = (): Promise<string[]> => {
  return api<string[]>(`${RULES_API_URL}/v1/lookup/all_ability_schools`);
};

// --- ADDED: 5 new functions ---
export const getOriginChoices = (): Promise<BackgroundChoiceInfo[]> => {
  return api<BackgroundChoiceInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/origin_choices`,
  );
};

export const getChildhoodChoices = (): Promise<BackgroundChoiceInfo[]> => {
  return api<BackgroundChoiceInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/childhood_choices`,
  );
};

export const getComingOfAgeChoices = (): Promise<BackgroundChoiceInfo[]> => {
  return api<BackgroundChoiceInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/coming_of_age_choices`,
  );
};

export const getTrainingChoices = (): Promise<BackgroundChoiceInfo[]> => {
  return api<BackgroundChoiceInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/training_choices`,
  );
};

export const getDevotionChoices = (): Promise<BackgroundChoiceInfo[]> => {
  return api<BackgroundChoiceInfo[]>(
    `${RULES_API_URL}/v1/lookup/creation/devotion_choices`,
  );
};

// --- ADDED: The missing function ---
export const getAllSkills = (): Promise<{ [key: string]: { stat: string } }> => {
  return api<{ [key: string]: { stat: string } }>(
    `${RULES_API_URL}/v1/lookup/all_skills`,
  );
};
// --- END ADD ---
