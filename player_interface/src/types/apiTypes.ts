// src/types/apiTypes.ts

// --- Core Character & World Types ---

export interface InventoryItem {
  name: string;
  description?: string;
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
  inventory: { [key: string]: InventoryItem };
  equipment: { [key: string]: InventoryItem };
  status_effects: string[];
  injuries: Injury[];
  location: {
    current_location_id: string;
    coordinates: [number, number];
  };
  position_x: number;
  position_y: number;
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

/**
 * NEW TYPE: Defines the shape of an object within ai_annotations.
 * We use an intersection to combine known properties with unknown ones.
 */
// A base type for the known properties
export interface AiAnnotationBase {
  coordinates: [number, number];
  type?: string;
  status?: string;
  key_id?: string;
  item_id?: string;
  quantity?: number;
}
// A type for any other dynamic properties
type AiAnnotationExtras = Record<string, unknown>;
// The final type is an intersection of both
export type AiAnnotationValue = AiAnnotationBase & AiAnnotationExtras;

export interface LocationContextResponse {
  id: string;
  name: string;
  generated_map_data: number[][];
  npc_instances: NpcInstance[];
  item_instances: ItemInstance[];
  ai_annotations?: {
    [key: string]: AiAnnotationValue; // <-- This now uses the intersection type
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
  quantity: number;
  coordinates: [number, number];
  location_id?: number;
  npc_id?: number;
}

// --- Interaction Types (Corrected) ---

export interface InteractionRequestPayload {
  actor_id: string;
  location_id: string;
  target_object_id: string;
  interaction_type: string;
}

/**
 * NEW TYPE: Defines the shape of items being added/removed
 * in an InteractionResponse.
 */
export interface ItemChange {
  item_id: string;
  quantity: number;
}

export interface InteractionResponse {
  success: boolean;
  message: string;
  updated_annotations?: { [key: string]: AiAnnotationValue }; // <-- FIX 2: Use specific type
  items_added?: ItemChange[]; // <-- FIX 3: Use specific type
  items_removed?: ItemChange[]; // <-- FIX 4: Use specific type
}

// --- Types for Combat (Corrected) ---

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
  encounter_id?: string;
  player_character?: CharacterContextResponse;
  npcs?: NpcInstance[];
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

// --- Types for Character Creation (Corrected) ---

export interface FeatureChoiceRequest {
  feature_id: string;
  choice_name: string;
}

export interface CharacterCreateRequest {
  name: string;
  kingdom: string;
  feature_choices: FeatureChoiceRequest[];
  origin_choice: string;
  childhood_choice: string;
  coming_of_age_choice: string;
  training_choice: string;
  devotion_choice: string;
  ability_school: string;
  ability_talent: string;
}

export interface TalentInfo {
  name: string;
  description: string;
  source?: string;
  effect?: string;
}

export interface BackgroundChoiceInfo {
  name: string;
  description: string;
  skills: string[];
}

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