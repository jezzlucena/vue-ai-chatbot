import type { Language } from '@/types/Language'
import { type ToastOptions } from 'vue3-toastify'

/**
 * Hardcoded localized names of the available languages
 * in each respective tongue, plus a flag emoji.
 */
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

/** Universal options for displaying toasts across the app */
export const TOAST_OPTIONS: ToastOptions = {
  position: 'top-right',
  autoClose: 2000,
}