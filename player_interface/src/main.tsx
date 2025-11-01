// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { initializeAssets } from "./assets/assetLoader.ts"; // Correct path

// Initialize assets before rendering the app
initializeAssets()
  .then(() => {
    ReactDOM.createRoot(document.getElementById("root")!).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
    );
  })
  .catch((error) => {
    console.error("Failed to initialize assets:", error);
  });
