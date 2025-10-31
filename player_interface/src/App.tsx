// src/App.tsx
import { useState } from 'react';
import './App.css';
import MainMenuScreen from './screens/MainMenuScreen';
import ExplorationScreen from './screens/ExplorationScreen';
import CombatScreen from './screens/CombatScreen';
import { type CombatEncounterResponse } from './types/apiTypes';

type GameScreen = 'MainMenu' | 'Exploration' | 'Combat' | 'CharacterSheet';

function App() {
    const [currentScreen, setCurrentScreen] = useState<GameScreen>('MainMenu');
    const [combatContext, setCombatContext] = useState<CombatEncounterResponse | null>(null);

    // (handleStartNewGame and handleLoadGame are unchanged) ...
    const handleStartNewGame = () => {
        console.log("Starting New Game... Navigating to Exploration screen.");
        setCurrentScreen('Exploration');
    };

    const handleLoadGame = () => {
        console.log("Loading Game...");
        alert("Load Game clicked (Not implemented)");
    };

    const handleCombatStart = (combatData: CombatEncounterResponse) => {
        console.log(`App: Starting combat ${combatData.id}`);
        setCombatContext(combatData);
        setCurrentScreen('Combat');
    };

    // --- 1. ADD HANDLER FOR ENDING COMBAT ---
    const handleCombatEnd = () => {
        console.log("App: Combat has ended. Returning to Exploration.");
        setCombatContext(null); // Clear combat state
        setCurrentScreen('Exploration'); // Switch back to exploration
    };

    const renderScreen = () => {
        switch (currentScreen) {
            case 'MainMenu':
                return <MainMenuScreen
                          onStartNewGame={handleStartNewGame}
                          onLoadGame={handleLoadGame}
                        />;
            case 'Exploration':
                return <ExplorationScreen onCombatStart={handleCombatStart} />;

            case 'Combat':
                if (!combatContext) {
                    // This should not happen, but good to have a fallback
                    console.error("In Combat screen but no combat context!");
                    setCurrentScreen('Exploration'); // Go back
                    return null;
                }
                // --- 2. PASS NEW HANDLER TO COMBAT SCREEN ---
                return <CombatScreen
                          combatContext={combatContext}
                          onCombatEnd={handleCombatEnd}
                        />;

            default:
                return <div>Unknown Screen</div>;
        }
    };

    return (
        <div className="app-container w-screen h-screen bg-gray-900 text-white overflow-hidden">
            {renderScreen()}
        </div>
    );
}

export default App;
