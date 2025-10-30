// src/screens/MainMenuScreen.tsx
import React from 'react';

// Define the props the component expects (functions passed down from App)
interface MainMenuScreenProps {
    onStartNewGame: () => void;
    onLoadGame: () => void;
}

const MainMenuScreen: React.FC<MainMenuScreenProps> = ({ onStartNewGame, onLoadGame }) => {
    return (
        <div className="main-menu flex flex-col items-center justify-center h-full bg-gradient-to-b from-gray-800 to-black p-8">
            {/* Use Tailwind classes for styling */}
            <h1 className="text-6xl font-bold mb-12 text-red-500 font-serif shadow-lg">
                AI TTRPG {/* TODO: Replace with actual game title */}
            </h1>

            <div className="space-y-4 w-full max-w-xs">
                {/* Basic button styling with Tailwind */}
                <button
                    onClick={onStartNewGame}
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

                {/* Add Quit button later if needed, depends if it's browser or packaged app */}
                {/* <button className="w-full bg-gray-700 hover:bg-gray-600 text-gray-300 font-bold py-3 px-6 rounded-lg shadow-md transition duration-150 ease-in-out">
                    Quit
                </button> */}
            </div>

            <p className="absolute bottom-4 text-xs text-gray-500">
                Version 0.0.1 {/* Or fetch dynamically */}
            </p>
        </div>
    );
};

export default MainMenuScreen;