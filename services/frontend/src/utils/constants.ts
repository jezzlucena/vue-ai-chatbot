import type { Language } from '@/types/Language'

export const LANGUAGES: {
  [key in Language]: {
    long: string
    short: string
  }
} = {
  en_US: {
    long: 'English 🇺🇸',
    short: '🇺🇸',
  },
  es_ES: {
    long: 'Español 🇪🇸',
    short: '🇪🇸',
  },
  pt_BR: {
    long: 'Português 🇧🇷',
    short: '🇧🇷',
  },
}
