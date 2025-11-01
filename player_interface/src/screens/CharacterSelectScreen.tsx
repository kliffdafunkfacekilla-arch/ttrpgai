// src/screens/CharacterSelectScreen.tsx
import React, { useState, useEffect } from "react";
// --- MODIFIED: Use fetchCharacters ---
import { fetchCharacters } from "../api/apiClient";
import { type CharacterContextResponse } from "../types/apiTypes";
import { Users } from "lucide-react";

// Define the props passed down from App.tsx
interface CharacterSelectScreenProps {
  onCharacterSelected: (character: CharacterContextResponse) => void;
  onBack: () => void;
}

const CharacterSelectScreen: React.FC<CharacterSelectScreenProps> = ({
  onCharacterSelected,
  onBack,
}) => {
  const [characters, setCharacters] = useState<CharacterContextResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch characters on component mount
  useEffect(() => {
    const loadCharacters = async () => {
      try {
        setIsLoading(true);
        setError(null);
        // --- MODIFIED: Use fetchCharacters ---
        const charList = await fetchCharacters();
        setCharacters(charList);
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "An unknown error occurred while fetching characters.";
        console.error("Failed to fetch character list:", err);
        setError(message);
      } finally {
        setIsLoading(false);
      }
    };
    loadCharacters();
  }, []);

  const renderContent = () => {
    if (isLoading) {
      return <p className="text-amber-300 glow-text">Loading characters...</p>;
    }

    if (error) {
      return <p className="text-red-400 glow-text">Error: {error}</p>;
    }

    if (characters.length === 0) {
      return (
        <p className="text-stone-400">
          No characters found. Go back and create a new one.
        </p>
      );
    }

    // Render a button for each character
    return (
      <div className="space-y-3 w-full max-w-md">
        {characters.map((char) => (
          <button
            key={char.id}
            onClick={() => onCharacterSelected(char)}
            className="stone-button w-full"
          >
            {char.name}
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="main-menu flex flex-col items-center justify-center h-full p-8">
      <div className="flex items-center gap-3 mb-12">
        <Users className="w-12 h-12 text-amber-400 glow-icon" />
        <h1 className="text-4xl font-bold text-amber-400 glow-text font-medieval tracking-wider">
          Select Your Character
        </h1>
      </div>

      {renderContent()}

      <button
        onClick={onBack}
        className="stone-button w-full max-w-xs mt-8"
      >
        Back to Main Menu
      </button>
    </div>
  );
};

export default CharacterSelectScreen;
