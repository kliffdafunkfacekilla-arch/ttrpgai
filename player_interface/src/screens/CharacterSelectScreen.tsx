// src/screens/CharacterSelectScreen.tsx
import React, { useState, useEffect } from 'react';
import { getCharacterList } from '../api/apiClient';
import { type CharacterContextResponse } from '../types/apiTypes';

// Define the props passed down from App.tsx
interface CharacterSelectScreenProps {
onCharacterSelected: (character: CharacterContextResponse) => void;
onBack: () => void;
}

const CharacterSelectScreen: React.FC<CharacterSelectScreenProps> = ({ onCharacterSelected, onBack }) => {
const [characters, setCharacters] = useState<CharacterContextResponse[]>([]);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

// Fetch characters on component mount
useEffect(() => {
const fetchCharacters = async () => {
try {
setIsLoading(true);
setError(null);
const charList = await getCharacterList();
setCharacters(charList);
} catch (err: any) {
console.error("Failed to fetch character list:", err);
setError(err.message || "Could not load characters.");
} finally {
setIsLoading(false);
}
};
fetchCharacters();
}, []);

const renderContent = () => {
if (isLoading) {
return <p>Loading characters...</p>;
}

if (error) {
return <p className="text-red-500">Error: {error}</p>;
}

if (characters.length === 0) {
return <p>No characters found. Go back and create a new one.</p>;
}

// Render a button for each character
return (
<div className="space-y-4 w-full max-w-xs">
{characters.map((char) => (
<button
key={char.id}
onClick={() => onCharacterSelected(char)}
className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg shadow-md transition duration-150"
>
{char.name} (ID: {char.id})
</button>
))}
</div>
);
};

return (
<div className="main-menu flex flex-col items-center justify-center h-full bg-gradient-to-b from-gray-800 to-black p-8">
<h1 className="text-4xl font-bold mb-12 text-white font-serif">
Select Your Character
</h1>

{renderContent()}

<button
onClick={onBack}
className="w-full max-w-xs mt-8 bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg shadow-md"
>
Back to Main Menu
</button>
</div>
);
};

export default CharacterSelectScreen;
