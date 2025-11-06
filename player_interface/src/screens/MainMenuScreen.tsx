
// src/screens/MainMenuScreen.tsx
import React from "react";
import { Crown } from "lucide-react";

// Define the props the component expects
interface MainMenuScreenProps {
  onStartNewGame: () => void;
  onQuickStart: () => void;
  isLoading: boolean;
}

const MainMenuScreen: React.FC<MainMenuScreenProps> = ({
  onStartNewGame,
  onQuickStart,
  isLoading,
}) => {
  return (
    <div className="main-menu flex flex-col items-center justify-center h-full p-8">
      <div className="flex items-center gap-3 mb-12">
        <Crown className="w-16 h-16 text-amber-400 glow-icon" />
        <h1 className="text-6xl font-bold text-amber-400 glow-text font-medieval tracking-wider">
          SHADOWFALL CHRONICLES
        </h1>
      </div>
      <div className="space-y-4 w-full max-w-xs">
        <button
          onClick={onStartNewGame}
          className="stone-button w-full"
        >
          New Game
        </button>
        <button
            onClick={onQuickStart}
            className="px-6 py-3 bg-yellow-500 text-gray-900 rounded-lg shadow-md hover:bg-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-300 focus:ring-opacity-50 transition-colors disabled:opacity-50"
            disabled={isLoading}
        >
            {isLoading ? 'Loading...' : 'Quick Start (Test)'}
        </button>
      </div>
      <p className="absolute bottom-4 text-xs text-stone-500">Version 0.0.1</p>
    </div>
  );
};

export default MainMenuScreen;
