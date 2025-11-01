// src/assets/assetLoader.ts
import tileDefinitionsData from "../data/tile_definitions.json";
// --- 1. IMPORT THE NEW JSON ---
import entityDefinitionsData from "../data/entity_definitions.json";

// --- Interfaces and Types ---
export interface TileDefinition {
  name: string;
  passable: boolean;
  tags: string[];
  states?: {
    [stateName: string]: {
      passable: boolean;
    };
  };
}

// --- 2. ADD ENTITY DEFINITION INTERFACE ---
export interface EntityDefinition {
  name: string;
  sheet: string; // Spritesheet filename
  col: number; // 1-based column
  row: number; // 1-based row
}

export type TileDefinitionsMap = Record<string, TileDefinition>;
// --- 3. ADD ENTITY DEFINITION MAP TYPE ---
export type EntityDefinitionsMap = Record<string, EntityDefinition>;

// Type for storing the mapping needed for calculation
interface SpriteInfo {
  sheetFilename: string;
  gridCol: number; // 0-indexed column
  gridRow: number; // 0-indexed row
}

// Type for the final lookup map
// This map holds the calculated/looked-up info needed to render each tile/state
// --- 4. RENAME to a more generic name ---
type SpriteLookupMap = Record<string, SpriteInfo>; // Key: "ID" or "ID_state" or "template_id"

// --- Constants ---
export const TILE_SIZE = 128; // Your tile size in pixels
// Note: This assumes entity sprites are also 128x128.
// We can make this more flexible later if needed.

// --- Load Raw Definitions ---
const tileDefinitions: TileDefinitionsMap =
  tileDefinitionsData as TileDefinitionsMap;
// --- 5. LOAD NEW DEFINITIONS ---
const entityDefinitions: EntityDefinitionsMap =
  entityDefinitionsData as EntityDefinitionsMap;

// --- Processed Sprite Mapping ---
// --- 6. RENAME to a more generic name ---
const spriteLookupMap: SpriteLookupMap = {};

// --- Spritesheet URL Cache ---
// Stores the URLs for the actual spritesheet files
const loadedSpritesheetUrls: Record<string, string> = {};

/**
 * Caches a spritesheet URL.
 */
const cacheSheetUrl = (filename: string, path: "tiles" | "entities") => {
  if (!loadedSpritesheetUrls[filename]) {
    loadedSpritesheetUrls[filename] = `/assets/graphics/${path}/${filename}`;
  }
};

/**
 * Processes the raw definitions into a unified lookup map.
 */
const buildSpriteLookupMap = (): void => {
  console.log("Building sprite lookup map...");

  // --- 7. PROCESS TILE DEFINITIONS ---
  // (This is your existing mapping logic, just adapted slightly)
  const manualTileMap: Record<
    string,
    { sheet: string; col: number; row: number }
  > = {
    "0": { sheet: "outdoor_tiles_1.png", col: 3, row: 3 }, // Grass
    "1": { sheet: "outdoor_tiles_1.png", col: 5, row: 4 }, // Tree
    "2": { sheet: "outdoor_tiles_1.png", col: 2, row: 5 }, // Water
    "3": { sheet: "indoor_town_default_1.png", col: 3, row: 4 }, // Stone Floor
    "4": { sheet: "indoor_town_default_1.png", col: 2, row: 1 }, // Stone Wall
    "5": { sheet: "indoor_town_default_1.png", col: 3, row: 1 }, // Door Closed
    "5_open": { sheet: "indoor_town_default_1.png", col: 1, row: 1 }, // Door Open (State)
  };

  for (const tileId in tileDefinitions) {
    const baseMapInfo = manualTileMap[tileId];
    if (baseMapInfo) {
      spriteLookupMap[tileId] = {
        sheetFilename: baseMapInfo.sheet,
        gridCol: baseMapInfo.col - 1, // Convert to 0-based index
        gridRow: baseMapInfo.row - 1, // Convert to 0-based index
      };
      cacheSheetUrl(baseMapInfo.sheet, "tiles");
    } else {
      console.warn(`No manual mapping provided for Tile ID: ${tileId}`);
    }

    const def = tileDefinitions[tileId];
    if (def.states) {
      for (const stateName in def.states) {
        const stateKey = `${tileId}_${stateName}`;
        const stateMapInfo = manualTileMap[stateKey];
        if (stateMapInfo) {
          spriteLookupMap[stateKey] = {
            sheetFilename: stateMapInfo.sheet,
            gridCol: stateMapInfo.col - 1,
            gridRow: stateMapInfo.row - 1,
          };
          cacheSheetUrl(stateMapInfo.sheet, "tiles");
        } else {
          console.warn(
            `No specific manual mapping for state '${stateName}' of Tile ID: ${tileId}.`,
          );
        }
      }
    }
  }

  // --- 8. PROCESS ENTITY DEFINITIONS ---
  for (const templateId in entityDefinitions) {
    const entityInfo = entityDefinitions[templateId];
    if (entityInfo) {
      spriteLookupMap[templateId] = {
        sheetFilename: entityInfo.sheet,
        gridCol: entityInfo.col - 1, // Convert to 0-based
        gridRow: entityInfo.row - 1, // Convert to 0-based
      };
      // Cache the URL, assuming entity graphics are in 'entities' folder
      cacheSheetUrl(entityInfo.sheet, "entities");
    }
  }

  console.log("Sprite lookup map built:", spriteLookupMap);
  console.log("Spritesheet URLs cached:", loadedSpritesheetUrls);
};

