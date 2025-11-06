// src/screens/CharacterSheetScreen.tsx
import React from "react";
import {
type CharacterContextResponse,
type Injury,
} from "../types/apiTypes";

interface CharacterSheetScreenProps {
character: CharacterContextResponse;
onClose: () => void;
}

// Helper component for a stat block
const StatBlock: React.FC<{
title: string;
data: Record<string, unknown>;
}> = ({ title, data }) => (
<div className="mb-4">
<h3 className="text-xl font-bold border-b border-gray-600 mb-2">{title}</h3>
<div className="grid grid-cols-2 gap-x-4 gap-y-1">
{Object.entries(data).map(([key, value]) => (
<div key={key} className="flex justify-between">
<span className="text-gray-400 capitalize">
{key.replace(/_/g, " ")}:
</span>
<span className="font-medium">{String(value)}</span>
</div>
))}
</div>
</div>
);

// Helper component for a list block
// --- MODIFICATION: Adjusted to handle new inventory/equipment/injury types ---
const ListBlock: React.FC<{
title: string;
items: (string | { id: string; quantity: number } | { slot: string, item: string } | Injury)[] | undefined;
}> = ({ title, items }) => (
<div className="mb-4">
<h3 className="text-xl font-bold border-b border-gray-600 mb-2">{title}</h3>
{!items || items.length === 0 ? (
<p className="text-gray-500 italic">None</p>
) : (
<ul className="list-disc list-inside">
{items.map((item, index) => {
let content = "";
if (typeof item === "string") {
content = item; // For Abilities, Talents, Status Effects
} else if ("quantity" in item) {
content = `${item.id} (x${item.quantity})`; // For Inventory
} else if ("slot" in item) {
content = `${item.slot}: ${item.item}`; // For Equipment
} else if ("description" in item) {
content = `${item.location} (${item.severity}): ${item.description}`; // For Injuries
}
return (
<li key={index} className="capitalize">
{content}
</li>
);
})}
</ul>
)}
</div>
);
// --- END MODIFICATION ---

const CharacterSheetScreen: React.FC<CharacterSheetScreenProps> = ({
character,
onClose,
}) => {
const {
name,
stats,
skills,
inventory,
abilities,
max_hp,
current_hp,
resource_pools,
// --- ADD NEW FIELDS ---
talents,
equipment,
status_effects,
injuries,
// --- END ADD ---
} = character;

// --- MODIFICATION: Create display objects from flat structure ---
const combat_stats = {
HP: `${current_hp} / ${max_hp}`,
...Object.fromEntries(
Object.entries(resource_pools).map(([key, value]) => [
key,
`${value.current} / ${value.max}`,
]),
),
};

// Convert simplified inventory {id: qty} to list for display
const inventory_list = Object.entries(inventory).map(([id, quantity]) => ({
id: id,
quantity: quantity,
}));

// --- ADDED: Convert equipment to list for display ---
const equipment_list = Object.entries(equipment).map(([slot, item]) => ({
slot: slot,
item: item,
}));

// Convert skills {id: {rank: X, sre: Y}} to {id: "Rank X"}
const skills_display = Object.fromEntries(
Object.entries(skills).map(([key, value]) => [
key,
`Rank ${value.rank}`
])
);
// --- END MODIFICATION ---

return (
// This is the overlay panel
<div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] max-w-[90%] h-[700px] max-h-[90%] bg-gray-900 border-4 border-gray-700 rounded-lg z-50 flex flex-col">
<header className="flex justify-between items-center p-4 border-b-2 border-gray-700">
<h2 className="text-3xl font-bold font-serif">
{name}'s Character Sheet
</h2>
<button
onClick={onClose}
className="text-2xl font-bold text-gray-400 hover:text-white"
>
&times; {/* This is a "X" close icon */}
</button>
</header>

<main className="p-6 overflow-y-auto flex-grow">
{/* Main Stats Grid */}
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
<div>
<StatBlock title="Core Stats" data={stats} />
<StatBlock title="Combat Stats" data={combat_stats} />
{/* --- ADDED TALENTS, STATUS, INJURIES --- */}
<ListBlock title="Talents" items={talents} />
<ListBlock title="Status Effects" items={status_effects} />
<ListBlock title="Injuries" items={injuries} />
</div>
<div>
{/* --- MODIFICATION: Use new list variables --- */}
<ListBlock title="Inventory" items={inventory_list} />
<ListBlock title="Equipment" items={equipment_list} />
<ListBlock title="Abilities" items={abilities} />
<StatBlock title="Skills" data={skills_display} />
{/* --- END MODIFICATION --- */}
</div>
</div>
</main>

<footer className="p-4 border-t-2 border-gray-700 text-center">
<button
onClick={onClose}
className="bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-6 rounded-lg"
>
Close
</button>
</footer>
</div>
);
};

export default CharacterSheetScreen;