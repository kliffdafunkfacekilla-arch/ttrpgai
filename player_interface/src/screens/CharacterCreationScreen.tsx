// src/screens/CharacterCreationScreen.tsx
import React, { useState, useEffect } from "react";
import {
  createCharacter,
  getKingdomFeatures,
  getBackgroundTalents,
  getAbilityTalents,
  getAbilitySchools,
} from "../api/apiClient";
import {
  type CharacterContextResponse,
  type KingdomFeaturesData,
  type TalentInfo,
  type KingdomFeatureChoice,
  type CharacterCreateRequest,
  type FeatureChoiceRequest,
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
  | "background"
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
  backgroundTalents: TalentInfo[];
  abilityTalents: TalentInfo[];
  abilitySchools: string[];
};
type Choices = {
  kingdom: string | null;
  featureChoices: FeatureChoiceRequest[];
  backgroundTalent: string | null;
  abilitySchool: string | null;
  abilityTalent: string | null;
  name: string;
};

// --- Constants ---
const KINGDOMS = ["Mammal", "Reptile", "Avian", "Aquatic", "Insect", "Plant"];
// The features we need to select, in order. F9 is separate.
const FEATURE_IDS: string[] = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"];

// --- Helper: capitalize string ---
const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

// --- Main Component ---
const CharacterCreationScreen: React.FC<CharacterCreationScreenProps> = ({
  onCharacterCreated,
  onBack,
}) => {
  // --- State ---
  const [step, setStep] = useState<CreationStep>("kingdom");
  const [featureStep, setFeatureStep] = useState(0); // Index for F1-F8

  const [loadingState, setLoadingState] = useState<LoadingState>({
    isLoading: true,
    error: null,
  });
  const [rulesData, setRulesData] = useState<RulesData>({
    kingdomFeatures: null,
    backgroundTalents: [],
    abilityTalents: [],
    abilitySchools: [],
  });
  const [choices, setChoices] = useState<Choices>({
    kingdom: null,
    featureChoices: [],
    backgroundTalent: null,
    abilitySchool: null,
    abilityTalent: null,
    name: "",
  });

  // --- Data Loading Effect ---
  useEffect(() => {
    const loadAllData = async () => {
      try {
        setLoadingState({ isLoading: true, error: null });
        const [features, bgTalents, abTalents, schools] = await Promise.all([
          getKingdomFeatures(),
          getBackgroundTalents(),
          getAbilityTalents(),
          getAbilitySchools(),
        ]);

        setRulesData({
          kingdomFeatures: features,
          backgroundTalents: bgTalents,
          abilityTalents: abTalents,
          abilitySchools: schools,
        });
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

  // --- Navigation Handlers ---
  const handleNext = () => {
    switch (step) {
      case "kingdom":
        setStep("features");
        setFeatureStep(0); // Start at F1
        break;
      case "features":
        if (featureStep < FEATURE_IDS.length - 1) {
          setFeatureStep((s) => s + 1); // Go to next feature
        } else {
          setStep("background"); // Done with F1-F8
        }
        break;
      case "background":
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
    }
  };

  const handleBack = () => {
    switch (step) {
      case "kingdom":
        onBack(); // Go back to Main Menu
        break;
      case "features":
        if (featureStep > 0) {
          setFeatureStep((s) => s - 1); // Go to previous feature
        } else {
          setStep("kingdom"); // Go back to kingdom select
        }
        break;
      case "background":
        setStep("features");
        setFeatureStep(FEATURE_IDS.length - 1); // Go to last feature (F8)
        break;
      case "school":
        setStep("background");
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
    setChoices((c) => ({ ...c, kingdom, featureChoices: [] })); // Reset features if kingdom changes
    handleNext();
  };

  const selectFeatureChoice = (
    featureId: string,
    choice: KingdomFeatureChoice,
  ) => {
    setChoices((c) => {
      // Remove any previous choice for this featureId
      const otherChoices = c.featureChoices.filter(
        (fc) => fc.feature_id !== featureId,
      );
      const newChoice: FeatureChoiceRequest = {
        feature_id: featureId,
        choice_name: choice.name,
      };
      return { ...c, featureChoices: [...otherChoices, newChoice] };
    });

    // F9 (Capstone) is a special case, handled in the 'review' step
    if (featureId !== "F9") {
      handleNext();
    }
  };

  const selectBackground = (talentName: string) => {
    setChoices((c) => ({ ...c, backgroundTalent: talentName }));
    handleNext();
  };

  const selectSchool = (schoolName: string) => {
    setChoices((c) => ({
      ...c,
      abilitySchool: schoolName,
      abilityTalent: null,
    })); // Reset talent
    handleNext();
  };

  const selectAbilityTalent = (talentName: string) => {
    setChoices((c) => ({ ...c, abilityTalent: talentName }));
    handleNext();
  };

  // --- Final Submission ---
  const handleSubmit = async () => {
    if (!isReviewComplete()) return;

    // Add the F9 (Capstone) choice
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
      feature_choices: choices.featureChoices, // This now includes F9
      background_talent: choices.backgroundTalent!,
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

  const renderLoading = () => (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4">Loading Rules Data...</h2>
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
      return <div className="text-red-400">Error: Could not find features for {kingdom}.</div>;

    return (
      <div>
        <h2 className="text-3xl font-bold mb-2 text-center text-amber-300 glow-text font-medieval">
          Step 2: Features ({featureStep + 1} / {FEATURE_IDS.length})
        </h2>
        <h3 className="text-xl text-stone-400 mb-6 text-center">
          Choose your <span className="font-bold text-amber-300">{featureId}</span>{" "}
          Feature
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

  const renderBackgroundSelect = () => (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
        Step 3: Choose Background Talent
      </h2>
      <div className="space-y-3 max-h-96 overflow-y-auto pr-2 stone-panel p-4">
        {rulesData.backgroundTalents.map((talent) => (
          <button
            key={talent.name}
            onClick={() => selectBackground(talent.name)}
            className="w-full text-left p-4 stone-button"
          >
            <p className="text-lg font-semibold">{talent.name}</p>
            <p className="text-sm text-stone-300">{talent.description}</p>
          </button>
        ))}
      </div>
    </div>
  );

  const renderSchoolSelect = () => (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
        Step 4: Choose Ability School
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {rulesData.abilitySchools.map((school) => (
          <button
            key={school}
            onClick={() => selectSchool(school)}
            className="stone-button p-4 text-lg"
          >
            {capitalize(school)}
          </button>
        ))}
      </div>
    </div>
  );

  const renderTalentSelect = () => {
    // NOTE: We are currently showing ALL ability talents.
    // A future improvement would be to filter this list based on the
    // `abilityTalents` data structure also containing school info.
    const availableTalents = rulesData.abilityTalents;

    return (
      <div>
        <h2 className="text-3xl font-bold mb-2 text-center text-amber-300 glow-text font-medieval">
          Step 5: Choose Ability Talent
        </h2>
        <h3 className="text-xl text-stone-400 mb-6 text-center">
          For School:{" "}
          <span className="font-bold text-amber-300">
            {capitalize(choices.abilitySchool!)}
          </span>
        </h3>
        <div className="space-y-3 max-h-96 overflow-y-auto pr-2 stone-panel p-4">
          {availableTalents.map((talent) => (
            <button
              key={talent.name}
              onClick={() => selectAbilityTalent(talent.name)}
              className="w-full text-left p-4 stone-button"
            >
              <p className="text-lg font-semibold">{talent.name}</p>
              <p className="text-sm text-stone-300">{talent.description}</p>
            </button>
          ))}
        </div>
      </div>
    );
  };

  const renderNameInput = () => (
    <div>
      <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
        Step 6: Choose Your Name
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

  const isReviewComplete = () => {
    const f9Choice = choices.featureChoices.find((f) => f.feature_id === "F9");
    return (
      choices.kingdom &&
      choices.featureChoices.length >= 8 && // F1-F8
      f9Choice && // F9
      choices.backgroundTalent &&
      choices.abilitySchool &&
      choices.abilityTalent &&
      choices.name.trim()
    );
  };

  const renderReview = () => {
    const f9Choices = rulesData.kingdomFeatures?.["F9"]?.["All"] || [];
    const f9Choice = choices.featureChoices.find((f) => f.feature_id === "F9");

    return (
      <div>
        <h2 className="text-3xl font-bold mb-6 text-center text-amber-300 glow-text font-medieval">
          Step 7: Review &amp; Create
        </h2>
        <div className="space-y-4 text-lg p-4 stone-panel">
          <p>
            <strong>Name:</strong> {choices.name || "..."}
          </p>
          <p>
            <strong>Kingdom:</strong> {choices.kingdom || "..."}
          </p>
          <p>
            <strong>Background:</strong> {choices.backgroundTalent || "..."}
          </p>
          <p>
            <strong>School:</strong> {choices.abilitySchool || "..."}
          </p>
          <p>
            <strong>Talent:</strong> {choices.abilityTalent || "..."}
          </p>
          <p>
            <strong>Features (F1-F8):</strong>{" "}
            {choices.featureChoices.filter((f) => f.feature_id !== "F9").length}{" "}
            / 8 chosen
          </p>

          {/* F9 (Capstone) Selection */}
          <div className="pt-4 border-t border-stone-700">
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
    if (loadingState.isLoading && !rulesData.kingdomFeatures)
      return renderLoading();
    if (loadingState.error && !rulesData.kingdomFeatures) return renderError();

    switch (step) {
      case "kingdom":
        return renderKingdomSelect();
      case "features":
        return renderFeatureSelect();
      case "background":
        return renderBackgroundSelect();
      case "school":
        return renderSchoolSelect();
      case "talent":
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
