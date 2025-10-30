// src/App.tsx
import React, { useState } from 'react'; // Import useState
import './App.css'; // We can use this for global styles if needed
import MainMenuScreen from './screens/MainMenuScreen'; // Import the MainMenu
import ExplorationScreen from './screens/ExplorationScreen'; // Import the ExplorationScreen
// import CombatScreen from './screens/CombatScreen';

// Define possible game states/screens
type GameScreen = 'MainMenu' | 'Exploration' | 'Combat' | 'CharacterSheet';

function App() {
    // State to track the current active screen
    const [currentScreen, setCurrentScreen] = useState<GameScreen>('MainMenu');

    // State to hold necessary game context (will grow)
    // For now, just placeholder, will be populated by API calls
    const [gameContext, setGameContext] = useState<any>(null); // Replace 'any' later

    // Function to handle starting a new game (passed to MainMenu)
    const handleStartNewGame = () => {
        console.log("Starting New Game... Navigating to Exploration screen.");
        // For now, we'll just switch the screen.
        // API calls and context setting will be added later.
        setCurrentScreen('Exploration');
    };

    // Function to handle loading a game (placeholder)
    const handleLoadGame = () => {
        console.log("Loading Game...");
        // TODO: Implement load game logic
        alert("Load Game clicked (Not implemented)");
    };


    // Render the current screen based on state
    const renderScreen = () => {
        switch (currentScreen) {
            case 'MainMenu':
                return <MainMenuScreen onStartNewGame={handleStartNewGame} onLoadGame={handleLoadGame} />;
            case 'Exploration':
                // The ExplorationScreen handles its own data fetching for now.
                return <ExplorationScreen />;
            // case 'Combat':
            // return <CombatScreen context={gameContext} />;
            default:
                return <div>Unknown Screen</div>;
        }
    };

    return (
        <div className="app-container w-screen h-screen bg-gray-900 text-white overflow-hidden">
            {/* Basic container - Styling and layout will evolve */}
            {renderScreen()}
        </div>
    );
}

export default App;