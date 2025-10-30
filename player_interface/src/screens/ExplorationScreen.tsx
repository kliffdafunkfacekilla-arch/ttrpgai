// src/screens/ExplorationScreen.tsx
import React, { useState, useEffect } from 'react';
// --- 1. IMPORT getCharacterContext ---
import { getLocationContext, getCharacterContext } from '../api/apiClient';
// --- 2. IMPORT CharacterContextResponse ---
import { type LocationContextResponse, type CharacterContextResponse } from '../types/apiTypes';
import MapRenderer from '../components/MapRenderer';
import EntityRenderer from '../components/EntityRenderer';

// --- 3. DEFINE A PLAYER ID (Placeholder) ---
// In a real app, this would come from a login or character selection screen
const PLAYER_CHARACTER_ID = 1; // Assumes character with ID 1 exists

const ExplorationScreen: React.FC = () => {
  const [location, setLocation] = useState<LocationContextResponse | null>(null);
  // --- 4. ADD STATE FOR PLAYER ---
  const [player, setPlayer] = useState<CharacterContextResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // --- 5. REFACTOR DATA FETCHING ---
    const fetchData = async () => {
      try {
        setIsLoading(true);

        // First, get the character context to find out *where* they are
        console.log(`Fetching character context for ID: ${PLAYER_CHARACTER_ID}`);
        const charData = await getCharacterContext(String(PLAYER_CHARACTER_ID));
        setPlayer(charData);

        const locationId = charData.character_sheet.location.current_location_id;
        console.log(`Character is at location ID: ${locationId}. Fetching location context.`);

        // Then, get the context for that location
        const locData = await getLocationContext(locationId);
        setLocation(locData);

        if (!locData.generated_map_data) {
            console.warn("Warning: Location data was fetched, but 'generated_map_data' is null or undefined.");
        }

      } catch (err: any) {
        console.error("Failed to fetch game context:", err);
        setError(err.message || "An unknown error occurred while fetching game data.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []); // Empty dependency array, runs once on mount

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Loading Game Data...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center h-full text-red-500">Error: {error}</div>;
  }

  // --- 6. UPDATE RENDER CHECKS ---
  if (!location || !player) {
    return <div className="flex items-center justify-center h-full text-yellow-500">Missing location or player data.</div>;
  }

  return (
    <div className="exploration-screen flex flex-col h-full w-full p-4 box-border">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">
          Exploring: {location.name} (ID: {location.id})
        </h1>
        {/* Display player name */}
        <p className="text-sm text-gray-400">Playing as: {player.name}</p>
      </header>

      <div className="map-container relative flex-grow overflow-auto bg-gray-800 border border-gray-700">
        {location.generated_map_data ? (
            <MapRenderer mapData={location.generated_map_data} />
        ) : (
            <div className="flex items-center justify-center h-full text-yellow-500">
                <p>Map data is missing for this location.</p>
            </div>
        )}

        {/* --- 7. PASS PLAYER TO RENDERER --- */}
        <EntityRenderer
          player={player}
          npcs={location.npc_instances}
          items={location.item_instances}
        />
      </div>

      <footer className="mt-4 h-32 bg-gray-800 border border-gray-700 p-4">
        <h3 className="font-bold">Event Log</h3>
        <p className="text-gray-400">You have entered the {location.name}.</p>
      </footer>
    </div>
  );
};

export default ExplorationScreen;
