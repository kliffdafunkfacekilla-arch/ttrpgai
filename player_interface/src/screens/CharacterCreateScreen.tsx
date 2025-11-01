// src/screens/CharacterCreateScreen.tsx
import React, { useState } from 'react';
import { createCharacter } from '../api/apiClient';
import { type CharacterContextResponse } from '../types/apiTypes';

// Define the props passed down from App.tsx
interface CharacterCreateScreenProps {
onCharacterCreated: (character: CharacterContextResponse) => void;
onBack: () => void;
}

const CharacterCreateScreen: React.FC<CharacterCreateScreenProps> = ({ onCharacterCreated, onBack }) => {
const [name, setName] = useState("");
const [isCreating, setIsCreating] = useState(false);
const [error, setError] = useState<string | null>(null);

const handleSubmit = async (e: React.FormEvent) => {
e.preventDefault(); // Prevent form from reloading page
if (!name.trim()) {
setError("Name cannot be empty.");
return;
}

try {
setIsCreating(true);
setError(null);
const newCharacter = await createCharacter(name);
onCharacterCreated(newCharacter); // Pass the new character up to App.tsx
} catch (err: any) {
console.error("Failed to create character:", err);
setError(err.message || "Could not create character.");
setIsCreating(false);
}
// No finally block, as we navigate away on success
};

return (
<div className="main-menu flex flex-col items-center justify-center h-full bg-gradient-to-b from-gray-800 to-black p-8">
<h1 className="text-4xl font-bold mb-12 text-white font-serif">
Create New Character
</h1>

<form onSubmit={handleSubmit} className="space-y-4 w-full max-w-xs">
<div>
<label htmlFor="charName" className="block text-sm font-medium text-gray-300 mb-2">
Character Name:
</label>
<input
id="charName"
type="text"
value={name}
onChange={(e) => setName(e.target.value)}
className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white"
placeholder="e.g., Kaelen"
/>
</div>

{error && <p className="text-red-500 text-sm">{error}</p>}

<button
type="submit"
disabled={isCreating || !name}
className="w-full bg-green-700 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-lg shadow-md disabled:opacity-50"
>
{isCreating ? "Creating..." : "Create and Begin"}
</button>
</form>

<button
onClick={onBack}
disabled={isCreating}
className="w-full max-w-xs mt-8 bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg shadow-md disabled:opacity-50"
>
Back to Main Menu
</button>
</div>
);
};

export default CharacterCreateScreen;
