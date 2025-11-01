// src/screens/MainMenuScreen.tsx
import React from "react";
import { Crown } from "lucide-react";

// Define the props the component expects
interface MainMenuScreenProps {
  onStartNewGame: () => void;
  onLoadGame: () => void;
}

const MainMenuScreen: React.FC<MainMenuScreenProps> = ({
  onStartNewGame,
  onLoadGame,
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
          onClick={onLoadGame}
          className="stone-button w-full"
        >
          Load Game
        </button>
      </div>
      <p className="absolute bottom-4 text-xs text-stone-500">Version 0.0.1</p>
    </div>
  );
};

export default MainMenuScreen;
