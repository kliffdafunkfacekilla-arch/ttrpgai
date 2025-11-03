// src/types/apiTypes.ts

// --- Core Character & World Types ---
export interface InventoryItem {
  name: string; // This seems to be used by CharacterSheetScreen
  description?: string; // Adding as optional
  quantity: number;
}

export interface Injury {
  location: string;
  severity: string;
  description: string;
}

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
  inventory: { [key: string]: InventoryItem }; // Changed to match CharacterSheetScreen
  equipment: { [key: string]: InventoryItem };
  status_effects: string[];
  injuries: Injury[];
  // --- MODIFIED: This is now an object ---
  location: {
    current_location_id: string;
    coordinates: [number, number];
  };
  // --- END MODIFIED ---
  position_x: number; // This is now redundant, but we'll leave it for now
  position_y: number; // This is now redundant, but we'll leave it for now
  // --- ADDED: For CombatScreen ---
  character_sheet: {
    abilities: string[];
    inventory: { [key: string]: InventoryItem };
    combat_stats: {
      current_hp: number;
      max_hp: number;
    };
    location: {
      current_location_id: string;
      coordinates: [number, number];
    };
  };
}

// --- Types for Exploration & World ---
export interface LocationContextResponse {
  id: string;
  name: string;
  generated_map_data: number[][];
  npc_instances: NpcInstance[];
  item_instances: ItemInstance[];
  ai_annotations?: {
    [key: string]: {
      coordinates: [number, number];
      [key: string]: any; // Other properties
    };
  };
}

export interface NpcInstance {
  id: string;
  template_id: string;
  name_override?: string;
  coordinates: [number, number];
  behavior_tags: string[];
  current_hp: number;
  max_hp: number;
  stats?: { [key: string]: number };
  skills?: { [key: string]: number };
}

export interface ItemInstance {
  id: string;
  template_id: string;
  coordinates: [number, number];
}

export interface InteractionRequestPayload {
  actor_id: string;
  location_id: string;
  target_object_id: string;
  interaction_type: string;
}

export interface InteractionResponse {
  success: boolean;
  message: string;
  updated_annotations?: any;
  items_added?: any[];
  items_removed?: any[]; // Added for completeness
  narrative?: string; // From old type
  options?: string[]; // From old type
}

// --- Types for Combat ---
export interface CombatStartRequestPayload {
  location_id: string;
  player_ids: string[];
  npc_template_ids: string[];
}

export interface CombatEncounterResponse {
  id: number;
  location_id: string;
  turn_order: string[];
  current_turn_index: number;
  // --- These were from the old type, may not match story_engine ---
  encounter_id?: string;
  player_character?: CharacterContextResponse;
  npcs?: NpcInstance[]; // Using NpcInstance
  current_turn?: string;
  log?: string[];
  grid_size?: { width: number; height: number };
}

export interface PlayerActionRequestPayload {
  action: "attack" | "use_ability" | "use_item" | "wait";
  target_id?: string;
  ability_id?: string;
  item_id?: string;
}

export interface PlayerActionResponse {
  success: boolean;
  message: string;
  log: string[];
  new_turn_index: number;
  combat_over: boolean;
}

// --- Types for Character Creation ---
export interface FeatureChoiceRequest {
  feature_id: string; // e.g., "F1", "F9"
  choice_name: string; // e.g., "Predator's Gaze", "Capstone: +2 Might"
}

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

export interface TalentInfo {
  name: string;
  description: string; // Changed from 'effect' to match UI
  source?: string; // Added from rules_engine model
  effect?: string; // Added from rules_engine model
}

// --- ADDED THIS TYPE ---
export interface BackgroundChoiceInfo {
  name: string;
  description: string;
  skills: string[];
}
// --- END ADD ---

export interface FeatureMods {
  "+2"?: string[];
  "+1"?: string[];
  "-1"?: string[];
}

export interface KingdomFeatureChoice {
  name: string;
  mods: FeatureMods;
}

export interface KingdomFeatureSet {
  [kingdom: string]: KingdomFeatureChoice[];
}

export interface KingdomFeaturesData {
  [feature_id: string]: KingdomFeatureSet;
}
