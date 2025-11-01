// src/App.tsx
import { useState } from 'react';
import './App.css';
import MainMenuScreen from './screens/MainMenuScreen';
import ExplorationScreen from './screens/ExplorationScreen';
import CombatScreen from './screens/CombatScreen';
import {
    type CombatEncounterResponse,
    type CharacterContextResponse
} from './types/apiTypes';

import CharacterSelectScreen from './screens/CharacterSelectScreen';
import CharacterCreateScreen from './screens/CharacterCreateScreen';
// --- 2. IMPORT THE NEW SCREEN ---
import CharacterSheetScreen from './screens/CharacterSheetScreen';

type GameScreen = 'MainMenu' | 'CharacterSelect' | 'CharacterCreate' | 'Exploration' | 'Combat' | 'CharacterSheet';

function App() {
    const [currentScreen, setCurrentScreen] = useState<GameScreen>('MainMenu');
    const [combatContext, setCombatContext] = useState<CombatEncounterResponse | null>(null);
    const [activeCharacter, setActiveCharacter] = useState<CharacterContextResponse | null>(null);

    // --- 1. ADD NEW STATE ---
    const [showCharacterSheet, setShowCharacterSheet] = useState(false);

    // ... (handleCombatStart, handleCombatEnd, handleCharacterSelected, etc. are unchanged)
    const handleCombatStart = (combatData: CombatEncounterResponse) => {
        setCombatContext(combatData);
        setCurrentScreen('Combat');
    };
    const handleCombatEnd = () => {
        setCombatContext(null);
        setCurrentScreen('Exploration');
    };
    const handleCharacterSelected = (character: CharacterContextResponse) => {
        console.log(`Character selected: ${character.id} - ${character.name}`);
        setActiveCharacter(character);
        setCurrentScreen('Exploration');
    };

    const handleCharacterCreated = (character: CharacterContextResponse) => {
        console.log(`Character created: ${character.id} - ${character.name}`);
        setActiveCharacter(character);
        setCurrentScreen('Exploration');
    };

    const handleExitToMenu = () => {
        console.log("Exiting to Main Menu...");
        setActiveCharacter(null);
        setCombatContext(null);
        setCurrentScreen('MainMenu');
    };

    const renderScreen = () => {
        switch (currentScreen) {
            case 'MainMenu':
                return <MainMenuScreen
                    onStartNewGame={() => setCurrentScreen('CharacterCreate')}
                    onLoadGame={() => setCurrentScreen('CharacterSelect')}
                />;
            case 'CharacterSelect':
                return <CharacterSelectScreen
                    onCharacterSelected={handleCharacterSelected}
                    onBack={() => setCurrentScreen('MainMenu')}
                />;

            case 'CharacterCreate':
                return <CharacterCreateScreen
                    onCharacterCreated={handleCharacterCreated}
                    onBack={() => setCurrentScreen('MainMenu')}
                />;
            case 'Exploration':
                if (!activeCharacter) {
                    // ... (fallback unchanged)
                    console.error("In Exploration screen but no active character!");
                    handleExitToMenu();
                    return null;
                }
                return <ExplorationScreen
                    key={activeCharacter.id}
                    activeCharacter={activeCharacter}
                    onCombatStart={handleCombatStart}
                    onExitToMenu={handleExitToMenu}
                    // --- 3. PASS THE HANDLER DOWN ---
                    onShowCharacterSheet={() => setShowCharacterSheet(true)}
                />;

            case 'Combat':
                if (!combatContext || !activeCharacter) {
                    // ... (fallback unchanged)
                    console.error("In Combat screen but no combat or character context!");
                    handleExitToMenu();
                    return null;
                }
                return <CombatScreen
                    combatContext={combatContext}
                    activeCharacter={activeCharacter}
                    onCombatEnd={handleCombatEnd}
                // We could also pass onShowCharacterSheet here if we want to allow it in combat
                />;

            default:
                return <div>Unknown Screen</div>;
        }
    };

    return (
        <div className="app-container w-screen h-screen bg-gray-900 text-white overflow-hidden">
            {/* The main screen is rendered here */}
            {renderScreen()}

            {/* --- 4. ADD OVERLAY RENDER LOGIC --- */}
            {/* If showCharacterSheet is true AND we have a character, render the overlay */}
            {showCharacterSheet && activeCharacter && (
                // This div is the semi-transparent backdrop
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
