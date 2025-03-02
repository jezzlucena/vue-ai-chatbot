import type { Language } from "@/types/Language";

export const LANGUAGES: {
  [key in Language]: {
    long: string,
    short: string
  }
} = {
  en_US: {
    long: "English 🇺🇸",
    short: "Eng 🇺🇸"
  },
  es_ES: { 
    long: "Español 🇪🇸",
    short: "Esp 🇪🇸"
  },
  pt_BR: { 
    long: "Português 🇧🇷",
    short: "Por 🇧🇷"
  }
};
