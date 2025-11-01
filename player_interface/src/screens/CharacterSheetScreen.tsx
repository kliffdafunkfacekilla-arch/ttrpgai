// src/screens/CharacterSheetScreen.tsx
import React from "react";
import {
  type CharacterContextResponse,
  type InventoryItem,
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
const ListBlock: React.FC<{
  title: string;
  items: (string | InventoryItem)[] | undefined;
}> = ({ title, items }) => (
  <div className="mb-4">
    <h3 className="text-xl font-bold border-b border-gray-600 mb-2">{title}</h3>
    {!items || items.length === 0 ? (
      <p className="text-gray-500 italic">None</p>
    ) : (
      <ul className="list-disc list-inside">
        {items.map((item, index) => (
          <li key={index} className="capitalize">
            {typeof item === "string" ? item : item.name}
          </li>
        ))}
      </ul>
    )}
  </div>
);

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
  } = character;

  // Create a display-friendly object for combat stats
  const combat_stats = {
    HP: `${current_hp} / ${max_hp}`,
    ...Object.fromEntries(
      Object.entries(resource_pools).map(([key, value]) => [
        key,
        `${value.current} / ${value.max}`,
      ]),
    ),
  };

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
          </div>
          <div>
            <ListBlock title="Inventory" items={Object.values(inventory)} />
            <ListBlock title="Abilities" items={abilities} />
            <StatBlock title="Skills" data={skills} />
          </div>
        </div>
        {/* We can add sections for equipped items, talents, etc. later */}
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
