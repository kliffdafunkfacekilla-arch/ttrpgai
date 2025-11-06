
// src/App.tsx
import { useState, useEffect } from "react";
import "./App.css";
import MainMenuScreen from "./screens/MainMenuScreen";
import ExplorationScreen from "./screens/ExplorationScreen";
import CombatScreen from "./screens/CombatScreen";
import { createDefaultTestCharacter } from "./api/apiClient";
import {
  type CombatEncounterResponse,
  type CharacterContextResponse,
} from "./types/apiTypes";

import CharacterSelectScreen from "./screens/CharacterSelectScreen";
import CharacterCreationScreen from "./screens/CharacterCreationScreen";
import CharacterSheetScreen from "./screens/CharacterSheetScreen";

type GameScreen =
  | "MainMenu"
  | "CharacterCreate"
  | "CharacterSelect"
  | "Exploration"
  | "Combat"
  | "CharacterSheet";

function App() {
  const [currentScreen, setCurrentScreen] = useState<GameScreen>("MainMenu");
  const [combatContext, setCombatContext] =
    useState<CombatEncounterResponse | null>(null);
  const [activeCharacter, setActiveCharacter] =
    useState<CharacterContextResponse | null>(null);
  const [showCharacterSheet, setShowCharacterSheet] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // This effect handles the screen transition after a character is loaded or created.
  useEffect(() => {
    if (activeCharacter && currentScreen === "MainMenu") {
      setCurrentScreen("Exploration");
    }
  }, [activeCharacter, currentScreen]);

  const handleQuickStart = async () => {
    setIsLoading(true);
    try {
      const newChar = await createDefaultTestCharacter();
      setActiveCharacter(newChar); // This will trigger the useEffect to change screen
    } catch (error) {
      console.error("Failed to create default character:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCombatStart = (combatData: CombatEncounterResponse) => {
    setCombatContext(combatData);
    setCurrentScreen("Combat");
  };
  const handleCombatEnd = () => {
    setCombatContext(null);
    setCurrentScreen("Exploration");
  };

  const handleCharacterSelected = (character: CharacterContextResponse) => {
    setActiveCharacter(character);
    setCurrentScreen("Exploration");
  };

  const handleCharacterCreated = (character: CharacterContextResponse) => {
    setActiveCharacter(character);
    setCurrentScreen("Exploration");
  };

  const handleExitToMenu = () => {
    setActiveCharacter(null);
    setCombatContext(null);
    setCurrentScreen("MainMenu");
  };

  const renderScreen = () => {
    switch (currentScreen) {
      case "MainMenu":
        return (
          <MainMenuScreen
            onStartNewGame={() => setCurrentScreen("CharacterCreate")}
            onQuickStart={handleQuickStart}
            isLoading={isLoading}
          />
        );
      case "CharacterSelect":
        return (
          <CharacterSelectScreen
            onCharacterSelected={handleCharacterSelected}
            onBack={() => setCurrentScreen("MainMenu")}
          />
        );
      case "CharacterCreate":
        return (
          <CharacterCreationScreen
            onCharacterCreated={handleCharacterCreated}
            onBack={() => setCurrentScreen("MainMenu")}
          />
        );
      case "Exploration":
        if (!activeCharacter) {
          handleExitToMenu();
          return null;
        }
        return (
          <ExplorationScreen
            key={activeCharacter.id}
            activeCharacter={activeCharacter}
            onCombatStart={handleCombatStart}
            onExitToMenu={handleExitToMenu}
            onShowCharacterSheet={() => setShowCharacterSheet(true)}
          />
        );
      case "Combat":
        if (!combatContext || !activeCharacter) {
          handleExitToMenu();
          return null;
        }
        return (
          <CombatScreen
            combatContext={combatContext}
            activeCharacter={activeCharacter}
            onCombatEnd={handleCombatEnd}
          />
        );
      default:
        return <div>Unknown Screen</div>;
    }
  };

  return (
    <div className="app-container min-h-screen bg-dungeon text-stone-100 font-sans overflow-hidden">
      <div className="fixed inset-0 opacity-10 pointer-events-none bg-noise" />
      {renderScreen()}
      {showCharacterSheet && activeCharacter && (
        <div className="absolute top-0 left-0 w-full h-full bg-black bg-opacity-75 z-40">
          <CharacterSheetScreen
            character={activeCharacter}
            onClose={() => setShowCharacterSheet(false)}
          />
        </div>
      )}
    </div>
  );
}

export default App;
