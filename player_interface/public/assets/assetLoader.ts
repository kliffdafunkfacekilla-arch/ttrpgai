// src/assets/assetLoader.ts
import tileDefinitionsData from "../data/tile_definitions.json";

// --- Interfaces and Types ---
export interface TileDefinition {
  name: string;
  // graphic_ref is now ignored in favor of calculated coords
  passable: boolean;
  tags: string[];
  states?: {
    [stateName: string]: {
      // graphic_ref ignored here too
      passable: boolean;
      // We'll store grid coords for states directly
    };
  };
}

export type TileDefinitionsMap = Record<string, TileDefinition>;

// Type for storing the mapping needed for calculation
interface TileSpriteInfo {
  sheetFilename: string;
  gridCol: number; // 0-indexed column
  gridRow: number; // 0-indexed row
}

// Type for the final lookup map
type TileSpriteMap = Record<string, TileSpriteInfo>; // Key: "ID" or "ID_state"

// --- Constants ---
export const TILE_SIZE = 128; // Your tile size in pixels
export const SPRITESHEET_COLS = 5; // Number of tiles across your sheets

// --- Load Raw Definitions ---
const tileDefinitions: TileDefinitionsMap =
  tileDefinitionsData as TileDefinitionsMap;

// --- Processed Sprite Mapping ---
// This map holds the calculated/looked-up info needed to render each tile/state
const tileSpriteMap: TileSpriteMap = {};

// --- Spritesheet URL Cache ---
// Stores the URLs for the actual spritesheet files
const loadedSpritesheetUrls: Record<string, string> = {};

/**
 * Maps the user-provided grid coordinates (1-based Col x Row) to 0-based indices
 * and stores them along with the spritesheet filename.
 */
const buildTileSpriteMap = (): void => {
  console.log(
    "Building tile sprite map from definitions and manual mapping...",
  );

  // Your provided mapping (Col, Row are 1-based from input)
  const manualMap: Record<string, { sheet: string; col: number; row: number }> =
    {
      "0": { sheet: "outdoor_tiles_1.png", col: 3, row: 3 }, // Grass
      "1": { sheet: "outdoor_tiles_1.png", col: 5, row: 4 }, // Tree
      "2": { sheet: "outdoor_tiles_1.png", col: 2, row: 5 }, // Water
      "3": { sheet: "indoor_town_default_1.png", col: 3, row: 4 }, // Stone Floor
      "4": { sheet: "indoor_town_default_1.png", col: 2, row: 1 }, // Stone Wall
      "5": { sheet: "indoor_town_default_1.png", col: 3, row: 1 }, // Door Closed
      "5_open": { sheet: "indoor_town_default_1.png", col: 1, row: 1 }, // Door Open (State)
      // Add fallback mapping if desired, otherwise handled in getTileRenderInfo
      // "fallback": { sheet: "fallback.png", col: 1, row: 1} // Assumes fallback is a 1x1 sheet
    };

  for (const tileId in tileDefinitions) {
    const baseMapInfo = manualMap[tileId];
    if (baseMapInfo) {
      tileSpriteMap[tileId] = {
        sheetFilename: baseMapInfo.sheet,
        gridCol: baseMapInfo.col - 1, // Convert to 0-based index
        gridRow: baseMapInfo.row - 1, // Convert to 0-based index
      };
      // Cache the spritesheet URL if not already done
      if (!loadedSpritesheetUrls[baseMapInfo.sheet]) {
        loadedSpritesheetUrls[baseMapInfo.sheet] =
          `/assets/graphics/tiles/${baseMapInfo.sheet}`;
      }
    } else {
      console.warn(`No manual mapping provided for Tile ID: ${tileId}`);
    }

    // Handle states defined in tile_definitions.json
    const def = tileDefinitions[tileId];
    if (def.states) {
      for (const stateName in def.states) {
        const stateKey = `${tileId}_${stateName}`;
        const stateMapInfo = manualMap[stateKey]; // Look for specific state mapping first
        if (stateMapInfo) {
          tileSpriteMap[stateKey] = {
            sheetFilename: stateMapInfo.sheet,
            gridCol: stateMapInfo.col - 1,
            gridRow: stateMapInfo.row - 1,
          };
          if (!loadedSpritesheetUrls[stateMapInfo.sheet]) {
            loadedSpritesheetUrls[stateMapInfo.sheet] =
              `/assets/graphics/tiles/${stateMapInfo.sheet}`;
          }
        } else if (baseMapInfo) {
          // Fallback: If state has no specific map, assume it uses base tile's location (unlikely for open/closed)
          // Or better: log a warning if state exists in def but not in manualMap
          console.warn(
            `No specific manual mapping provided for state '${stateName}' of Tile ID: ${tileId}. State visuals might be wrong.`,
          );
          // You could potentially reuse the baseMapInfo here if states share coords, but unlikely for doors
          // tileSpriteMap[stateKey] = tileSpriteMap[tileId];
        }
      }
    }
  }
  console.log("Tile sprite map built:", tileSpriteMap);
  console.log("Spritesheet URLs cached:", loadedSpritesheetUrls);
};

// --- Exported Functions ---
/**
 * Call this once at application startup.
 * Returns a void Promise (resolves immediately as we only cache URLs now).
 */
export const initializeAssets = (): Promise<void> => {
  buildTileSpriteMap();
  // Add UI asset loading/caching later if needed
  return Promise.resolve(); // No async loading needed just for URLs
};

/**
 * Gets the spritesheet URL and clipping info for a tile ID and state.
 * Calculates pixel coordinates from stored grid coordinates.
 * @param tileId The numeric ID of the tile (e.g., "0", "1").
 * @param state Optional state name (e.g., "open" for a door).
 * @returns An object with sheet URL and clipping coords { sheetUrl, sx, sy, sWidth, sHeight } or undefined.
 */
export const getTileRenderInfo = (
  tileId: string | number,
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
  const baseTileIdStr = String(tileId);
  let key = baseTileIdStr;
  if (state) {
    key = `${baseTileIdStr}_${state}`;
  }

  const spriteInfo = tileSpriteMap[key] || tileSpriteMap[baseTileIdStr]; // Fallback to base tile if state not found

  if (!spriteInfo) {
    console.warn(
      `Render info not found for tileId: ${tileId}, state: ${state}. Using fallback.`,
    );
    // Attempt to return fallback image info
    const fallbackUrl = "/assets/graphics/tiles/fallback.png";
    return {
      sheetUrl: fallbackUrl,
      sx: 0,
      sy: 0,
      sWidth: TILE_SIZE,
      sHeight: TILE_SIZE,
    };
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

/** Gets the full definition data (unchanged from previous version) */
export const getTileDefinition = (
  tileId: string | number,
): TileDefinition | undefined => {
  return tileDefinitions[String(tileId)];
};
