"use client";

import type { Language } from "@hellodesk/shared/api-types";

const LANGUAGE_OPTIONS: ReadonlyArray<{ language: Language; label: string; nativeLabel: string }> = [
  { language: "en", label: "English", nativeLabel: "English" },
  { language: "vi", label: "Vietnamese", nativeLabel: "Tiếng Việt" },
];

interface LanguagePickerProps {
  isStarting?: boolean;
  errorMessage?: string;
  onSelect: (language: Language) => void;
}

export function LanguagePicker({ isStarting, errorMessage, onSelect }: LanguagePickerProps) {
  return (
    <section className="kiosk-card" aria-labelledby="welcome-heading">
      <p className="eyebrow">HelloDesk</p>
      <h1 id="welcome-heading">Welcome</h1>
      <p>Choose your language to begin.</p>
      <p lang="vi">Chọn ngôn ngữ để bắt đầu.</p>
      <div className="language-options" role="group" aria-label="Choose your language">
        {LANGUAGE_OPTIONS.map(({ language, label, nativeLabel }) => (
          <button
            key={language}
            className="language-button"
            type="button"
            disabled={isStarting}
            onClick={() => onSelect(language)}
          >
            <span>{label}</span>
            <span lang={language}>{nativeLabel}</span>
          </button>
        ))}
      </div>
      {errorMessage ? <p className="error-message" role="alert">{errorMessage}</p> : null}
    </section>
  );
}
