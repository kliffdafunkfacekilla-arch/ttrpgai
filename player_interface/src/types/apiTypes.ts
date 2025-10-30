// src/types/apiTypes.ts

// --- Context Types ---
// Represents the structure of the character sheet JSON blob
export interface CharacterSheet {
  stats: Record<string, number>;
  skills: Record<string, { rank: number; sre: number }>;
  abilities: Record<string, number>;
  resources: Record<string, { current: number; max: number }>;
  combat_stats: {
    max_hp: number;
    current_hp: number;
    status_effects: string[];
  };
  inventory: Array<{ item_id: string; quantity: number }>;
  equipment: Record<string, any>; // Consider defining more strictly (e.g., { slot: { item_id: string, name: string } })
  choices: Record<string, any>; // Stores creation choices
  unlocked_talents: Array<{ name: string; source: string; effect: string }>;
  location: string; // Current location ID or name
}

// Response from GET /v1/context/character/{char_id}
export interface CharacterContextResponse {
  id: number; // The database ID of the character
  name: string;
  kingdom: string;
  character_sheet: CharacterSheet;
}

// Represents region data nested in location context
export interface Region {
  id: number;
  name: string;
  current_weather: string;
  environmental_effects: string[];
  faction_influence: Record<string, any>;
}

// Represents item instances (in inventory or location)
export interface ItemInstance {
  id: number;
  template_id: string; // The base item ID (e.g., "potion_health_small")
  quantity: number;
  location_id?: number | null; // Set if on the ground
  npc_id?: number | null; // Set if in NPC inventory
}

// Represents NPC instances within a location
export interface NpcInstance {
  id: number; // The instance ID (e.g., 12)
  template_id: string; // The base NPC ID (e.g., "goblin_scout")
  name_override?: string | null; // Custom name like "Grak"
  current_hp: number;
  max_hp: number;
  status_effects: string[];
  location_id: number;
  item_instances: ItemInstance[]; // NPC's inventory
  behavior_tags: string[];
  stats?: Record<string, number>; // Stats might be included directly
  skills?: Record<string, number>; // Skills might be included directly
}

// Represents trap instances within a location
export interface TrapInstance {
    id: number;
    template_id: string; // e.g., "pit_trap_t1"
    location_id: number;
    coordinates?: any; // Define structure if needed, e.g., [number, number]
    status: string; // "armed", "disarmed", "triggered"
}

// Response from GET /v1/context/location/{location_id}
export interface LocationContextResponse {
  id: number;
  name: string;
  tags: string[];
  exits: Record<string, any>; // e.g., {"north": 2} where 2 is the next location ID
  generated_map_data?: Array<Array<number>> | null; // The tile ID grid
  map_seed?: string | null;
  region_id: number;
  region: Region; // Nested region details
  npc_instances: NpcInstance[]; // NPCs currently in the location
  item_instances: ItemInstance[]; // Items currently on the ground
  trap_instances: TrapInstance[]; // Traps currently in the location
  ai_annotations?: Record<string, any> | null; // State of interactable objects, descriptions
}

// --- Interaction Types ---
// Payload for POST /v1/actions/interact
export interface InteractionRequestPayload {
  actor_id: string; // e.g., "player_1"
  location_id: number;
  target_object_id: string; // Key from ai_annotations (e.g., "door_A")
  interaction_type?: string; // Optional, defaults to "use" on backend
}

// Response from POST /v1/actions/interact
export interface InteractionResponse {
  success: boolean;
  message: string; // User-facing feedback message
  updated_annotations?: Record<string, any> | null; // New state of annotations if changed
  items_added?: Array<{ item_id: string; quantity: number }> | null;
  items_removed?: Array<{ item_id: string; quantity: number }> | null;
  // Add other potential outcomes like quest updates if needed
}

// --- Combat Types ---
// Payload for POST /v1/combat/start (add if needed)
// export interface CombatStartRequestPayload {
//    location_id: number;
//    player_ids: string[];
//    npc_template_ids: string[];
// }

// Represents a participant within the CombatEncounterResponse
export interface CombatParticipantResponse {
    actor_id: string; // "player_1", "npc_12"
    actor_type: string; // "player", "npc"
    initiative_roll: number;
}

// Response from POST /v1/combat/start or GET /v1/combat/{id} (if you add that endpoint)
export interface CombatEncounterResponse {
    id: number; // Combat encounter ID
    location_id: number;
    status: string; // "active", "players_win", "npcs_win", etc.
    turn_order: string[]; // List of actor_ids in initiative order
    current_turn_index: number; // Index into turn_order
    participants: CombatParticipantResponse[]; // List of participants involved
}

// Payload for POST /v1/combat/{combat_id}/player_action
export interface PlayerActionRequestPayload {
    action: string; // "attack", "move", "use_ability", "wait"
    target_id?: string | null; // e.g., "npc_12" for attack/ability
    // Add other relevant fields based on action type:
    // ability_id?: string;
    // position?: [number, number]; // For movement
    // item_id?: string; // For using an item
}

// Response from POST /v1/combat/{combat_id}/player_action
export interface PlayerActionResponse {
    success: boolean; // Did the action processing succeed (even if the action missed)?
    message: string; // Primary outcome message (e.g., "Hit!", "Miss!")
    log: string[]; // Detailed step-by-step log of what happened
    damage_dealt?: number;
    target_hp_remaining?: number;
    outcome?: string; // e.g., "hit", "miss", "critical_hit" from rules_engine
    damage_details?: any[]; // Raw damage calculation details if needed
    // Add fields for status effects applied, etc. if returned by backend
}

// --- StoryFlag Types ---
// Represents a single story flag
export interface StoryFlag {
  id: number;
  flag_name: string;
  value: string;
}

// Payload for POST /v1/flags/ (setting a flag)
export interface StoryFlagPayload {
  flag_name: string;
  value: string;
}

// --- ActiveQuest Types ---
// Represents a single active quest
export interface ActiveQuest {
  id: number;
  title: string;
  description?: string | null;
  steps: string[];
  current_step: number;
  status: string; // "active", "completed", "failed"
  campaign_id: number;
}

// Payload for POST /v1/quests/ (creating a quest)
export interface ActiveQuestCreatePayload {
  title: string;
  description?: string | null;
  steps: string[];
  current_step?: number; // Optional, defaults to 1 on backend
  status?: string; // Optional, defaults to "active" on backend
  campaign_id: number;
}

// Payload for PUT /v1/quests/{quest_id} (updating a quest)
export interface ActiveQuestUpdatePayload {
  current_step?: number | null;
  status?: string | null;
  description?: string | null;
  steps?: string[] | null;
}

// --- Campaign Types ---
// Represents the main campaign object
export interface Campaign {
  id: number;
  name: string;
  main_plot_summary?: string | null;
  active_quests: ActiveQuest[]; // Nested quests included in response
}

// Payload for POST /v1/campaigns/ (creating a campaign)
export interface CampaignCreatePayload {
  name: string;
  main_plot_summary?: string | null;
}
