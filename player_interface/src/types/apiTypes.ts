// src/types/apiTypes.ts
// --- NEW SPECIFIC TYPES ---
export interface InventoryItem {
  name: string;
  description: string;
  quantity: number;
}
export interface Injury {
  location: string;
  severity: string;
  description: string;
}
// --- UNCHANGED TYPES ---
export interface CharacterContextResponse {
  id: string;
  name: string;
  kingdom: string | null;
  level: number;
  stats: { [key: string]: number };
  skills: { [key: string]: number };
  max_hp: number;
  current_hp: number;
  resource_pools: { [key: string]: { current: number; max: number } };
  talents: string[];
  abilities: string[];
  inventory: { [key: string]: InventoryItem };
  equipment: { [key: string]: InventoryItem };
  status_effects: string[];
  injuries: Injury[];
  position_x: number;
  position_y: number;
}
export interface InteractionRequest {
  character_id: string;
  action: string;
  target_id?: string;
  context: string;
}
export interface InteractionResponse {
  narrative: string;
  options: string[];
  // ... other potential fields
}
export interface CombatNpc {
  id: string;
  name: string;
  hp: number;
  max_hp: number;
  position: { x: number; y: number };
  // ... other combat-relevant fields
}
export interface CombatEncounterResponse {
  encounter_id: string;
  player_character: CharacterContextResponse;
  npcs: CombatNpc[];
  current_turn: string; // 'player' or npc_id
  log: string[];
  grid_size: { width: number; height: number };
}
export interface CombatActionRequest {
  character_id: string;
  action_type: string; // 'move', 'attack', 'ability', 'item'
  target_id?: string;
  position?: { x: number; y: number };
  ability_name?: string;
  item_name?: string;
}
// --- NEW CHARACTER CREATION TYPES ---
/**
 * Represents a single choice for a feature, sent to the character_engine.
 * Matches schemas.FeatureChoice in character_engine.
 */
export interface FeatureChoiceRequest {
  feature_id: string; // e.g., "F1", "F9"
  choice_name: string; // e.g., "Predator's Gaze", "Capstone: +2 Might"
}
/**
 * The full payload for creating a new character.
 * Matches schemas.CharacterCreate in character_engine.
 */
export interface CharacterCreateRequest {
  name: string;
  kingdom: string;
  feature_choices: FeatureChoiceRequest[];

  // --- MODIFIED ---
  origin_choice: string;
  childhood_choice: string;
  coming_of_age_choice: string;
  training_choice: string;
  devotion_choice: string;
  // --- END MODIFIED ---

  ability_school: string;
  ability_talent: string;
}
/**
 * A simple talent structure returned by the rules_engine.
 */
export interface TalentInfo {
  name: string;
  description: string;
  // Note: The rules_engine endpoints from Module 1 only return these fields.
}
// --- ADDED THIS TYPE ---
/**
 * A simple background choice structure returned by the rules_engine.
 */
export interface BackgroundChoiceInfo {
  name: string;
  description: string;
  skills: string[];
}
// --- END ADD ---
/**
 * The modifiers block for a single feature choice.
 */
export interface FeatureMods {
  "+2"?: string[];
  "+1"?: string[];
  "-1"?: string[];
}
/**
 * A single selectable choice within a kingdom for a feature.
 */
export interface KingdomFeatureChoice {
  name: string;
  mods: FeatureMods;
}
/**
 * The set of choices for a given feature, keyed by Kingdom.
 * e.g., { "Mammal": [KingdomFeatureChoice...], "Reptile": [...] }
 * or { "All": [KingdomFeatureChoice...] } for F9.
 */
export interface KingdomFeatureSet {
  [kingdom: string]: KingdomFeatureChoice[];
}
/**
 * The complete kingdom features data structure fetched from the rules_engine.
 * e.g., { "F1": KingdomFeatureSet, "F2": KingdomFeatureSet, ... }
 */
export interface KingdomFeaturesData {
  [feature_id: string]: KingdomFeatureSet;
}
