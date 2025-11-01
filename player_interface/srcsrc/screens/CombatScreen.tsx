// src/screens/CombatScreen.tsx
import React, { useState, useEffect } from "react";
import {
  type CombatEncounterResponse,
  type PlayerActionRequestPayload,
  type CharacterContextResponse,
  type NpcInstance,
} from "../types/apiTypes";
import {
  getCharacterContext,
  getLocationContext,
  postPlayerAction,
} from "../api/apiClient";

interface CombatScreenProps {
  combatContext: CombatEncounterResponse;
  onCombatEnd: () => void;
  activeCharacter: CharacterContextResponse;
}

type ParticipantFullState = (CharacterContextResponse | NpcInstance) & {
  actor_id: string;
  actor_type: "player" | "npc";
};

type CombatActionMenu =
  | "main"
  | "select_target"
  | "select_ability"
  | "select_item";

type PendingAction = {
  type: "attack" | "use_ability" | "use_item";
  id?: string;
  name: string;
};

const CombatScreen: React.FC<CombatScreenProps> = ({
  combatContext,
  onCombatEnd,
  activeCharacter,
}) => {
  const [turn, setTurn] = useState(combatContext.current_turn_index);
  const [participants, setParticipants] = useState<ParticipantFullState[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [log, setLog] = useState<string[]>(["Combat started!"]);
  const [currentMenu, setCurrentMenu] = useState<CombatActionMenu>("main");
  const [pendingAction, setPendingAction] = useState<PendingAction | null>(
    null,
  );
  const playerActorId = `player_${activeCharacter.id}`;
  const currentActorId = combatContext.turn_order[turn];
  const isPlayerTurn = currentActorId === playerActorId;

  const addLog = (message: string) => {
    console.log(message);
    setLog((prev) => [message, ...prev.slice(0, 9)]);
  };

  useEffect(() => {
    const fetchParticipantData = async () => {
      setIsLoading(true);
      addLog("Fetching participant data...");
      const fullParticipantData: ParticipantFullState[] = [];
      for (const actorId of combatContext.turn_order) {
        try {
          if (actorId.startsWith("player_")) {
            const charData = await getCharacterContext(actorId.split("_")[1]);
            fullParticipantData.push({
              ...charData,
              actor_id: actorId,
              actor_type: "player",
            });
          } else if (actorId.startsWith("npc_")) {
            const locData = await getLocationContext(combatContext.location_id);
            const npcData = locData.npc_instances.find(
              (npc) => `npc_${npc.id}` === actorId,
            );
            if (npcData) {
              fullParticipantData.push({
                ...npcData,
                actor_id: actorId,
                actor_type: "npc",
              });
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
  }, [combatContext]);

  const handlePlayerAction = async (targetId: string) => {
    if (!isPlayerTurn || !pendingAction) return;
    addLog(`Player performing: ${pendingAction.name} on ${targetId}...`);
    let payload: PlayerActionRequestPayload;
    switch (pendingAction.type) {
      case "attack":
        payload = { action: "attack", target_id: targetId };
        break;
      case "use_ability":
        payload = {
          action: "use_ability",
          ability_id: pendingAction.id,
          target_id: targetId,
        };
        break;
      case "use_item":
        payload = {
          action: "use_item",
          item_id: pendingAction.id,
          target_id: targetId,
        };
        break;
      default:
        addLog("Error: Unknown pending action type.");
        return;
    }
    try {
      const result = await postPlayerAction(combatContext.id, payload);
      result.log.forEach(addLog);
      if (result.success) {
        await refreshCombatState();
      } else {
        addLog(`Action failed: ${result.message}`);
      }
    } catch (err: any) {
      addLog(`Error performing action: ${err.message}`);
    } finally {
      setCurrentMenu("main");
      setPendingAction(null);
    }
  };

  const resetToMainMenu = () => {
    setCurrentMenu("main");
    setPendingAction(null);
  };
  const onSelectAttack = () => {
    setPendingAction({ type: "attack", name: "Attack" });
    setCurrentMenu("select_target");
  };
  const onSelectAbility = (ability: { id: string; name: string }) => {
    setPendingAction({
      type: "use_ability",
      id: ability.id,
      name: `Ability: ${ability.name}`,
    });
    setCurrentMenu("select_target");
  };
  const onSelectItem = (item: { template_id: string }) => {
    setPendingAction({
      type: "use_item",
      id: item.template_id,
      name: `Item: ${item.template_id}`,
    });
    setCurrentMenu("select_target");
  };
  const refreshCombatState = async () => {
    setIsLoading(true);
    addLog("Refreshing combat state...");
    const fullParticipantData: ParticipantFullState[] = [];
    let combatIsOver = false;
    let livingNpcs = 0;
    let livingPlayers = 0;
    for (const actorId of combatContext.turn_order) {
      try {
        if (actorId.startsWith("player_")) {
          const charData = await getCharacterContext(actorId.split("_")[1]);
          if (charData.character_sheet.combat_stats.current_hp > 0)
            livingPlayers++;
          fullParticipantData.push({
            ...charData,
            actor_id: actorId,
            actor_type: "player",
          });
        } else if (actorId.startsWith("npc_")) {
          const locData = await getLocationContext(combatContext.location_id);
          const npcData = locData.npc_instances.find(
            (npc) => `npc_${npc.id}` === actorId,
          );
          if (npcData) {
            if (npcData.current_hp > 0) livingNpcs++;
            fullParticipantData.push({
              ...npcData,
              actor_id: actorId,
              actor_type: "npc",
            });
          }
        }
      } catch (err) {
        /* ignore error */
      }
    }
    setParticipants(fullParticipantData);
    if (livingPlayers === 0) {
      addLog("All players are defeated. Game Over.");
      combatIsOver = true;
    } else if (livingNpcs === 0) {
      addLog("All enemies are defeated. Victory!");
      combatIsOver = true;
    }
    if (combatIsOver) {
      setTimeout(onCombatEnd, 3000);
    } else {
      setTurn((prevTurn) => (prevTurn + 1) % combatContext.turn_order.length);
      setIsLoading(false);
    }
  };

  const getParticipantHP = (p: ParticipantFullState) => {
    if (p.actor_type === "player") {
      const stats = (p as CharacterContextResponse).character_sheet
        .combat_stats;
      return `${stats.current_hp} / ${stats.max_hp}`;
    } else {
      const stats = p as NpcInstance;
      return `${stats.current_hp} / ${stats.max_hp}`;
    }
  };
  if (isLoading && participants.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        Loading Combat...
      </div>
    );
  }

  const livingNpcs = participants.filter(
    (p) => p.actor_type === "npc" && (p as NpcInstance).current_hp > 0,
  );

  const playerAbilities = activeCharacter.character_sheet.abilities || [];
  const playerInventory = activeCharacter.character_sheet.inventory || [];

  const renderMainMenu = () => (
    <div className="flex flex-col space-y-4">
      <h3 className="text-xl">Choose Action:</h3>
      <button
        onClick={onSelectAttack}
        className="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
      >
        Attack
      </button>
      <button
        onClick={() => setCurrentMenu("select_ability")}
        disabled={playerAbilities.length === 0}
        className="bg-blue-700 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        Use Ability
      </button>
      <button
        onClick={() => setCurrentMenu("select_item")}
        disabled={playerInventory.length === 0}
        className="bg-green-700 hover:bg-green-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        Use Item
      </button>
    </div>
  );

  const renderTargetSelectionMenu = () => (
    <div className="flex flex-col space-y-4">
      <h3 className="text-xl">Select Target for {pendingAction?.name}:</h3>
      {livingNpcs.map((npc) => (
        <button
          key={`target-${npc.actor_id}`}
          onClick={() => handlePlayerAction(npc.actor_id)}
          className="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
        >
          {npc.actor_id} (HP: {getParticipantHP(npc)})
        </button>
      ))}
      {livingNpcs.length === 0 && (
        <p className="text-gray-500">No living targets!</p>
      )}
      <button
        onClick={resetToMainMenu}
        className="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded"
      >
        Back
      </button>
    </div>
  );

  const renderAbilitySelectionMenu = () => (
    <div className="flex flex-col space-y-4">
      <h3 className="text-xl">Choose Ability:</h3>
      {playerAbilities.map((ability: any) => (
        <button
          key={ability.id || ability}
          onClick={() =>
            onSelectAbility({
              id: ability.id || ability,
              name: ability.name || ability,
            })
          }
          className="bg-blue-700 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          {ability.name || ability}
        </button>
      ))}
      <button
        onClick={resetToMainMenu}
        className="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded"
      >
        Back
      </button>
    </div>
  );

  const renderItemSelectionMenu = () => (
    <div className="flex flex-col space-y-4">
      <h3 className="text-xl">Choose Item:</h3>
      {playerInventory.map((item: any) => (
        <button
          key={item.id || item.template_id}
          onClick={() => onSelectItem(item)}
          className="bg-green-700 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
        >
          {item.template_id}
        </button>
      ))}
      <button
        onClick={resetToMainMenu}
        className="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded"
      >
        Back
      </button>
    </div>
  );

  const renderActionPanel = () => {
    if (!isPlayerTurn) {
      return <p className="text-xl text-gray-400 italic">Waiting for NPC...</p>;
    }
    switch (currentMenu) {
      case "main":
        return renderMainMenu();
      case "select_target":
        return renderTargetSelectionMenu();
      case "select_ability":
        return renderAbilitySelectionMenu();
      case "select_item":
        return renderItemSelectionMenu();
      default:
        return <p>Error: Unknown menu state</p>;
    }
  };
  return (
    <div className="flex h-full w-full p-4">
      {/* ... (Participant List - Left Side - Unchanged) ... */}
      <div className="w-1/4 bg-gray-800 p-4 border border-gray-700">
        <h2 className="text-xl font-bold mb-4">Participants</h2>
        {participants.map((p) => (
          <div
            key={p.actor_id}
            className={`p-2 my-1 ${p.actor_id === currentActorId ? "border-2 border-yellow-400" : ""}`}
          >
            <span
              className={
                p.actor_type === "player" ? "text-green-400" : "text-red-400"
              }
            >
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

        {/* --- ACTION PANEL (MODIFIED) --- */}
        <div className="flex-grow flex items-center justify-center">
          {renderActionPanel()}
        </div>

        {/* ... (Log Panel - Unchanged) ... */}
        <div className="h-48 bg-gray-800 p-4 border border-gray-700 overflow-y-auto">
          {log.map((msg, i) => (
            <p key={i} className="font-mono text-sm">
              {msg}
            </p>
          ))}
        </div>
      </div>

      {/* ... (Target Info - Right Side - Unchanged) ... */}
      <div className="w-1/4 bg-gray-800 p-4 border border-gray-700">
        <h2 className="text-xl font-bold mb-4">Target Info</h2>
        <p className="text-gray-500">(Select a target to see details)</p>
      </div>
    </div>
  );
};

export default CombatScreen;
