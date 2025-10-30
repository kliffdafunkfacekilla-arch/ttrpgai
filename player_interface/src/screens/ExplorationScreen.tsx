// src/screens/ExplorationScreen.tsx
import React, { useState, useEffect } from 'react';
import { getLocationContext } from '../api/apiClient';
import { type LocationContextResponse } from '../types/apiTypes';
import MapRenderer from '../components/MapRenderer'; // Import the MapRenderer
import EntityRenderer from '../components/EntityRenderer'; // --- IMPORT NEW COMPONENT ---

const ExplorationScreen: React.FC = () => {
  const [location, setLocation] = useState<LocationContextResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const locationId = 1;

    console.log(`Fetching location context for ID: ${locationId}`);
    getLocationContext(locationId)
      .then(data => {
        console.log("Location context received:", data);
        if (!data.generated_map_data) {
            console.warn("Warning: Location data was fetched, but 'generated_map_data' is null or undefined.");
        }
        setLocation(data);
      })
      .catch(err => {
        console.error("Failed to fetch location context:", err);
        setError(err.message || "An unknown error occurred while fetching location data.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  if (isLoading) {
    return <div className="flex items-center justify-center h-full">Loading Exploration Screen...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center h-full text-red-500">Error: {error}</div>;
  }

  if (!location) {
    return <div className="flex items-center justify-center h-full text-yellow-500">No location data could be loaded.</div>;
  }

  return (
    <div className="exploration-screen flex flex-col h-full w-full p-4 box-border">
      <header className="mb-4">
        <h1 className="text-2xl font-bold">
          Exploring: {location.name} (ID: {location.id})
        </h1>
        <p className="text-sm text-gray-400">{location.region.name}</p>
      </header>

      {/* Container for the map with scrolling */}
      {/* --- MODIFICATION: Make container relative --- */}
      <div className="map-container relative flex-grow overflow-auto bg-gray-800 border border-gray-700">
        {location.generated_map_data ? (
            <MapRenderer mapData={location.generated_map_data} />
        ) : (
            <div className="flex items-center justify-center h-full text-yellow-500">
                <p>Map data is missing for this location.</p>
            </div>
        )}

        {/* --- ADD ENTITY RENDERER --- */}
        {/* It will overlay on top of the MapRenderer */}
        <EntityRenderer
          npcs={location.npc_instances}
          items={location.item_instances}
        />
      </div>

      {/* --- ADD UI PANEL (Placeholder) --- */}
      <footer className="mt-4 h-32 bg-gray-800 border border-gray-700 p-4">
        <h3 className="font-bold">Event Log</h3>
        <p className="text-gray-400">You have entered the {location.name}.</p>
        {/* We will populate this log with messages from interactions and combat */}
      </footer>
    </div>
  );
};

export default ExplorationScreen;
