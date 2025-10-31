// src/screens/CombatScreen.tsx
import React, { useState, useEffect } from 'react';
import {
    type CombatEncounterResponse,
    type PlayerActionRequestPayload,
    type CharacterContextResponse, // For player HP
    type NpcInstance              // For NPC HP
} from '../types/apiTypes';
import {
    getCharacterContext,
    getLocationContext,
    postPlayerAction
} from '../api/apiClient';

// --- 1. DEFINE PROPS ---
interface CombatScreenProps {
  combatContext: CombatEncounterResponse;
  onCombatEnd: () => void;
}

// --- 2. ADD HELPER TYPE FOR PARTICIPANT STATE ---
type ParticipantFullState = (CharacterContextResponse | NpcInstance) & {
    actor_id: string;
    actor_type: 'player' | 'npc';
};

// --- 3. DEFINE PLAYER ID (Placeholder) ---
const PLAYER_ACTOR_ID = "player_1"; // This should match the ID used in ExplorationScreen

const CombatScreen: React.FC<CombatScreenProps> = ({ combatContext, onCombatEnd }) => {
  const [turn, setTurn] = useState(combatContext.current_turn_index);
  const [participants, setParticipants] = useState<ParticipantFullState[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [log, setLog] = useState<string[]>(['Combat started!']);

  const currentActorId = combatContext.turn_order[turn];
  const isPlayerTurn = currentActorId === PLAYER_ACTOR_ID;

  // --- 4. ADD LOGGING FUNCTION ---
  const addLog = (message: string) => {
    console.log(message);
    setLog(prev => [message, ...prev.slice(0, 9)]); // Keep last 10 messages
  };

  // --- 5. DATA FETCHING EFFECT (To get full participant stats/HP) ---
  useEffect(() => {
    const fetchParticipantData = async () => {
      setIsLoading(true);
      addLog("Fetching participant data...");
      const fullParticipantData: ParticipantFullState[] = [];

      for (const actorId of combatContext.turn_order) {
        try {
          if (actorId.startsWith('player_')) {
            const charData = await getCharacterContext(actorId.split('_')[1]);
            fullParticipantData.push({ ...charData, actor_id: actorId, actor_type: 'player' });
          } else if (actorId.startsWith('npc_')) {
            // We need to fetch NPC data from the *location* context
            // In a real app, a direct get_npc(id) would be better
            const locData = await getLocationContext(combatContext.location_id);
            const npcData = locData.npc_instances.find(npc => `npc_${npc.id}` === actorId);
            if (npcData) {
              fullParticipantData.push({ ...npcData, actor_id: actorId, actor_type: 'npc' });
            }
          }
        } catch (err: any) {
          addLog(`Error fetching data for ${actorId}: ${err.message}`);
        }
      }
      setParticipants(fullParticipantData);
      setIsLoading(false);
    };

    fetchParticipantData();
  }, [combatContext]); // Re-fetch if combatContext ever changes

  // --- 6. ACTION HANDLER ---
  const handlePlayerAttack = async (targetId: string) => {
    if (!isPlayerTurn) return;
    addLog(`Player attacking ${targetId}...`);

    const payload: PlayerActionRequestPayload = {
      action: 'attack',
      target_id: targetId
    };

    try {
      const result = await postPlayerAction(combatContext.id, payload);

      // Add all logs from the backend
      result.log.forEach(addLog);

      if (result.success) {
        // Action succeeded, backend advanced the turn.
        // We need to refresh all participant data to see new HP, etc.
        // And check if combat ended.
        await refreshCombatState();
      } else {
        addLog(`Action failed: ${result.message}`);
      }
    } catch (err: any) {
      addLog(`Error attacking: ${err.message}`);
    }
  };

  // --- 7. STATE REFRESH FUNCTION ---
  const refreshCombatState = async () => {
    setIsLoading(true);
    addLog("Refreshing combat state...");

    // This is a simplified refresh.
    // A better way would be a GET /v1/combat/{id}/state endpoint
    // For now, we just re-fetch all participants.

    const fullParticipantData: ParticipantFullState[] = [];
    let combatIsOver = false;
    let livingNpcs = 0;
    let livingPlayers = 0;

    for (const actorId of combatContext.turn_order) {
      try {
        if (actorId.startsWith('player_')) {
          const charData = await getCharacterContext(actorId.split('_')[1]);
          if (charData.character_sheet.combat_stats.current_hp > 0) livingPlayers++;
          fullParticipantData.push({ ...charData, actor_id: actorId, actor_type: 'player' });
        } else if (actorId.startsWith('npc_')) {
          // This is a bit inefficient, but works for now
          const locData = await getLocationContext(combatContext.location_id);
          const npcData = locData.npc_instances.find(npc => `npc_${npc.id}` === actorId);
          if (npcData) {
            if (npcData.current_hp > 0) livingNpcs++;
            fullParticipantData.push({ ...npcData, actor_id: actorId, actor_type: 'npc' });
          }
        }
      } catch (err) { /* ignore single-entity-fetch error */ }
    }

    setParticipants(fullParticipantData);

    // Check for combat end
    if (livingPlayers === 0) {
      addLog("All players are defeated. Game Over.");
      combatIsOver = true;
    } else if (livingNpcs === 0) {
      addLog("All enemies are defeated. Victory!");
      combatIsOver = true;
    }

    if (combatIsOver) {
      setTimeout(onCombatEnd, 3000); // Wait 3s then call end
    } else {
      // Manually advance turn index on frontend to match backend
      setTurn((prevTurn) => (prevTurn + 1) % combatContext.turn_order.length);
      setIsLoading(false);
    }
  };

  // --- 8. HELPER TO GET PARTICIPANT HP ---
  const getParticipantHP = (p: ParticipantFullState) => {
    if (p.actor_type === 'player') {
      const stats = (p as CharacterContextResponse).character_sheet.combat_stats;
      return `${stats.current_hp} / ${stats.max_hp}`;
    } else {
      const stats = (p as NpcInstance);
      return `${stats.current_hp} / ${stats.max_hp}`;
    }
  };

  // --- 9. RENDER LOGIC ---
  if (isLoading && participants.length === 0) {
    return <div className="flex items-center justify-center h-full">Loading Combat...</div>;
  }

  const livingNpcs = participants.filter(p =>
    p.actor_type === 'npc' && (p as NpcInstance).current_hp > 0
  );

  return (
    <div className="flex h-full w-full p-4">
      {/* Participant List (Left Side) */}
      <div className="w-1/4 bg-gray-800 p-4 border border-gray-700">
        <h2 className="text-xl font-bold mb-4">Participants</h2>
        {participants.map((p) => (
          <div
            key={p.actor_id}
            className={`p-2 my-1 ${p.actor_id === currentActorId ? 'border-2 border-yellow-400' : ''}`}
          >
            <span className={p.actor_type === 'player' ? 'text-green-400' : 'text-red-400'}>
              {p.actor_id}
            </span>
            <span className="text-sm text-gray-300 ml-4">
              HP: {getParticipantHP(p)}
            </span>
          </div>
        ))}
      </div>

      {/* Action / Log (Center) */}
      <div className="w-1/2 flex flex-col p-4">
        <h2 className="text-2xl font-bold text-center">
          Turn: {currentActorId}
        </h2>

        {/* Action Panel */}
        <div className="flex-grow flex items-center justify-center">
          {!isPlayerTurn && (
            <p className="text-xl text-gray-400 italic">Waiting for NPC...</p>
          )}
          {isPlayerTurn && (
            <div className="flex flex-col space-y-4">
              <h3 className="text-xl">Choose Action:</h3>
              {livingNpcs.map(npc => (
                <button
                  key={`attack-${npc.actor_id}`}
                  onClick={() => handlePlayerAttack(npc.actor_id)}
                  className="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
                >
                  Attack {npc.actor_id}
                </button>
              ))}
              {livingNpcs.length === 0 && (
                <p className="text-gray-500">No living targets!</p>
              )}
            </div>
          )}
        </div>

        {/* Log Panel */}
        <div className="h-48 bg-gray-800 p-4 border border-gray-700 overflow-y-auto">
          {log.map((msg, i) => (
            <p key={i} className="font-mono text-sm">{msg}</p>
          ))}
        </div>
      </div>

      {/* Target Info (Right Side - Placeholder) */}
      <div className="w-1/4 bg-gray-800 p-4 border border-gray-700">
         <h2 className="text-xl font-bold mb-4">Target Info</h2>
         <p className="text-gray-500">(Select a target to see details)</p>
      </div>
    </div>
  );
};

export default CombatScreen;
