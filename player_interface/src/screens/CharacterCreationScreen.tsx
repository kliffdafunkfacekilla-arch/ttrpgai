// src/screens/CharacterCreationScreen.tsx
import React, { useState, useEffect, useMemo } from "react";
import {
  createCharacter,
  getKingdomFeatures,
  getOriginChoices,
  getChildhoodChoices,
  getComingOfAgeChoices,
  getTrainingChoices,
  getDevotionChoices,
  // getAbilityTalents, // <-- REMOVED this
  getAbilitySchools,
  getAllSkills,
  getEligibleTalents, // <-- ADDED this
} from "../api/apiClient";
import {
  type CharacterContextResponse,
  type KingdomFeaturesData,
  type TalentInfo,
  type KingdomFeatureChoice,
  type CharacterCreateRequest,
  type FeatureChoiceRequest,
  type FeatureMods,
  type BackgroundChoiceInfo,
} from "../types/apiTypes";

// --- Component Props ---
interface CharacterCreationScreenProps {
  onCharacterCreated: (character: CharacterContextResponse) => void;
  onBack: () => void;
}

// --- State Types ---
type CreationStep =
  | "kingdom"
  | "features"
  | "origin"
  | "childhood"
  | "comingOfAge"
  | "training"
  | "devotion"
  | "school"
  | "talent"
  | "name"
  | "review";

type LoadingState = {
  isLoading: boolean;
  error: string | null;
};

type RulesData = {
  kingdomFeatures: KingdomFeaturesData | null;
  originChoices: BackgroundChoiceInfo[];
  childhoodChoices: BackgroundChoiceInfo[];
  comingOfAgeChoices: BackgroundChoiceInfo[];
  trainingChoices: BackgroundChoiceInfo[];
  devotionChoices: BackgroundChoiceInfo[];
  abilityTalents: TalentInfo[]; // This will now be loaded dynamically
  abilitySchools: string[];
  all_skills: { [key: string]: { stat: string } };
  ability_school_stats: { [key: string]: string };
};

type Choices = {
  kingdom: string | null;
  featureChoices: FeatureChoiceRequest[];
  originChoice: string | null;
  childhoodChoice: string | null;
  comingOfAgeChoice: string | null;
  trainingChoice: string | null;
  devotionChoice: string | null;
  abilitySchool: string | null;
  abilityTalent: string | null;
  name: string;
};

// --- Constants ---
const KINGDOMS = ["Mammal", "Reptile", "Avian", "Aquatic", "Insect", "Plant"];
const FEATURE_IDS: string[] = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"];

const BASE_STATS: { [key: string]: number } = {
  Might: 8,
  Endurance: 8,
  Finesse: 8,
  Reflexes: 8,
  Vitality: 8,
  Fortitude: 8,
  Knowledge: 8,
  Logic: 8,
  Awareness: 8,
  Intuition: 8,
  Charm: 8,
  Willpower: 8,
};

const ABILITY_SCHOOL_STAT_MAP: { [key: string]: string } = {
  Force: "Might",
  Bastion: "Endurance",
  Ki: "Finesse",
  Grace: "Reflexes",
  Biomancy: "Vitality",
  Cunning: "Finesse",
  Cosmos: "Logic",
  Evocation: "Knowledge",
  Spirit: "Awareness",
  Psionics: "Intuition",
  Command: "Charm",
  Chaos: "Willpower",
};

// --- Helper: capitalize string ---
const capitalize = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : "");

