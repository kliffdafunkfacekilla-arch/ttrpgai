// src/components/MapRenderer.tsx
import React from 'react';
import { getTileRenderInfo, TILE_SIZE } from '../assets/assetLoader';

interface MapRendererProps {
  mapData: number[][];
  // We can add tileStateData later if needed, e.g. for open doors
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
          const renderInfo = getTileRenderInfo(tileId);

          if (!renderInfo) {
            // Render a fallback or an empty space if tile info is missing
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