// --- Exported Functions ---
/**
 * Call this once at application startup.
 */
export const initializeAssets = (): Promise<void> => {
  buildSpriteLookupMap();
  return Promise.resolve();
};

/**
 * Gets the spritesheet URL and clipping info for a tile ID or template ID.
 * Calculates pixel coordinates from stored grid coordinates.
 * @param id The numeric ID of the tile (e.g., "0") OR the template_id of an entity (e.g., "goblin_scout").
 * @param state Optional state name (e.g., "open" for a door).
 * @returns An object with sheet URL and clipping coords { sheetUrl, sx, sy, sWidth, sHeight } or undefined.
 */
// --- 9. RENAME and UPDATE ---
export const getSpriteRenderInfo = (
  id: string | number,
  state?: string,
):
  | {
      sheetUrl: string;
      sx: number;
      sy: number;
      sWidth: number;
      sHeight: number;
    }
  | undefined => {
  const baseIdStr = String(id);
  let key = baseIdStr;
  if (state) {
    key = `${baseIdStr}_${state}`;
  }

  // Fallback logic: if state key ("5_open") isn't found, try base key ("5")
  // If base key ("goblin_scout") isn't found, try "fallback"
  const spriteInfo =
    spriteLookupMap[key] ||
    spriteLookupMap[baseIdStr] ||
    spriteLookupMap["fallback"];

  if (!spriteInfo) {
    console.warn(
      `Render info not found for id: ${id}, state: ${state}. No fallback available.`,
    );
    // As a last resort, render a purple box if even fallback is missing
    const fallbackUrl = "/assets/graphics/tiles/fallback.png"; // A known fallback asset
    if (loadedSpritesheetUrls["fallback.png"]) {
      return {
        sheetUrl: fallbackUrl,
        sx: 0,
        sy: 0,
        sWidth: TILE_SIZE,
        sHeight: TILE_SIZE,
      };
    }
    return undefined; // Should not happen if fallback.png exists
  }

  const sheetUrl = loadedSpritesheetUrls[spriteInfo.sheetFilename];
  if (!sheetUrl) {
    console.error(
      `Spritesheet URL not cached for filename: ${spriteInfo.sheetFilename}`,
    );
    const fallbackUrl = "/assets/graphics/tiles/fallback.png";
    return {
      sheetUrl: fallbackUrl,
      sx: 0,
      sy: 0,
      sWidth: TILE_SIZE,
      sHeight: TILE_SIZE,
    };
  }

  // Calculate pixel coordinates
  const sx = spriteInfo.gridCol * TILE_SIZE;
  const sy = spriteInfo.gridRow * TILE_SIZE;

  return {
    sheetUrl: sheetUrl,
    sx: sx,
    sy: sy,
    sWidth: TILE_SIZE,
    sHeight: TILE_SIZE,
  };
};

/** Gets the full tile definition data (unchanged) */
export const getTileDefinition = (
  tileId: string | number,
): TileDefinition | undefined => {
  return tileDefinitions[String(tileId)];
};

// --- 10. ADD new getter for entity definitions ---
/** Gets the full entity definition data */
export const getEntityDefinition = (
  templateId: string,
): EntityDefinition | undefined => {
  return entityDefinitions[templateId];
};