// --- Main Component ---
const CharacterCreationScreen: React.FC<CharacterCreationScreenProps> = ({
  onCharacterCreated,
  onBack,
}) => {
  // --- State ---
  const [step, setStep] = useState<CreationStep>("kingdom");
  const [featureStep, setFeatureStep] = useState(0);

  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: true,
    error: null,
  });
  const [rulesData, setRulesData] = useState<RulesData>({
    kingdomFeatures: null,
    originChoices: [],
    childhoodChoices: [],
    comingOfAgeChoices: [],
    trainingChoices: [],
    devotionChoices: [],
    abilityTalents: [], // <-- Starts empty
    abilitySchools: [],
    all_skills: {},
    ability_school_stats: ABILITY_SCHOOL_STAT_MAP,
  });
  const [choices, setChoices] = useState<Choices>({
    kingdom: null,
    featureChoices: [],
    originChoice: null,
    childhoodChoice: null,
    comingOfAgeChoice: null,
    trainingChoice: null,
    devotionChoice: null,
    abilitySchool: null,
    abilityTalent: null,
    name: "",
  });

  // --- Live Stat Calculation ---
  const calculatedStats = useMemo(() => {
    const newStats = { ...BASE_STATS };
    if (!choices.kingdom || !rulesData.kingdomFeatures) {
      return newStats;
    }

    const applyMods = (mods: FeatureMods) => {
      for (const [modValue, statList] of Object.entries(mods)) {
        const value = parseInt(modValue, 10);
        if (isNaN(value)) continue;

        for (const statName of statList) {
          if (statName in newStats) {
            newStats[statName as keyof typeof newStats] += value;
          }
        }
      }
    };

    for (const featureChoice of choices.featureChoices) {
      const { feature_id, choice_name } = featureChoice;
      const kingdom_key = feature_id === "F9" ? "All" : choices.kingdom;

      const choiceData = rulesData.kingdomFeatures[feature_id]?.[
        kingdom_key
      ]?.find((c) => c.name === choice_name);

      if (choiceData?.mods) {
        applyMods(choiceData.mods);
      }
    }
    return newStats;
  }, [choices.kingdom, choices.featureChoices, rulesData.kingdomFeatures]);

  // --- Live Skill Calculation ---
  const calculatedSkills = useMemo(() => {
    const skills = new Set<string>();
    const allChoices = [
      rulesData.originChoices.find((c) => c.name === choices.originChoice),
      rulesData.childhoodChoices.find(
        (c) => c.name === choices.childhoodChoice,
      ),
      rulesData.comingOfAgeChoices.find(
        (c) => c.name === choices.comingOfAgeChoice,
      ),
      rulesData.trainingChoices.find(
        (c) => c.name === choices.trainingChoice,
      ),
      rulesData.devotionChoices.find(
        (c) => c.name === choices.devotionChoice,
      ),
    ];
    for (const choice of allChoices) {
      if (choice) {
        for (const skill of choice.skills) {
          skills.add(skill);
        }
      }
    }
    return skills;
  }, [
    choices.originChoice,
    choices.childhoodChoice,
    choices.comingOfAgeChoice,
    choices.trainingChoice,
    choices.devotionChoice,
    rulesData,
  ]);

  // --- Data Loading Effects ---

  // Initial Load (runs once)
  useEffect(() => {
    const loadAllData = async () => {
      try {
        setLoadingState({ isLoading: true, error: null });

        const [
          features,
          origins,
          childhoods,
          comingOfAges,
          trainings,
          devotions,
          schools,
          allSkills,
        ] = await Promise.all([
          getKingdomFeatures(),
          getOriginChoices(),
          getChildhoodChoices(),
          getComingOfAgeChoices(),
          getTrainingChoices(),
          getDevotionChoices(),
          // getAbilityTalents(), // <-- REMOVED
          getAbilitySchools(),
          getAllSkills(),
        ]);

        setRulesData((prev) => ({
          ...prev,
          kingdomFeatures: features,
          originChoices: origins,
          childhoodChoices: childhoods,
          comingOfAgeChoices: comingOfAges,
          trainingChoices: trainings,
          devotionChoices: devotions,
          // abilityTalents: abTalents, // <-- REMOVED
          abilitySchools: schools,
          all_skills: allSkills,
          ability_school_stats: ABILITY_SCHOOL_STAT_MAP,
        }));
        setLoadingState({ isLoading: false, error: null });
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : "An unknown error occurred while loading rules data.";
        setLoadingState({
          isLoading: false,
          error: message,
        });
      }
    };
    loadAllData();
  }, []);

  // --- *** NEW DYNAMIC HOOK *** ---
  // Runs when the step changes to 'talent'
  useEffect(() => {
    if (step === "talent") {
      const fetchTalents = async () => {
        setLoadingState({ isLoading: true, error: null });

        // Build the skill ranks map
        const skillRanks: { [key: string]: number } = {};
        for (const skillName of calculatedSkills) {
          skillRanks[skillName] = 1; // All background skills are Rank 1
        }

        try {
          console.log("Fetching eligible talents with:", calculatedStats, skillRanks);
          const eligibleTalents = await getEligibleTalents(
            calculatedStats,
            skillRanks,
          );
          
          setRulesData((prev) => ({
            ...prev,
            abilityTalents: eligibleTalents,
          }));
          setLoadingState({ isLoading: false, error: null });
        } catch (err) {
          const message =
            err instanceof Error
              ? err.message
              : "An unknown error occurred while fetching eligible talents.";
          setLoadingState({
            isLoading: false,
            error: message,
          });
        }
      };
      fetchTalents();
    }
  }, [step, calculatedStats, calculatedSkills]); // Dependencies

  // --- Navigation Handlers ---
  const handleNext = () => {
    switch (step) {
      case "kingdom":
        setStep("features");
        setFeatureStep(0);
        break;
      case "features":
        if (featureStep < FEATURE_IDS.length - 1) {
          setFeatureStep((s) => s + 1);
        } else {
          setStep("origin");
        }
        break;
      case "origin":
        setStep("childhood");
        break;
      case "childhood":
        setStep("comingOfAge");
        break;
      case "comingOfAge":
        setStep("training");
        break;
      case "training":
        setStep("devotion");
        break;
      case "devotion":
        setStep("school");
        break;
      case "school":
        setStep("talent");
        break;
      case "talent":
        setStep("name");
        break;
      case "name":
        setStep("review");
        break;
      case "review":
        // This is handled by handleSubmit
        break;
    }
  };
  const handleBack = () => {
    switch (step) {
      case "kingdom":
        onBack();
        break;
      case "features":
        if (featureStep > 0) {
          setFeatureStep((s) => s - 1);
        } else {
          setStep("kingdom");
        }
        break;
      case "origin":
        setStep("features");
        setFeatureStep(FEATURE_IDS.length - 1);
        break;
      case "childhood":
        setStep("origin");
        break;
      case "comingOfAge":
        setStep("childhood");
        break;
      case "training":
        setStep("comingOfAge");
        break;
      case "devotion":
        setStep("training");
        break;
      case "school":
        setStep("devotion");
        break;
      case "talent":
        setStep("school");
        break;
      case "name":
        setStep("talent");
        break;
      case "review":
        setStep("name");
        break;
    }
  };

  // --- Selection Handlers ---
  const selectKingdom = (kingdom: string) => {
    setChoices((c) => ({ ...c, kingdom, featureChoices: [] }));
    handleNext();
  };
  const selectFeatureChoice = (
    featureId: string,
    choice: KingdomFeatureChoice,
  ) => {
    setChoices((c) => {
      const otherChoices = c.featureChoices.filter(
        (fc) => fc.feature_id !== featureId,
      );
      const newChoice: FeatureChoiceRequest = {
        feature_id: featureId,
        choice_name: choice.name,
      };
      return { ...c, featureChoices: [...otherChoices, newChoice] };
    });

    if (featureId !== "F9") {
      handleNext();
    }
  };

  const selectOrigin = (choiceName: string) => {
    setChoices((c) => ({ ...c, originChoice: choiceName }));
    handleNext();
  };
  const selectChildhood = (choiceName: string) => {
    setChoices((c) => ({ ...c, childhoodChoice: choiceName }));
    handleNext();
  };
  const selectComingOfAge = (choiceName: string) => {
    setChoices((c) => ({ ...c, comingOfAgeChoice: choiceName }));
    handleNext();
  };
  const selectTraining = (choiceName: string) => {
    setChoices((c) => ({ ...c, trainingChoice: choiceName }));
    handleNext();
  };
  const selectDevotion = (choiceName: string) => {
    setChoices((c) => ({ ...c, devotionChoice: choiceName }));
    handleNext();
  };

  const selectSchool = (schoolName: string) => {
    setChoices((c) => ({
      ...c,
      abilitySchool: schoolName,
      abilityTalent: null, // Reset talent choice if school changes
    }));
    handleNext();
  };
  const selectAbilityTalent = (talentName: string) => {
    setChoices((c) => ({ ...c, abilityTalent: talentName }));
    handleNext();
  };

  // --- Final Submission ---
  const handleSubmit = async () => {
    if (!isReviewComplete()) return;

    const f9Choice = choices.featureChoices.find((f) => f.feature_id === "F9");
    if (!f9Choice) {
      setLoadingState((s) => ({
        ...s,
        error: "Please select a Capstone (F9) choice.",
      }));
      return;
    }
    
    const payload: CharacterCreateRequest = {
      name: choices.name,
      kingdom: choices.kingdom!,
      feature_choices: choices.featureChoices,
      origin_choice: choices.originChoice!,
      childhood_choice: choices.childhoodChoice!,
      coming_of_age_choice: choices.comingOfAgeChoice!,
      training_choice: choices.trainingChoice!,
      devotion_choice: choices.devotionChoice!,
      ability_school: choices.abilitySchool!,
      ability_talent: choices.abilityTalent!,
    };

    try {
      setLoadingState({ isLoading: true, error: null });
      const newCharacter = await createCharacter(payload);
      onCharacterCreated(newCharacter);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "An unknown error occurred while creating the character.";
      setLoadingState({
        isLoading: false,
        error: message,
      });
    }
  };

  // --- Render Functions for Steps ---

  const renderLoading = (text: string = "Loading Rules Data...") => (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4">{text}</h2>
      <p className="text-gray-400">Please wait.</p>
    </div>
  );
  const renderError = () => (
    <div className="text-center text-red-400">
      <h2 className="text-2xl font-bold mb-4">Error</h2>
      <p>{loadingState.error}</p>
      <button
        onClick={onBack}
        className="mt-6 bg-red-700 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
      >
        Back to Menu
      </button>
    </div>
  );
  const renderKingdomSelect = () => (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
        Step 1: Choose your Kingdom
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {KINGDOMS.map((kingdom) => (
          <button
            key={kingdom}
            onClick={() => selectKingdom(kingdom)}
            className="stone-button p-6 text-xl"
          >
            {kingdom}
          </button>
        ))}
      </div>
    </div>
  );
  const renderFeatureSelect = () => {
    const featureId = FEATURE_IDS[featureStep];
    const kingdom = choices.kingdom!;
    const featureSet = rulesData.kingdomFeatures?.[featureId]?.[kingdom];

    if (!featureSet)
      return (
        <div className="text-red-400">
          Error: Could not find features for {kingdom}.
        </div>
      );

    return (
      <div>
        <h2 className="text-3xl font-bold mb-2 text-center text-amber-300 glow-text font-medieval">
          Step 2: Features ({featureStep + 1} / {FEATURE_IDS.length})
        </h2>
        <h3 className="text-xl text-stone-400 mb-6 text-center">
          Choose your{" "}
          <span className="font-bold text-amber-300">{featureId}</span> Feature
        </h3>
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2 stone-panel p-4">
          {featureSet.map((choice) => (
            <button
              key={choice.name}
              onClick={() => selectFeatureChoice(featureId, choice)}
              className="w-full text-left p-4 stone-button"
            >
              <p className="text-lg font-semibold">{choice.name}</p>
              <p className="text-sm text-stone-300">
                {Object.entries(choice.mods).map(
                  ([mod, stats]) => `(${mod}: ${stats.join(", ")}) `,
                )}
              </p>
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderBackgroundChoice = (
    stepTitle: string,
    choices: BackgroundChoiceInfo[],
    onSelect: (choiceName: string) => void,
  ) => (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
        {stepTitle}
      </h2>
      <div className="space-y-3 max-h-96 overflow-y-auto pr-2 stone-panel p-4">
        {choices.map((choice) => (
          <button
            key={choice.name}
            onClick={() => onSelect(choice.name)}
            className="w-full text-left p-4 stone-button"
          >
            <p className="text-lg font-semibold">{choice.name}</p>
            <p className="text-sm text-stone-300">{choice.description}</p>
            <p className="text-xs text-amber-300 mt-1">
              Skills: {choice.skills.join(", ")}
            </p>
          </button>
        ))}
      </div>
    </div>
  );

  const renderSchoolSelect = () => {
    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
          Step 8: Choose Ability School
        </h2>

        <div className="mb-4 p-2 stone-panel bg-gray-900/50">
          <p className="text-sm text-gray-300">
            Your current stats (Base 8 + Features):
          </p>
          <div className="grid grid-cols-4 gap-x-2 gap-y-1 text-sm">
            {Object.entries(calculatedStats).map(([stat, value]) => (
              <span
                key={stat}
                className={value >= 10 ? "text-green-400" : "text-gray-400"}
              >
                {stat}: {value}
              </span>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {rulesData.abilitySchools.map((school) => {
            const requiredStat = rulesData.ability_school_stats[school] || "Might";
            const currentStatValue =
              calculatedStats[requiredStat as keyof typeof calculatedStats] || 8;
            const isEligible = currentStatValue >= 10;

            return (
              <button
                key={school}
                onClick={() => selectSchool(school)}
                disabled={!isEligible}
                className={`stone-button p-4 text-lg ${
                  !isEligible ? "opacity-50 grayscale" : ""
                }`}
                title={
                  isEligible
                    ? `Requires ${requiredStat} 10 (You have ${currentStatValue})`
                    : `Requires ${requiredStat} 10 (You have ${currentStatValue})`
                }
              >
                {capitalize(school)}
                <span className="block text-xs text-gray-400">
                  (Req: {requiredStat})
                </span>
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  const renderTalentSelect = () => {
    // This now reads from the dynamically loaded state
    const availableTalents = rulesData.abilityTalents;

    if (loadingState.isLoading) {
      return renderLoading("Fetching Eligible Talents...");
    }
    
    // This now handles the case where the API correctly returns an empty list
    if (!availableTalents || availableTalents.length === 0) {
      return (
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4 text-amber-300">
            Step 9: Choose Ability Talent
          </h2>
          <p className="text-red-400">
            No eligible talents were found for your current stats and skills.
          </p>
          <p className="text-gray-400 text-sm mt-2">
            (This is likely a data issue in `talents.json`. Go back and change
            your stats or add low-level talents to the data file.)
          </p>
        </div>
      );
    }

    return (
      <div>
        <h2 className="text-3xl font-bold mb-2 text-center text-amber-300 glow-text font-medieval">
          Step 9: Choose Ability Talent
        </h2>
        <h3 className="text-xl text-stone-400 mb-6 text-center">
          For School:{" "}
          <span className="font-bold text-amber-300">
            {capitalize(choices.abilitySchool!)}
          </span>
        </h3>

        <div className="mb-4 p-2 stone-panel bg-gray-900/50">
          <p className="text-sm text-gray-300">Your current stats:</p>
          <div className="grid grid-cols-4 gap-x-2 gap-y-1 text-xs">
            {Object.entries(calculatedStats).map(([stat, value]) => (
              <span
                key={stat}
                className={value >= 10 ? "text-green-400" : "text-gray-400"}
              >
                {stat}: {value}
              </span>
            ))}
          </div>
          <p className="text-sm text-gray-300 mt-2">
            Your granted skills (Rank 1):
          </p>
          <p className="text-xs text-amber-300">
            {[...calculatedSkills].join(", ") || "None"}
          </p>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto pr-2 stone-panel p-4">
          {availableTalents.map((talent) => (
            <button
              key={talent.name}
              onClick={() => selectAbilityTalent(talent.name)}
              className="w-full text-left p-4 stone-button"
            >
              <p className="text-lg font-semibold">{talent.name}</p>
              <p className="text-sm text-stone-300">
                {talent.effect} {/* Use effect, not description */}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Source: {talent.source}
              </p>
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderNameInput = () => {
    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
          Step 10: Choose Your Name
        </h2>
        <input
          type="text"
          value={choices.name}
          onChange={(e) => setChoices((c) => ({ ...c, name: e.target.value }))}
          className="w-full p-4 bg-stone-800 border border-stone-600 rounded-lg text-white text-xl"
          placeholder="Enter character name"
        />
        <button
          onClick={handleNext}
          disabled={!choices.name.trim()}
          className="w-full mt-4 stone-button"
        >
          Review Character
        </button>
      </div>
    );
  };

  const isReviewComplete = () => {
    const f9Choice = choices.featureChoices.find((f) => f.feature_id === "F9");
    return (
      choices.kingdom &&
      choices.featureChoices.length >= 8 && // F1-F8
      f9Choice && // F9
      choices.originChoice &&
      choices.childhoodChoice &&
      choices.comingOfAgeChoice &&
      choices.trainingChoice &&
      choices.devotionChoice &&
      choices.abilitySchool &&
      choices.abilityTalent && // This must be selected
      choices.name.trim()
    );
  };
  const renderReview = () => {
    const f9Choices = rulesData.kingdomFeatures?.["F9"]?.["All"] || [];
    const f9Choice = choices.featureChoices.find((f) => f.feature_id === "F9");

    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
          Step 11: Review &amp; Create
        </h2>
        <div className="space-y-2 text-lg p-4 stone-panel text-left max-h-96 overflow-y-auto">
          <p>
            <strong>Name:</strong> {choices.name || "..."}
          </p>
          <p>
            <strong>Kingdom:</strong> {choices.kingdom || "..."}
          </p>
          <p>
            <strong>Features (F1-F8):</strong>{" "}
            {choices.featureChoices.filter((f) => f.feature_id !== "F9").length}{" "}
            / 8 chosen
          </p>
          <hr className="border-stone-600 my-2" />
          <p>
            <strong>Origin:</strong> {choices.originChoice || "..."}
          </p>
          <p>
            <strong>Childhood:</strong> {choices.childhoodChoice || "..."}
          </p>
          <p>
            <strong>Coming of Age:</strong> {choices.comingOfAgeChoice || "..."}
          </p>
          <p>
            <strong>Training:</strong> {choices.trainingChoice || "..."}
          </p>
          <p>
            <strong>Devotion:</strong> {choices.devotionChoice || "..."}
          </p>
          <hr className="border-stone-600 my-2" />
          <p>
            <strong>School:</strong> {choices.abilitySchool || "..."}
          </p>
          <p>
            <strong>Talent:</strong> {choices.abilityTalent || "..."}
          </p>

          {/* F9 (Capstone) Selection */}
          <div className="pt-4 border-t border-stone-700 mt-4">
            <h4 className="text-xl font-semibold mb-2">
              F9: Capstone (+2 to one stat)
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {f9Choices.map((choice) => (
                <button
                  key={choice.name}
                  onClick={() => selectFeatureChoice("F9", choice)}
                  className={`stone-button p-2 text-sm
                                        ${
                                          f9Choice?.choice_name === choice.name
                                            ? "active"
                                            : ""
                                        }`}
                >
                  {choice.name.replace("Capstone: ", "")}
                </button>
              ))}
            </div>
          </div>
        </div>

        {loadingState.error && (
          <p className="text-red-400 text-sm mt-4">{loadingState.error}</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={!isReviewComplete() || loadingState.isLoading}
          className="w-full mt-6 stone-button"
        >
          {loadingState.isLoading ? "Creating..." : "Create Character"}
        </button>
      </div>
    );
  };

  // --- Main Render Switch ---
  const renderCurrentStep = () => {
    // Check for initial load
    if (loadingState.isLoading && !rulesData.kingdomFeatures)
      return renderLoading();
    // Check for initial load error
    if (loadingState.error && !rulesData.kingdomFeatures) return renderError();

    // Normal step rendering
    switch (step) {
      case "kingdom":
        return renderKingdomSelect();
      case "features":
        return renderFeatureSelect();
      case "origin":
        return renderBackgroundChoice(
          "Step 3: Choose Origin",
          rulesData.originChoices,
          selectOrigin,
        );
      case "childhood":
        return renderBackgroundChoice(
          "Step 4: Choose Childhood",
          rulesData.childhoodChoices,
          selectChildhood,
        );
      case "comingOfAge":
        return renderBackgroundChoice(
          "Step 5: Choose Coming of Age",
          rulesData.comingOfAgeChoices,
          selectComingOfAge,
        );
      case "training":
        return renderBackgroundChoice(
          "Step 6: Choose Training",
          rulesData.trainingChoices,
          selectTraining,
        );
      case "devotion":
        return renderBackgroundChoice(
          "Step 7: Choose Devotion",
          rulesData.devotionChoices,
          selectDevotion,
        );
      case "school":
        return renderSchoolSelect();
      case "talent":
        // This step now has its own loading/error state
        if (loadingState.isLoading) return renderLoading("Fetching Eligible Talents...");
        if (loadingState.error) return renderError(); // Show talent-specific error
        return renderTalentSelect();
      case "name":
        return renderNameInput();
      case "review":
        return renderReview();
      default:
        return <div>Unknown step.</div>;
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="w-full max-w-3xl stone-panel p-8">
        {renderCurrentStep()}

        {/* Navigation Buttons */}
        <div className="mt-8 pt-4 border-t border-stone-700">
          <button
            onClick={handleBack}
            disabled={loadingState.isLoading}
            className="stone-button"
          >
            Back
          </button>
        </div>
      </div>
    </div>
  );
};

export default CharacterCreationScreen;