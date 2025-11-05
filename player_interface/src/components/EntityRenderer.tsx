// src/components/EntityRenderer.tsx
import React from "react";
import {
    type NpcInstance,
    type ItemInstance,
    type CharacterContextResponse,
} from "../types/apiTypes";
import { getSpriteRenderInfo, TILE_SIZE } from "../assets/assetLoader";

interface EntityRendererProps {
    npcs: NpcInstance[];
    items: ItemInstance[];
    player: CharacterContextResponse | null;
}

const EntityRenderer: React.FC<EntityRendererProps> = ({
    npcs,
    items,
    player,
}) => {
    return (
        <>
            {/* --- MODIFICATION: Use flat structure --- */}
            {player &&
                (() => {
                    // Use top-level position_x and position_y
                    const { position_x, position_y } = player;
                    const coordinates: [number, number] = [position_x, position_y];
                    // --- END MODIFICATION ---

                    // Use "player_default" as the template_id from entity_definitions.json
                    const renderInfo = getSpriteRenderInfo("player_default");

                    if (!renderInfo) {
                        console.warn("No render info for 'player_default'");
                        return null;
                    }

                    if (
                        !coordinates ||
                        !Array.isArray(coordinates) ||
                        coordinates.length < 2
                    ) {
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
                })()}

            {/* Render NPCs */}
            {(npcs || []).map((npc) => {
                const { coordinates } = npc;
                if (
                    !coordinates ||
                    !Array.isArray(coordinates) ||
                    coordinates.length < 2
                ) {
                    console.warn(
                        `NPC ${npc.template_id} (ID: ${npc.id}) has no coordinates. Skipping render.`,
                    );
                    return null;
                }

                const renderInfo = getSpriteRenderInfo(npc.template_id);
                // ... (render logic) ...
                const style = {
                    left: `${coordinates[0] * TILE_SIZE}px`,
                    top: `${coordinates[1] * TILE_SIZE}px`,
                    width: `${TILE_SIZE}px`,
                    height: `${TILE_SIZE}px`,
                    backgroundImage: `url(${renderInfo?.sheetUrl})`,
                    backgroundPosition: `-${renderInfo?.sx}px -${renderInfo?.sy}px`,
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
            {(items || []).map((item) => {
                const { coordinates } = item;
                if (
                    !coordinates ||
                    !Array.isArray(coordinates) ||
                    coordinates.length < 2
                ) {
                    console.warn(
                        `Item ${item.template_id} (ID: ${item.id}) has no coordinates. Skipping render.`,
                    );
                    return null;
                }

                const renderInfo = getSpriteRenderInfo(item.template_id);
                if (!renderInfo) {
                    console.warn(`No render info for Item template: ${item.template_id}`);
                    return null;
                }
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