// src/components/EntityRenderer.tsx
import React from 'react';
// --- 1. IMPORT CharacterContextResponse ---
import { type NpcInstance, type ItemInstance, type CharacterContextResponse } from '../types/apiTypes';
import { getSpriteRenderInfo, TILE_SIZE } from '../assets/assetLoader';

interface EntityRendererProps {
  npcs: NpcInstance[];
  items: ItemInstance[];
  // --- 2. ADD player PROP ---
  player: CharacterContextResponse | null;
}

const EntityRenderer: React.FC<EntityRendererProps> = ({ npcs, items, player }) => {

  return (
    <>
      {/* --- 3. ADD PLAYER RENDER LOGIC --- */}
      {player && player.character_sheet.location && (
        (() => {
          const { coordinates } = player.character_sheet.location;
          // Use "player_default" as the template_id from entity_definitions.json
          const renderInfo = getSpriteRenderInfo("player_default");

          if (!renderInfo) {
            console.warn("No render info for 'player_default'");
            return null;
          }

          if (!coordinates || !Array.isArray(coordinates) || coordinates.length < 2) {
             console.warn("Player has no coordinates. Skipping render.");
             return null;
          }

          const style = {
            left: `${coordinates[0] * TILE_SIZE}px`,
            top: `${coordinates[1] * TILE_SIZE}px`,
            width: `${TILE_SIZE}px`,
            height: `${TILE_SIZE}px`,
            backgroundImage: `url(${renderInfo.sheetUrl})`,
            backgroundPosition: `-${renderInfo.sx}px -${renderInfo.sy}px`,
          };

          return (
            <div
              key={`player-${player.id}`}
              className="absolute z-20" // z-20 so Player is above tiles and items
              style={style}
              title={player.name}
            />
          );
        })()
      )}

      {/* Render NPCs */}
      {npcs.map((npc) => {
        // --- 4. FIX HACK: Use the new coordinates field ---
        const { coordinates } = (npc as any);
        if (!coordinates || !Array.isArray(coordinates) || coordinates.length < 2) {
            // ... (console.warn) ...
            return null;
        }

        const renderInfo = getSpriteRenderInfo(npc.template_id);
        // ... (render logic) ...
        const style = {
          left: `${coordinates[0] * TILE_SIZE}px`,
          top: `${coordinates[1] * TILE_SIZE}px`,
          width: `${TILE_SIZE}px`,
          height: `${TILE_SIZE}px`,
          backgroundImage: `url(${renderInfo.sheetUrl})`,
          backgroundPosition: `-${renderInfo.sx}px -${renderInfo.sy}px`,
        };

        return (
          <div
            key={`npc-${npc.id}`}
            className="absolute z-10" // z-10 so NPCs are above tiles
            style={style}
            title={npc.name_override || npc.template_id}
          />
        );
      })}

      {/* Render Items */}
      {items.map((item) => {
        // --- 5. FIX HACK: Use the new coordinates field ---
        const { coordinates } = (item as any);
        if (!coordinates || !Array.isArray(coordinates) || coordinates.length < 2) {
            // ... (console.warn) ...
            return null;
        }

        const renderInfo = getSpriteRenderInfo(item.template_id);
        // ... (render logic) ...
        const style = {
          left: `${coordinates[0] * TILE_SIZE + TILE_SIZE / 4}px`,
          top: `${coordinates[1] * TILE_SIZE + TILE_SIZE / 4}px`,
          width: `${TILE_SIZE / 2}px`,
          height: `${TILE_SIZE / 2}px`,
          backgroundImage: `url(${renderInfo.sheetUrl})`,
          backgroundPosition: `-${renderInfo.sx / 2}px -${renderInfo.sy / 2}px`,
          backgroundSize: `${renderInfo.sWidth}px ${renderInfo.sHeight}px`,
        };

        return (
          <div
            key={`item-${item.id}`}
            className="absolute z-5" // z-5 so items are above tiles but below NPCs
            style={style}
            title={item.template_id}
          />
        );
      })}
    </>
  );
};

export default EntityRenderer;
