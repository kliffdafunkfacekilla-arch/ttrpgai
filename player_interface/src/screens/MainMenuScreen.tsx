// src/screens/MainMenuScreen.tsx
import React from 'react';

// Define the props the component expects
interface MainMenuScreenProps {
    onStartNewGame: () => void; // Reverted to this
    onLoadGame: () => void;
}

const MainMenuScreen: React.FC<MainMenuScreenProps> = ({ onStartNewGame, onLoadGame }) => {
    return (
        <div className="main-menu flex flex-col items-center justify-center h-full bg-gradient-to-b from-gray-800 to-black p-8">
            <h1 className="text-6xl font-bold mb-12 text-red-500 font-serif shadow-lg">
                AI TTRPG
            </h1>
            <div className="space-y-4 w-full max-w-xs">
                <button
                    onClick={onStartNewGame} // Reverted to this
                    className="w-full bg-red-700 hover:bg-red-600 text-white font-bold py-3 px-6 rounded-lg shadow-md transition duration-150 ease-in-out transform hover:scale-105"
                >
                    New Game
                </button>
                <button
                    onClick={onLoadGame}
                    className="w-full bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg shadow-md transition duration-150 ease-in-out transform hover:scale-105"
                >
                    Load Game
                </button>
            </div>
            <p className="absolute bottom-4 text-xs text-gray-500">
                Version 0.0.1
            </p>
        </div>
    );
};

export default MainMenuScreen;
