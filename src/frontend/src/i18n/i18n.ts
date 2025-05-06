import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';
import Cookies from 'js-cookie';

// Import all translation files
import enTranslation from './locales/en/translation.json';
import koTranslation from './locales/ko/translation.json';
import jaTranslation from './locales/ja/translation.json';
import zhTranslation from './locales/zh/translation.json';
import esTranslation from './locales/es/translation.json';
import frTranslation from './locales/fr/translation.json';
import deTranslation from './locales/de/translation.json';
import itTranslation from './locales/it/translation.json';
import ptTranslation from './locales/pt/translation.json';
import ruTranslation from './locales/ru/translation.json';

// Check for stored native language preference in cookie
const getNativeLanguageFromCookie = (): string => {
  return Cookies.get('lingogi_ui_language') || '';
};

// Initialize i18n
i18n
  // Load translations from HTTP backend
  .use(Backend)
  // Detect user language
  .use(LanguageDetector)
  // Pass i18n to react-i18next
  .use(initReactI18next)
  // Initialize with config
  .init({
    // Type this properly for TypeScript
    // Default language if nothing is detected
    fallbackLng: 'en',
    // Try to use cookie first if available
    lng: getNativeLanguageFromCookie(),
    // Debug mode in development
    debug: process.env.NODE_ENV === 'development',
    
    // Log missing translation keys in development mode
    saveMissing: process.env.NODE_ENV === 'development',
    missingKeyHandler: (lng, ns, key, fallbackValue) => {
      console.warn(`[i18n] MISSING TRANSLATION KEY: "${key}" for language: ${lng}`, {
        namespace: ns,
        fallbackValue: fallbackValue
      });
    },
    
    // Configure how missing translations are handled
    partialBundledLanguages: true, // Allow partial translations
    appendNamespaceToMissingKey: true, // Makes debugging easier
    parseMissingKeyHandler: (missing) => {
      // Log only in development to avoid console spam in production
      if (process.env.NODE_ENV === 'development') {
        console.warn(`[i18n] Parsing missing key: ${missing}`);
      }
      return missing;
    },
    // Resources for static translations
    resources: {
      en: { translation: enTranslation },
      ko: { translation: koTranslation },
      ja: { translation: jaTranslation },
      zh: { translation: zhTranslation },
      es: { translation: esTranslation },
      fr: { translation: frTranslation },
      de: { translation: deTranslation },
      it: { translation: itTranslation },
      pt: { translation: ptTranslation },
      ru: { translation: ruTranslation },
    },
    // Default namespace
    defaultNS: 'translation',
    // Allow nested keys
    keySeparator: '.',
    // Return nested objects
    returnObjects: true,
    // Interpolation settings
    interpolation: {
      escapeValue: false, // Don't escape HTML
    },
    // React specific settings
    react: {
      useSuspense: true,
      bindI18n: 'languageChanged loaded',
    },
    // Language detection settings
    detection: {
      order: ['cookie', 'localStorage', 'navigator'],
      caches: ['cookie'],
      lookupCookie: 'lingogi_ui_language', // Use proper property name for the plugin
    }
  });

// Force immediate language application when a new language is set
const originalChangeLanguage = i18n.changeLanguage;
i18n.changeLanguage = async (lng: string | undefined, ...args) => {
  console.log(`Changing language immediately to: ${lng}`);
  // Save to cookie for persistence
  if (lng) Cookies.set('lingogi_ui_language', lng, { expires: 30 });
  // Call original method
  return originalChangeLanguage(lng, ...args);
};

export default i18n;
