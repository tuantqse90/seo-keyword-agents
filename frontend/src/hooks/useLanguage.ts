"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { vi, type I18nKey } from "@/i18n/vi";
import { en } from "@/i18n/en";
import React from "react";

const translations: Record<string, I18nKey> = { vi, en };

export type Language = "vi" | "en";

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: I18nKey;
}

const LanguageContext = createContext<LanguageContextType>({
  lang: "vi",
  setLang: () => {},
  t: vi,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Language>("vi");

  useEffect(() => {
    const stored = localStorage.getItem("lang") as Language | null;
    if (stored && translations[stored]) {
      setLangState(stored);
    }
  }, []);

  const setLang = useCallback((newLang: Language) => {
    setLangState(newLang);
    localStorage.setItem("lang", newLang);
  }, []);

  const t = translations[lang] || vi;

  return React.createElement(
    LanguageContext.Provider,
    { value: { lang, setLang, t } },
    children
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
