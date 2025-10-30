import React, { useState } from 'react';
import { Sword, Shield, Heart, Zap, Eye, Brain, FileMusic as Muscle, Users, Dice6, Backpack, Map, Settings, Crown, Flame, Scroll, TreePine, Rabbit, Bird, Turtle, Bug, Leaf, Fish, Ear, Skull, DoorClosed as Nose, Hand, Feather, TreeDeciduous, Waves, User, CircleDot, Hexagon, Footprints, Anchor, Cat, Scale, Wheat, Sparkles, Star, Dumbbell, Activity, Plus, Target, Gauge, Move, Zap as Lightning, Mountain, Lightbulb, Compass, Smile, Focus, Swords, ShieldCheck, Battery, HeartPulse, Crosshair, Navigation, Frown, Wind, Timer, Shuffle, UserCheck, Zap as Psychic, Swords as Attack, Shield as Defense, Gauge as Stamina, Heart as HealthPoints, Target as FocusIcon, Move as Movement, Frown as Fatigue } from 'lucide-react';

interface CharacterStats {
  health: number;
  maxHealth: number;
  mana: number;
  maxMana: number;
  strength: number;
  dexterity: number;
  intelligence: number;
  wisdom: number;
  constitution: number;
  charisma: number;
  level: number;
  experience: number;
  gold: number;
}

interface InventoryItem {
  id: string;
  name: string;
  type: 'weapon' | 'armor' | 'potion' | 'misc';
  description: string;
  quantity: number;
}

