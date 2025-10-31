// src/api/apiClient.ts
import axios, { AxiosError } from 'axios';
import {
    type CharacterContextResponse,
    type LocationContextResponse,
    type InteractionRequestPayload,
    type InteractionResponse,
    type CombatEncounterResponse,
    type CombatStartRequestPayload,
    type PlayerActionRequestPayload,
    type PlayerActionResponse,
} from '../types/apiTypes'; // Adjust path as needed

// --- 1. ADD CHARACTER_ENGINE_BASE_URL ---
const STORY_ENGINE_BASE_URL = 'http://127.0.0.1:8003'; // Your story_engine URL
const CHARACTER_ENGINE_BASE_URL = 'http://127.0.0.1:8001'; // Your character_engine URL

// --- 2. CREATE A SEPARATE CLIENT FOR CHARACTER_ENGINE ---
// (Alternatively, we could make callApi accept a baseURL, but this is simpler for now)
const storyApiClient = axios.create({
    baseURL: STORY_ENGINE_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
});

const charApiClient = axios.create({
    baseURL: CHARACTER_ENGINE_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
});

import type { AxiosInstance } from 'axios';

// --- 3. MODIFY callApi TO ACCEPT AN API CLIENT ---
export const callApi = async <T>(
    apiClient: AxiosInstance, // Pass in the client to use
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    data?: any,
    params?: any
): Promise<T> => {
    // Use the client's baseURL
    console.log(`API Call: ${method.toUpperCase()} ${apiClient.defaults.baseURL}${url}`, { data, params });
    try {
        const response = await apiClient.request<T>({ method, url, data, params });
        console.log(`API Response: ${response.status}`, response.data);
        return response.data;
    } catch (error) {
        // ... (Error handling code is unchanged) ...
        const axiosError = error as AxiosError;
        let status = 500;
        let message = 'An unexpected error occurred';
        let details: any = null;

        if (axiosError.response) {
            status = axiosError.response.status;
            message = `API Error ${status}`;
            details = axiosError.response.data;
            console.error(`API Error ${status} for ${method.toUpperCase()} ${url}:`, details || axiosError.message);
            if (typeof details === 'object' && details !== null && 'detail' in details) {
                message = details.detail as string;
            } else if (typeof details === 'string') {
                message = details;
            }
        } else if (axiosError.request) {
            status = 503;
            message = 'Network Error or Service Unavailable. Is the backend running?';
            console.error(`Network Error for ${method.toUpperCase()} ${url}:`, axiosError.message);
        } else {
            message = axiosError.message || 'Error setting up API request';
            console.error(`Request Setup Error for ${method.toUpperCase()} ${url}:`, axiosError.message);
        }
        throw { status, message, details }; // Throw consistent error object
    }
};

// --- 4. UPDATE API FUNCTIONS TO USE THE CORRECT CLIENT ---
export const getCharacterContext = (characterId: string): Promise<CharacterContextResponse> => {
    const endpoint = `/v1/characters/${characterId}`;
    // Use charApiClient
    return callApi<CharacterContextResponse>(charApiClient, 'get', endpoint);
};

export const getLocationContext = (locationId: number): Promise<LocationContextResponse> => {
    const endpoint = `/v1/context/location/${locationId}`;
    // Use storyApiClient
    return callApi<LocationContextResponse>(storyApiClient, 'get', endpoint);
};

export const postInteraction = (payload: InteractionRequestPayload): Promise<InteractionResponse> => {
    const endpoint = '/v1/actions/interact';
    // Use storyApiClient
    return callApi<InteractionResponse>(storyApiClient, 'post', endpoint, payload);
};

export const postPlayerAction = (combatId: number, payload: PlayerActionRequestPayload): Promise<PlayerActionResponse> => {
    const endpoint = `/v1/combat/${combatId}/player_action`;
    // Use storyApiClient
    return callApi<PlayerActionResponse>(storyApiClient, 'post', endpoint, payload);
};

// --- ADD THIS NEW FUNCTION ---
export const startCombat = (payload: CombatStartRequestPayload): Promise<CombatEncounterResponse> => {
    const endpoint = '/v1/combat/start';
    // Use storyApiClient
    return callApi<CombatEncounterResponse>(storyApiClient, 'post', endpoint, payload);
};

// --- 5. ADD NEW FUNCTION FOR UPDATING LOCATION ---
export const updatePlayerLocation = (
    characterId: number,
    locationId: number,
    coordinates: [number, number]
): Promise<CharacterContextResponse> => {
    const endpoint = `/v1/characters/${characterId}/location`;
    const payload = {
        location_id: locationId,
        coordinates: coordinates,
    };
    // Use charApiClient
    return callApi<CharacterContextResponse>(charApiClient, 'put', endpoint, payload);
};
