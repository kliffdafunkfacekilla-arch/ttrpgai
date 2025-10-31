// src/components/MapRenderer.tsx
import React from 'react';
// --- 1. RENAME imported function ---
import { getSpriteRenderInfo, TILE_SIZE } from '../assets/assetLoader';

interface MapRendererProps {
  mapData: number[][];
}

const MapRenderer: React.FC<MapRendererProps> = ({ mapData }) => {
  if (!mapData || mapData.length === 0) {
    return <div>No map data to display.</div>;
  }

  const mapHeight = mapData.length;
  const mapWidth = mapData[0].length;

  return (
    <div
      className="relative bg-black"
      style={{
        width: `${mapWidth * TILE_SIZE}px`,
        height: `${mapHeight * TILE_SIZE}px`,
      }}
    >
      {mapData.map((row, y) =>
        row.map((tileId, x) => {
          // --- 2. RENAME called function ---
          const renderInfo = getSpriteRenderInfo(tileId);

          if (!renderInfo) {
            return (
              <div
                key={`${x}-${y}`}
                className="absolute"
                style={{
                  left: `${x * TILE_SIZE}px`,
                  top: `${y * TILE_SIZE}px`,
                  width: `${TILE_SIZE}px`,
                  height: `${TILE_SIZE}px`,
                  backgroundColor: 'purple', // Easy to spot missing tiles
                }}
              />
            );
          }

          return (
            <div
              key={`${x}-${y}`}
              className="absolute"
              style={{
                left: `${x * TILE_SIZE}px`,
                top: `${y * TILE_SIZE}px`,
                width: `${TILE_SIZE}px`,
                height: `${TILE_SIZE}px`,
                backgroundImage: `url(${renderInfo.sheetUrl})`,
                backgroundPosition: `-${renderInfo.sx}px -${renderInfo.sy}px`,
              }}
            />
          );
        })
      )}
    </div>
  );
};

export default MapRenderer;