function App() {
  const [activeTab, setActiveTab] = useState<'character' | 'inventory' | 'dice' | 'map' | 'categories'>('character');
  const [diceResult, setDiceResult] = useState<number | null>(null);
  const [isRolling, setIsRolling] = useState(false);

  const character: CharacterStats = {
    health: 85,
    maxHealth: 100,
    mana: 42,
    maxMana: 60,
    strength: 16,
    dexterity: 14,
    intelligence: 12,
    wisdom: 15,
    constitution: 18,
    charisma: 10,
    level: 7,
    experience: 2850,
    gold: 347
  };

  const inventory: InventoryItem[] = [
    { id: '1', name: 'Flamebrand Sword', type: 'weapon', description: 'A sword wreathed in eternal flames', quantity: 1 },
    { id: '2', name: 'Dragon Scale Mail', type: 'armor', description: 'Armor crafted from ancient dragon scales', quantity: 1 },
    { id: '3', name: 'Health Potion', type: 'potion', description: 'Restores 50 HP when consumed', quantity: 3 },
    { id: '4', name: 'Ancient Tome', type: 'misc', description: 'A mysterious book filled with arcane knowledge', quantity: 1 },
    { id: '5', name: 'Lockpicks', type: 'misc', description: 'Masterwork thieves\' tools', quantity: 5 },
  ];

  const rollDice = (sides: number) => {
    setIsRolling(true);
    setDiceResult(null);
    
    setTimeout(() => {
      const result = Math.floor(Math.random() * sides) + 1;
      setDiceResult(result);
      setIsRolling(false);
    }, 1000);
  };

  const StatBar = ({ current, max, color, icon: Icon }: { current: number; max: number; color: string; icon: React.ElementType }) => (
    <div className="flex items-center gap-3 mb-3">
      <Icon className="w-5 h-5 text-amber-400" />
      <div className="flex-1">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-stone-300">{current}/{max}</span>
          <span className="text-stone-400">{Math.round((current/max) * 100)}%</span>
        </div>
        <div className="h-3 bg-stone-800 rounded-full overflow-hidden border border-stone-700">
          <div 
            className={`h-full transition-all duration-500 ${color} shadow-glow`}
            style={{ width: `${(current/max) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );

  const StoneButton = ({ 
    children, 
    active, 
    onClick, 
    className = '' 
  }: { 
    children: React.ReactNode; 
    active?: boolean; 
    onClick?: () => void;
    className?: string;
  }) => (
    <button 
      onClick={onClick}
      className={`
        stone-button px-6 py-3 rounded-lg font-medieval text-sm tracking-wider transition-all duration-200
        ${active ? 'active' : ''}
        ${className}
      `}
    >
      {children}
    </button>
  );

  return (
    <div className="min-h-screen bg-dungeon text-stone-100 font-sans">
      {/* Background texture overlay */}
      <div className="fixed inset-0 opacity-10 pointer-events-none bg-noise" />
      
      {/* Header */}
      <header className="border-b border-stone-800 bg-stone-900/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Crown className="w-8 h-8 text-amber-400 glow-icon" />
              <h1 className="text-2xl font-bold text-amber-400 glow-text font-medieval tracking-wider">
                SHADOWFALL CHRONICLES
              </h1>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-stone-400">Character</div>
                <div className="font-bold text-amber-300 glow-text">Thorin Ironforge</div>
              </div>
              <Settings className="w-6 h-6 text-stone-400 hover:text-amber-400 transition-colors cursor-pointer" />
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="border-b border-stone-800 bg-stone-900/30">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex gap-4">
            <StoneButton 
              active={activeTab === 'character'} 
              onClick={() => setActiveTab('character')}
            >
              <Users className="w-4 h-4 inline mr-2" />
              CHARACTER
            </StoneButton>
            <StoneButton 
              active={activeTab === 'inventory'} 
              onClick={() => setActiveTab('inventory')}
            >
              <Backpack className="w-4 h-4 inline mr-2" />
              INVENTORY
            </StoneButton>
            <StoneButton 
              active={activeTab === 'dice'} 
              onClick={() => setActiveTab('dice')}
            >
              <Dice6 className="w-4 h-4 inline mr-2" />
              DICE
            </StoneButton>
            <StoneButton 
              active={activeTab === 'map'} 
              onClick={() => setActiveTab('map')}
            >
              <Map className="w-4 h-4 inline mr-2" />
              QUEST
            </StoneButton>
            <StoneButton 
              active={activeTab === 'categories'} 
              onClick={() => setActiveTab('categories')}
            >
              <TreePine className="w-4 h-4 inline mr-2" />
              CATEGORIES
            </StoneButton>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {activeTab === 'character' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Character Portrait & Info */}
            <div className="stone-panel p-6">
              <div className="text-center mb-6">
                <div className="w-24 h-24 mx-auto mb-4 bg-gradient-to-b from-amber-600 to-amber-800 rounded-full flex items-center justify-center border-4 border-amber-400 glow-border">
                  <Crown className="w-12 h-12 text-amber-100" />
                </div>
                <h2 className="text-xl font-bold text-amber-300 glow-text font-medieval">Thorin Ironforge</h2>
                <p className="text-stone-400">Dwarven Paladin</p>
                <div className="flex justify-center gap-4 mt-2 text-sm">
                  <span className="text-amber-400">Level {character.level}</span>
                  <span className="text-stone-400">•</span>
                  <span className="text-green-400">{character.gold} Gold</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <StatBar current={character.health} max={character.maxHealth} color="bg-red-500" icon={Heart} />
                <StatBar current={character.mana} max={character.maxMana} color="bg-blue-500" icon={Zap} />
              </div>
              
              <div className="mt-6 pt-4 border-t border-stone-700">
                <div className="text-sm text-stone-400 mb-2">Experience</div>
                <div className="h-2 bg-stone-800 rounded-full overflow-hidden border border-stone-700">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-600 to-purple-400 glow-purple"
                    style={{ width: '75%' }}
                  />
                </div>
                <div className="text-xs text-stone-400 mt-1">{character.experience}/3000 XP</div>
              </div>
            </div>

            {/* Attributes */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">ATTRIBUTES</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="stat-item">
                  <Muscle className="w-5 h-5 text-red-400 mb-1" />
                  <div className="text-sm text-stone-400">Strength</div>
                  <div className="text-xl font-bold text-red-300 glow-stat">{character.strength}</div>
                </div>
                <div className="stat-item">
                  <Eye className="w-5 h-5 text-green-400 mb-1" />
                  <div className="text-sm text-stone-400">Dexterity</div>
                  <div className="text-xl font-bold text-green-300 glow-stat">{character.dexterity}</div>
                </div>
                <div className="stat-item">
                  <Brain className="w-5 h-5 text-blue-400 mb-1" />
                  <div className="text-sm text-stone-400">Intelligence</div>
                  <div className="text-xl font-bold text-blue-300 glow-stat">{character.intelligence}</div>
                </div>
                <div className="stat-item">
                  <Scroll className="w-5 h-5 text-purple-400 mb-1" />
                  <div className="text-sm text-stone-400">Wisdom</div>
                  <div className="text-xl font-bold text-purple-300 glow-stat">{character.wisdom}</div>
                </div>
                <div className="stat-item">
                  <Shield className="w-5 h-5 text-yellow-400 mb-1" />
                  <div className="text-sm text-stone-400">Constitution</div>
                  <div className="text-xl font-bold text-yellow-300 glow-stat">{character.constitution}</div>
                </div>
                <div className="stat-item">
                  <Flame className="w-5 h-5 text-orange-400 mb-1" />
                  <div className="text-sm text-stone-400">Charisma</div>
                  <div className="text-xl font-bold text-orange-300 glow-stat">{character.charisma}</div>
                </div>
              </div>
            </div>

            {/* Combat Stats */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">COMBAT</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-stone-800/50 rounded border border-stone-700">
                  <div className="flex items-center gap-2">
                    <Sword className="w-4 h-4 text-red-400" />
                    <span className="text-sm text-stone-300">Attack Bonus</span>
                  </div>
                  <span className="font-bold text-red-300 glow-stat">+8</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-stone-800/50 rounded border border-stone-700">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-blue-400" />
                    <span className="text-sm text-stone-300">Armor Class</span>
                  </div>
                  <span className="font-bold text-blue-300 glow-stat">18</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-stone-800/50 rounded border border-stone-700">
                  <div className="flex items-center gap-2">
                    <Eye className="w-4 h-4 text-green-400" />
                    <span className="text-sm text-stone-300">Initiative</span>
                  </div>
                  <span className="font-bold text-green-300 glow-stat">+2</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inventory' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">INVENTORY</h3>
              <div className="space-y-3">
                {inventory.map(item => (
                  <div key={item.id} className="inventory-item p-4 bg-stone-800/30 rounded border border-stone-700 hover:border-amber-600 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center gap-3">
                        {item.type === 'weapon' && <Sword className="w-5 h-5 text-red-400" />}
                        {item.type === 'armor' && <Shield className="w-5 h-5 text-blue-400" />}
                        {item.type === 'potion' && <Heart className="w-5 h-5 text-green-400" />}
                        {item.type === 'misc' && <Scroll className="w-5 h-5 text-purple-400" />}
                        <h4 className="font-semibold text-stone-200">{item.name}</h4>
                      </div>
                      <span className="text-xs bg-amber-600/20 text-amber-300 px-2 py-1 rounded border border-amber-600/30">
                        x{item.quantity}
                      </span>
                    </div>
                    <p className="text-sm text-stone-400">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">EQUIPPED</h3>
              <div className="space-y-3">
                <div className="equipment-slot p-4 bg-stone-800/50 rounded border-2 border-dashed border-amber-600/30">
                  <div className="flex items-center gap-3 text-amber-400">
                    <Sword className="w-5 h-5" />
                    <span className="font-semibold">Flamebrand Sword</span>
                  </div>
                  <p className="text-sm text-stone-400 mt-1">+2 Fire Damage</p>
                </div>
                <div className="equipment-slot p-4 bg-stone-800/50 rounded border-2 border-dashed border-amber-600/30">
                  <div className="flex items-center gap-3 text-amber-400">
                    <Shield className="w-5 h-5" />
                    <span className="font-semibold">Dragon Scale Mail</span>
                  </div>
                  <p className="text-sm text-stone-400 mt-1">AC 18, Fire Resistance</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'dice' && (
          <div className="max-w-2xl mx-auto">
            <div className="stone-panel p-8 text-center">
              <h3 className="text-2xl font-bold text-amber-300 glow-text mb-6 font-medieval">DICE ROLLER</h3>
              
              <div className="mb-8">
                {isRolling ? (
                  <div className="dice-rolling w-24 h-24 mx-auto mb-4 bg-gradient-to-b from-amber-600 to-amber-800 rounded-lg flex items-center justify-center border-4 border-amber-400 glow-border">
                    <Dice6 className="w-12 h-12 text-amber-100 animate-spin" />
                  </div>
                ) : diceResult ? (
                  <div className="dice-result w-24 h-24 mx-auto mb-4 bg-gradient-to-b from-amber-600 to-amber-800 rounded-lg flex items-center justify-center border-4 border-amber-400 glow-border">
                    <span className="text-3xl font-bold text-amber-100">{diceResult}</span>
                  </div>
                ) : (
                  <div className="w-24 h-24 mx-auto mb-4 bg-stone-800 rounded-lg flex items-center justify-center border-2 border-stone-600">
                    <Dice6 className="w-12 h-12 text-stone-400" />
                  </div>
                )}
                
                {diceResult && !isRolling && (
                  <p className="text-amber-300 glow-text font-bold">You rolled: {diceResult}</p>
                )}
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StoneButton onClick={() => rollDice(4)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D4
                </StoneButton>
                <StoneButton onClick={() => rollDice(6)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D6
                </StoneButton>
                <StoneButton onClick={() => rollDice(8)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D8
                </StoneButton>
                <StoneButton onClick={() => rollDice(10)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D10
                </StoneButton>
                <StoneButton onClick={() => rollDice(12)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D12
                </StoneButton>
                <StoneButton onClick={() => rollDice(20)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D20
                </StoneButton>
                <StoneButton onClick={() => rollDice(100)} className="py-4">
                  <Dice6 className="w-5 h-5 mx-auto mb-1" />
                  D100
                </StoneButton>
                <StoneButton onClick={() => setDiceResult(null)} className="py-4">
                  <span className="text-xs">CLEAR</span>
                </StoneButton>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'map' && (
          <div className="stone-panel p-6">
            <h3 className="text-2xl font-bold text-amber-300 glow-text mb-6 font-medieval text-center">CURRENT QUEST</h3>
            <div className="max-w-2xl mx-auto">
              <div className="quest-card p-6 bg-stone-800/50 rounded border border-amber-600/30 mb-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gradient-to-b from-amber-600 to-amber-800 rounded-lg flex items-center justify-center border-2 border-amber-400">
                    <Crown className="w-6 h-6 text-amber-100" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-xl font-bold text-amber-300 glow-text mb-2">The Lost Crown of Athros</h4>
                    <p className="text-stone-300 leading-relaxed mb-4">
                      Deep within the Whispering Caverns, an ancient crown lies hidden. Legend speaks of its power to
                      command the very stones themselves. But beware - the caverns are filled with dangers both old and new.
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <span className="text-xs bg-green-600/20 text-green-300 px-2 py-1 rounded border border-green-600/30">
                        Active
                      </span>
                      <span className="text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded border border-purple-600/30">
                        Legendary
                      </span>
                      <span className="text-xs bg-amber-600/20 text-amber-300 px-2 py-1 rounded border border-amber-600/30">
                        Reward: 1000 XP
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <StoneButton className="p-4">
                  <Map className="w-5 h-5 mx-auto mb-2" />
                  VIEW MAP
                </StoneButton>
                <StoneButton className="p-4">
                  <Users className="w-5 h-5 mx-auto mb-2" />
                  PARTY STATUS
                </StoneButton>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'categories' && (
          <div className="space-y-8">
            {/* Kingdoms */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">KINGDOMS</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Users className="w-4 h-4 mx-auto mb-1 text-orange-400" />
                  MAMMAL
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Bird className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  AVIAN
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Turtle className="w-4 h-4 mx-auto mb-1 text-green-400" />
                  REPTILE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Bug className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                  INSECT
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Leaf className="w-4 h-4 mx-auto mb-1 text-green-500" />
                  PLANT
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Fish className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
                  AQUATIC
                </StoneButton>
              </div>
            </div>

            {/* Anatomy */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">ANATOMY</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Eye className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  EYES
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Ear className="w-4 h-4 mx-auto mb-1 text-purple-400" />
                  EARS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Skull className="w-4 h-4 mx-auto mb-1 text-red-400" />
                  JAW
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Nose className="w-4 h-4 mx-auto mb-1 text-pink-400" />
                  NOSE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Hand className="w-4 h-4 mx-auto mb-1 text-orange-400" />
                  ARMS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Feather className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
                  WINGS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <TreeDeciduous className="w-4 h-4 mx-auto mb-1 text-green-400" />
                  BRANCHES
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Fish className="w-4 h-4 mx-auto mb-1 text-blue-500" />
                  FINS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <User className="w-4 h-4 mx-auto mb-1 text-stone-400" />
                  BODY
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <CircleDot className="w-4 h-4 mx-auto mb-1 text-amber-400" />
                  TRUNK
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Hexagon className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                  THORAX
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Footprints className="w-4 h-4 mx-auto mb-1 text-brown-400" />
                  LEGS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Anchor className="w-4 h-4 mx-auto mb-1 text-green-600" />
                  ROOTS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Cat className="w-4 h-4 mx-auto mb-1 text-orange-500" />
                  TAIL
                </StoneButton>
              </div>
            </div>

            {/* Features */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">FEATURES</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Rabbit className="w-4 h-4 mx-auto mb-1 text-gray-400" />
                  FUR
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Scale className="w-4 h-4 mx-auto mb-1 text-green-400" />
                  SCALES
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <TreePine className="w-4 h-4 mx-auto mb-1 text-amber-600" />
                  BARK
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Shield className="w-4 h-4 mx-auto mb-1 text-stone-400" />
                  CARAPACE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Feather className="w-4 h-4 mx-auto mb-1 text-blue-300" />
                  FEATHERS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Bird className="w-4 h-4 mx-auto mb-1 text-yellow-500" />
                  BEAK
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Bug className="w-4 h-4 mx-auto mb-1 text-red-400" />
                  MANDIBLES
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Leaf className="w-4 h-4 mx-auto mb-1 text-green-500" />
                  FOLIAGE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Waves className="w-4 h-4 mx-auto mb-1 text-purple-400" />
                  ANTENNAE
                </StoneButton>
              </div>
            </div>

            {/* Background */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">BACKGROUND</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Heart className="w-4 h-4 mx-auto mb-1 text-red-400" />
                  DEVOTION
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Compass className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  ORIGIN
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Users className="w-4 h-4 mx-auto mb-1 text-green-400" />
                  REARING
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Wheat className="w-4 h-4 mx-auto mb-1 text-amber-400" />
                  PROFESSION
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Star className="w-4 h-4 mx-auto mb-1 text-purple-400" />
                  STAR SIGN
                </StoneButton>
              </div>
            </div>

            {/* Attributes */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">ATTRIBUTES</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Dumbbell className="w-4 h-4 mx-auto mb-1 text-red-400" />
                  MIGHT
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Activity className="w-4 h-4 mx-auto mb-1 text-orange-400" />
                  ENDURANCE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Plus className="w-4 h-4 mx-auto mb-1 text-green-400" />
                  VITALITY
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Shield className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  CONSTITUTION
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Target className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                  FINESSE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Gauge className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
                  REFLEXES
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Brain className="w-4 h-4 mx-auto mb-1 text-blue-500" />
                  KNOWLEDGE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Lightbulb className="w-4 h-4 mx-auto mb-1 text-purple-400" />
                  LOGIC
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Mountain className="w-4 h-4 mx-auto mb-1 text-green-600" />
                  INSTINCT
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Eye className="w-4 h-4 mx-auto mb-1 text-amber-500" />
                  PERCEPTION
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Smile className="w-4 h-4 mx-auto mb-1 text-pink-400" />
                  CHARM
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Focus className="w-4 h-4 mx-auto mb-1 text-indigo-400" />
                  WILLPOWER
                </StoneButton>
              </div>
            </div>

            {/* Powers */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">POWERS</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Lightning className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                  FORCE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <ShieldCheck className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  BASTION
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Wind className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
                  KI
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Leaf className="w-4 h-4 mx-auto mb-1 text-green-500" />
                  BIOMANCY
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Eye className="w-4 h-4 mx-auto mb-1 text-purple-400" />
                  CUNNING
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Feather className="w-4 h-4 mx-auto mb-1 text-white" />
                  GRACE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Sparkles className="w-4 h-4 mx-auto mb-1 text-purple-500" />
                  ARCANE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Heart className="w-4 h-4 mx-auto mb-1 text-blue-300" />
                  SPIRIT
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Timer className="w-4 h-4 mx-auto mb-1 text-amber-400" />
                  TIME
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Shuffle className="w-4 h-4 mx-auto mb-1 text-red-500" />
                  CHAOS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <UserCheck className="w-4 h-4 mx-auto mb-1 text-gold-400" />
                  LEADERSHIP
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Psychic className="w-4 h-4 mx-auto mb-1 text-pink-500" />
                  PSYCHIC
                </StoneButton>
              </div>
            </div>

            {/* Combat */}
            <div className="stone-panel p-6">
              <h3 className="text-lg font-bold text-amber-300 glow-text mb-4 font-medieval">COMBAT</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                <StoneButton className="p-3 text-xs">
                  <Attack className="w-4 h-4 mx-auto mb-1 text-red-400" />
                  ATTACK
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Defense className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                  DEFENSE
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Stamina className="w-4 h-4 mx-auto mb-1 text-green-400" />
                  STAMINA
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <HealthPoints className="w-4 h-4 mx-auto mb-1 text-red-500" />
                  HEALTH
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <FocusIcon className="w-4 h-4 mx-auto mb-1 text-purple-400" />
                  FOCUS
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Movement className="w-4 h-4 mx-auto mb-1 text-cyan-400" />
                  MOVEMENT
                </StoneButton>
                <StoneButton className="p-3 text-xs">
                  <Fatigue className="w-4 h-4 mx-auto mb-1 text-orange-400" />
                  FATIGUE
                </StoneButton>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;