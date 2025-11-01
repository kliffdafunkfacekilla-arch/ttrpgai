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
// --- ADD NEW SCREEN IMPORT ---
import CharacterCreationScreen from './screens/CharacterCreationScreen';
// --- REMOVE OLD SCREEN IMPORT ---
// import CharacterCreateScreen from './screens/CharacterCreateScreen';
import CharacterSheetScreen from './screens/CharacterSheetScreen';

// --- ADD 'CharacterCreate' TO TYPE ---
type GameScreen = 'MainMenu' | 'CharacterCreate' | 'CharacterSelect' | 'Exploration' | 'Combat' | 'CharacterSheet';

function App() {
    const [currentScreen, setCurrentScreen] = useState<GameScreen>('MainMenu');
    const [combatContext, setCombatContext] = useState<CombatEncounterResponse | null>(null);
    const [activeCharacter, setActiveCharacter] = useState<CharacterContextResponse | null>(null);
    const [showCharacterSheet, setShowCharacterSheet] = useState(false);

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

    // This handler is now called by CharacterCreationScreen
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
                    // --- PASS onStartNewGame ---
                    onStartNewGame={() => setCurrentScreen('CharacterCreate')}
                    onLoadGame={() => setCurrentScreen('CharacterSelect')}
                />;
            case 'CharacterSelect':
                return <CharacterSelectScreen
                    onCharacterSelected={handleCharacterSelected}
                    onBack={() => setCurrentScreen('MainMenu')}
                />;

            // --- ADD THIS CASE BLOCK ---
            case 'CharacterCreate':
                return <CharacterCreationScreen
                    onCharacterCreated={handleCharacterCreated}
                    onBack={() => setCurrentScreen('MainMenu')}
                />;

            // --- OLD 'CharacterCreate' case is removed ---

            case 'Exploration':
                if (!activeCharacter) {
                    console.error("In Exploration screen but no active character!");
                    handleExitToMenu();
                    return null;
                }
                return <ExplorationScreen
                    key={activeCharacter.id}
                    activeCharacter={activeCharacter}
                    onCombatStart={handleCombatStart}
                    onExitToMenu={handleExitToMenu}
                    onShowCharacterSheet={() => setShowCharacterSheet(true)}
                />;

            case 'Combat':
                if (!combatContext || !activeCharacter) {
                    console.error("In Combat screen but no combat or character context!");
                    handleExitToMenu();
                    return null;
                }
                return <CombatScreen
                    combatContext={combatContext}
                    activeCharacter={activeCharacter}
                    onCombatEnd={handleCombatEnd}
                />;

            default:
                return <div>Unknown Screen</div>;
        }
    };

    return (
        <div className="app-container w-screen h-screen bg-gray-900 text-white overflow-hidden">
            {/* The main screen is rendered here */}
            {renderScreen()}

            {/* Character Sheet Overlay logic is unchanged */}
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
