import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import BrandWizard from "./BrandWizard-tw.jsx";
import { I18nProvider } from "./i18n.jsx";
import stringsTw from "./strings-tw.json";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <I18nProvider locale="tw" strings={stringsTw}>
      <BrandWizard />
    </I18nProvider>
  </React.StrictMode>
);
