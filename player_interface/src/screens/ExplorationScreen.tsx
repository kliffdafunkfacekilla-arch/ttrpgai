// src/screens/ExplorationScreen.tsx
import React, { useState, useEffect, useCallback } from "react";
import {
  getLocationContext,
  // --- MODIFIED: Use fetchCharacterContext ---
  fetchCharacterContext,
  updatePlayerLocation,
  postInteraction,
  startCombat,
} from "../api/apiClient";
import {
  type LocationContextResponse,
  type CharacterContextResponse,
  type InteractionRequestPayload,
  type CombatStartRequestPayload,
  type CombatEncounterResponse,
  type NpcInstance,
} from "../types/apiTypes";
import MapRenderer from "../components/MapRenderer";
import EntityRenderer from "../components/EntityRenderer";
import { getTileDefinition } from "../assets/assetLoader";

interface ExplorationScreenProps {
  onCombatStart: (combatData: CombatEncounterResponse) => void;
  activeCharacter: CharacterContextResponse;
  onExitToMenu: () => void;
  onShowCharacterSheet: () => void;
}

const ExplorationScreen: React.FC<ExplorationScreenProps> = ({
  onCombatStart,
  activeCharacter,
  onExitToMenu,
  onShowCharacterSheet,
}) => {
  const [location, setLocation] = useState<LocationContextResponse | null>(
    null,
  );
  const [player, setPlayer] = useState<CharacterContextResponse | null>(
    activeCharacter,
  );
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [eventLog, setEventLog] = useState<string[]>([]);
  const [isTakingTurn, setIsTakingTurn] = useState(false);

  const addLog = useCallback((message: string) => {
    console.log(message);
    setEventLog((prevLog) => [message, ...prevLog.slice(0, 4)]);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      if (!player) return;

      try {
        setIsLoading(true);
        addLog(`Loading data for ${player.name}...`);
        const locationId = player.character_sheet.location.current_location_id;
        addLog(`Loading location ${locationId}...`);
        // This function will now exist
        const locData = await getLocationContext(String(locationId));
        setLocation(locData);
        addLog(`You have entered the ${locData.name}.`);
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "An unknown error occurred while fetching game data.";
        console.error("Failed to fetch game context:", err);
        setError(message);
        addLog(`Error: ${message}`);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [player, addLog]);

  const handleMove = useCallback(
    async (dx: number, dy: number) => {
      if (!player || !location || !location.generated_map_data || isTakingTurn)
        return;
      setIsTakingTurn(true);
      const [currX, currY] = player.character_sheet.location.coordinates;
      const newX = currX + dx;
      const newY = currY + dy;
      const locId = player.character_sheet.location.current_location_id;
      const npcAtTargetTile = location.npc_instances.find(
        (npc: NpcInstance) => {
          const coords = npc.coordinates;
          return coords && coords[0] === newX && coords[1] === newY;
        },
      );
      if (npcAtTargetTile) {
        if (npcAtTargetTile.behavior_tags.includes("aggressive")) {
          addLog(`You encounter a hostile ${npcAtTargetTile.template_id}!`);
          const allNpcTemplateIds = location.npc_instances.map(
            (npc) => npc.template_id,
          );
          const payload: CombatStartRequestPayload = {
            location_id: locId,
            player_ids: [`player_${player.id}`],
            npc_template_ids: allNpcTemplateIds,
          };
          try {
            const combatData = await startCombat(payload);
            addLog(`Combat started! (ID: ${combatData.id})`);
            onCombatStart(combatData);
          } catch (err) {
            const message =
              err instanceof Error
                ? err.message
                : "An unknown error occurred while starting combat.";
            addLog(`Failed to start combat: ${message}`);
            setIsTakingTurn(false);
          }
          return;
        } else {
          addLog(`${npcAtTargetTile.template_id} is blocking the way.`);
          setIsTakingTurn(false);
          return;
        }
      }
      if (
        newY < 0 ||
        newY >= location.generated_map_data.length ||
        newX < 0 ||
        newX >= location.generated_map_data[0].length
      ) {
        addLog("You can't move that way (bounds).");
        setIsTakingTurn(false);
        return;
      }
      const tileId = location.generated_map_data[newY][newX];
      const tileDef = getTileDefinition(tileId);
      if (!tileDef || !tileDef.passable) {
        addLog(`You can't move through a ${tileDef?.name || "wall"}.`);
        setIsTakingTurn(false);
        return;
      }
      try {
        addLog(`Moving to [${newX}, ${newY}]...`);
        // This function will now exist
        const updatedPlayer = await updatePlayerLocation(
          player.id,
          String(locId),
          [newX, newY],
        );
        setPlayer(updatedPlayer);
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "An unknown error occurred while moving.";
        addLog(`Move failed: ${message}`);
      } finally {
        setIsTakingTurn(false);
      }
    },
    [player, location, isTakingTurn, onCombatStart, addLog],
  );

  const handleInteract = useCallback(async () => {
    if (!player || !location || !location.ai_annotations || isTakingTurn)
      return;
    setIsTakingTurn(true);
    const [currX, currY] = player.character_sheet.location.coordinates;
    const locId = player.character_sheet.location.current_location_id;
    const targetObjectId = Object.keys(location.ai_annotations).find((key) => {
      const obj = location.ai_annotations![key];
      return (
        obj.coordinates &&
        obj.coordinates[0] === currX &&
        obj.coordinates[1] === currY
      );
    });
    if (!targetObjectId) {
      addLog("There is nothing to interact with here.");
      setIsTakingTurn(false);
      return;
    }
    try {
      addLog(`Interacting with ${targetObjectId}...`);
      const payload: InteractionRequestPayload = {
        actor_id: `player_${player.id}`,
        location_id: locId,
        target_object_id: targetObjectId,
        interaction_type: "use",
      };
      const result = await postInteraction(payload);
      addLog(result.message);
      if (result.success && result.updated_annotations) {
        addLog("Reloading location state...");
        const newLocData = await getLocationContext(String(locId));
        setLocation(newLocData);
        if (result.items_added && result.items_added.length > 0) {
          // --- MODIFIED: Use fetchCharacterContext ---
          const newPlayerData = await fetchCharacterContext(String(player.id));
          setPlayer(newPlayerData);
        }
      }
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "An unknown error occurred during interaction.";
      addLog(`Interaction failed: ${message}`);
    } finally {
      setIsTakingTurn(false);
    }
  }, [player, location, isTakingTurn, addLog]);

  const handleShowCharacterSheet = useCallback(() => {
    if (isTakingTurn) return; // Don't open menu while moving
    addLog("Opening Character Sheet...");
    onShowCharacterSheet(); // Call the prop passed down from App.tsx
  }, [isTakingTurn, onShowCharacterSheet, addLog]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isTakingTurn) return;
      switch (e.key) {
        case "w":
          handleMove(0, -1);
          break;
        case "s":
          handleMove(0, 1);
          break;
        case "a":
          handleMove(-1, 0);
          break;
        case "d":
          handleMove(1, 0);
          break;
        case "e":
          handleInteract();
          break;
        case "c":
          handleShowCharacterSheet();
          break;
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleMove, handleInteract, handleShowCharacterSheet, isTakingTurn]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        Loading Game Data...
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        Error: {error}
      </div>
    );
  }
  if (!location || !player) {
    return (
      <div className="flex items-center justify-center h-full text-yellow-500">
        Missing location or player data.
      </div>
    );
  }

  return (
    <div className="exploration-screen flex flex-col h-full w-full p-4 box-border">
      <header className="mb-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">
            Exploring: {location.name} (ID: {location.id})
          </h1>
          <p className="text-sm text-gray-400">
            Playing as: {player.name} at [
            {player.character_sheet.location.coordinates.join(", ")}]
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleShowCharacterSheet}
            className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 px-4 rounded-lg"
          >
            Character (C)
          </button>
          <button
            onClick={onExitToMenu}
            className="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg"
          >
            Exit to Menu
          </button>
        </div>
      </header>
      <div className="map-container relative flex-grow overflow-auto bg-gray-800 border border-gray-700">
        {location.generated_map_data ? (
          <MapRenderer mapData={location.generated_map_data} />
        ) : (
          <div className="flex items-center justify-center h-full text-yellow-500">
            <p>Map data is missing for this location.</p>
          </div>
        )}
        <EntityRenderer
          player={player}
          npcs={location.npc_instances}
          items={location.item_instances}
        />
      </div>
      <footer className="mt-4 h-32 bg-gray-800 border border-gray-700 p-4 overflow-y-auto">
        <h3 className="font-bold">Event Log</h3>
        {eventLog.length === 0 && (
          <p className="text-gray-400">
            Use W, A, S, D to move. Use E to interact.
          </p>
        )}
        {eventLog.map((msg, index) => (
          <p key={index} className="text-gray-300">
            {msg}
          </p>
        ))}
      </footer>
    </div>
  );
};

export default ExplorationScreen;
