import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import BrandWizard from "./BrandWizard-ja.jsx";
import { I18nProvider } from "./i18n.jsx";
import stringsJa from "./strings-ja.json";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nProvider locale="ja" strings={stringsJa}>
      <BrandWizard />
    </I18nProvider>
  </React.StrictMode>
);
