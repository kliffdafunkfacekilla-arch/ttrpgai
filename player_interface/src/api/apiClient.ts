// src/api/apiClient.ts
import axios, { AxiosError } from 'axios';
import {
    CharacterContextResponse,
    LocationContextResponse,
    InteractionRequestPayload,
    InteractionResponse,
    CombatEncounterResponse,
    PlayerActionRequestPayload,
    PlayerActionResponse,
} from '../types/apiTypes'; // Adjust path as needed

const STORY_ENGINE_BASE_URL = 'http://127.0.0.1:8003'; // Your story_engine URL

const apiClient = axios.create({
    baseURL: STORY_ENGINE_BASE_URL,
    timeout: 10000,
    headers: { 'Content-Type': 'application/json' },
});

// --- Generic API Caller ---
export const callApi = async <T>(
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    data?: any,
    params?: any
): Promise<T> => {
    console.log(`API Call: ${method.toUpperCase()} ${STORY_ENGINE_BASE_URL}${url}`, { data, params });
    try {
        const response = await apiClient.request<T>({ method, url, data, params });
        console.log(`API Response: ${response.status}`, response.data);
        return response.data;
    } catch (error) {
        // ... (Error handling code from previous response - keep it here) ...
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
            message = 'Network Error or Service Unavailable. Is the story_engine running?';
            console.error(`Network Error for ${method.toUpperCase()} ${url}:`, axiosError.message);
        } else {
            message = axiosError.message || 'Error setting up API request';
            console.error(`Request Setup Error for ${method.toUpperCase()} ${url}:`, axiosError.message);
        }
        throw { status, message, details }; // Throw consistent error object
    }
};

// --- Specific API Functions ---
export const getCharacterContext = (characterId: string): Promise<CharacterContextResponse> => {
    const endpoint = `/v1/context/character/${characterId}`;
    return callApi<CharacterContextResponse>('get', endpoint);
};

export const getLocationContext = (locationId: number): Promise<LocationContextResponse> => {
    const endpoint = `/v1/context/location/${locationId}`;
    return callApi<LocationContextResponse>('get', endpoint);
};

export const postInteraction = (payload: InteractionRequestPayload): Promise<InteractionResponse> => {
    const endpoint = '/v1/actions/interact';
    return callApi<InteractionResponse>('post', endpoint, payload);
};

// Placeholder for startCombat if needed later
// export const startCombat = (payload: CombatStartRequestPayload): Promise<CombatEncounterResponse> => { ... }

export const postPlayerAction = (combatId: number, payload: PlayerActionRequestPayload): Promise<PlayerActionResponse> => {
    const endpoint = `/v1/combat/${combatId}/player_action`;
    return callApi<PlayerActionResponse>('post', endpoint, payload);
};

// Add other functions (listCharacters, etc.) as needed