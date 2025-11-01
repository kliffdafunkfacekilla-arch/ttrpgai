// src/api/apiClient.ts
import {
    type CharacterContextResponse,
    type InteractionRequest,
    type InteractionResponse,
    type CombatEncounterResponse,
    type CombatActionRequest,
    // --- NEWLY IMPORTED TYPES ---
    type CharacterCreateRequest,
    type KingdomFeaturesData,
    type TalentInfo
} from '../types/apiTypes';

// --- Base URLs are unchanged ---
const BASE_URL = '/api/story'; // Story Engine
const CHARACTER_API_URL = '/api/character'; // Character Engine
const RULES_API_URL = '/api/rules'; // Rules Engine

// --- api helper function is unchanged ---
async function api<T>(url: string, options: RequestInit = {}): Promise<T> {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        });
        if (!response.ok) {
            let errorBody;
            try {
                errorBody = await response.json();
            } catch (e) {
                errorBody = { detail: response.statusText };
            }
            console.error(`API Error ${response.status}: ${JSON.stringify(errorBody)}`);
            throw new Error(errorBody.detail || `HTTP error! status: ${response.status}`);
        }
        // Handle cases where response might be empty
        const text = await response.text();
        return text ? (JSON.parse(text) as T) : ({} as T);
    } catch (err: any) {
        console.error('API request failed:', err);
        throw err;
    }
}

// --- Character Engine Functions ---
export const fetchCharacters = (): Promise<CharacterContextResponse[]> => {
    return api<CharacterContextResponse[]>(`${CHARACTER_API_URL}/characters/`);
};

export const fetchCharacterContext = (characterId: string): Promise<CharacterContextResponse> => {
    return api<CharacterContextResponse>(`${CHARACTER_API_URL}/characters/${characterId}`);
};

// --- MODIFIED createCharacter ---
/**
 * Creates a new character using the full creation payload.
 * @param payload - The complete set of character creation choices.
 * @returns The newly created character's full context.
 */
export const createCharacter = (payload: CharacterCreateRequest): Promise<CharacterContextResponse> => {
    return api<CharacterContextResponse>(`${CHARACTER_API_URL}/characters/`, {
        method: 'POST',
        body: JSON.stringify(payload),
    });
};

// --- updateCharacterContext is unchanged ---
export const updateCharacterContext = (characterId: string, context: CharacterContextResponse): Promise<CharacterContextResponse> => {
    return api<CharacterContextResponse>(`${CHARACTER_API_URL}/characters/${characterId}`, {
        method: 'PUT',
        body: JSON.stringify(context),
    });
};

// --- Story Engine Functions are unchanged ---
export const postInteraction = (request: InteractionRequest): Promise<InteractionResponse> => {
    return api<InteractionResponse>(`${BASE_URL}/interaction/`, {
        method: 'POST',
        body: JSON.stringify(request),
    });
};

export const startCombat = (characterId: string, mapId: string): Promise<CombatEncounterResponse> => {
    return api<CombatEncounterResponse>(`${BASE_URL}/combat/start`, {
        method: 'POST',
        body: JSON.stringify({ character_id: characterId, map_id: mapId }),
    });
};

export const getCombatState = (encounterId: string): Promise<CombatEncounterResponse> => {
    return api<CombatEncounterResponse>(`${BASE_URL}/combat/state/${encounterId}`);
};

export const postCombatAction = (encounterId: string, action: CombatActionRequest): Promise<CombatEncounterResponse> => {
    return api<CombatEncounterResponse>(`${BASE_URL}/combat/action/${encounterId}`, {
        method: 'POST',
        body: JSON.stringify(action),
    });
};

// --- NEW Rules Engine Functions for Character Creation ---
/**
 * Fetches the complete hierarchical structure of kingdom features,
 * including all choices and their stat mods.
 */
export const getKingdomFeatures = (): Promise<KingdomFeaturesData> => {
    return api<KingdomFeaturesData>(`${RULES_API_URL}/v1/lookup/creation/kingdom_features`);
};

/**
 * Fetches the list of all Background-type talents.
 */
export const getBackgroundTalents = (): Promise<TalentInfo[]> => {
    return api<TalentInfo[]>(`${RULES_API_URL}/v1/lookup/creation/background_talents`);
};

/**
 * Fetches the list of all Ability-type talents.
 */
export const getAbilityTalents = (): Promise<TalentInfo[]> => {
    return api<TalentInfo[]>(`${RULES_API_URL}/v1/lookup/creation/ability_talents`);
};

/**
 * Fetches the list of all Ability School names.
 */
export const getAbilitySchools = (): Promise<string[]> => {
    return api<string[]>(`${RULES_API_URL}/v1/lookup/all_ability_schools`);
};
