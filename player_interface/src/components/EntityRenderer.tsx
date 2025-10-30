// src/components/EntityRenderer.tsx
import React from 'react';
import { type NpcInstance, type ItemInstance } from '../types/apiTypes';

interface EntityRendererProps {
  npcs: NpcInstance[];
  items: ItemInstance[];
  // We'll add player position later
}

// Simple function to get a visual representation for an entity
// In the future, this will use the assetLoader like the MapRenderer
const getEntityStyle = (templateId: string): React.CSSProperties => {
  if (templateId.includes('goblin')) {
    return { backgroundColor: 'green', opacity: 0.8 };
  }
  if (templateId.includes('spider')) {
    return { backgroundColor: 'darkred', opacity: 0.8 };
  }
  if (templateId.includes('potion')) {
    return { backgroundColor: 'blue', opacity: 0.7, borderRadius: '50%' };
  }
  return { backgroundColor: 'gray', opacity: 0.7 };
};

const EntityRenderer: React.FC<EntityRendererProps> = ({ npcs, items }) => {
  // For now, we assume entities don't have specific map coordinates
  // and we'll just render placeholder indicators.
  // A future step is to add coordinates to NPCs/Items in the world_engine
  // and render them at the correct [x, y] position.

  // --- THIS IS A PLACEHOLDER RENDER ---
  // We'll update this when entities have coordinates.
  // For now, let's just list what's in the room.

  return (
    <div className="absolute top-0 left-0 p-4 bg-black bg-opacity-50 text-white pointer-events-none">
      <h3 className="text-lg font-bold">Entities Present:</h3>

      {/* Render NPCs */}
      <ul className="list-disc pl-5">
        {npcs.map((npc) => (
          <li key={npc.id} style={{ color: getEntityStyle(npc.template_id).backgroundColor || 'white' }}>
            {npc.name_override || npc.template_id} (HP: {npc.current_hp}/{npc.max_hp})
          </li>
        ))}
      </ul>

      {/* Render Items */}
      <ul className="list-disc pl-5 mt-2">
        {items.map((item) => (
          <li key={item.id} style={{ color: getEntityStyle(item.template_id).backgroundColor || 'cyan' }}>
            {item.template_id} (x{item.quantity})
          </li>
        ))}
      </ul>
    </div>
  );

  /* // --- FUTURE IMPLEMENTATION (when entities have coordinates) ---
  // This is what we're working towards:

  return (
    <>
      {npcs.map((npc) => {
        // Assuming npc.coordinates exists, e.g., [x, y]
        if (!npc.coordinates) return null;

        const style = {
          ...getEntityStyle(npc.template_id),
          left: `${npc.coordinates[0] * TILE_SIZE}px`,
          top: `${npc.coordinates[1] * TILE_SIZE}px`,
          width: `${TILE_SIZE}px`,
          height: `${TILE_SIZE}px`,
        };

        return (
          <div
            key={`npc-${npc.id}`}
            className="absolute z-10"
            style={style}
            title={npc.name_override || npc.template_id}
          />
        );
      })}

      {items.map((item) => {
        // Assuming item.coordinates exists, e.g., [x, y]
        if (!item.coordinates) return null;

        const style = {
          ...getEntityStyle(item.template_id),
          left: `${item.coordinates[0] * TILE_SIZE + TILE_SIZE / 4}px`, // Offset for items
          top: `${item.coordinates[1] * TILE_SIZE + TILE_SIZE / 4}px`,
          width: `${TILE_SIZE / 2}px`,
          height: `${TILE_SIZE / 2}px`,
        };

        return (
          <div
            key={`item-${item.id}`}
            className="absolute z-5"
            style={style}
            title={item.template_id}
          />
        );
      })}
    </>
  );
  */
};

export default EntityRenderer;
