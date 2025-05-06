import enTranslation from '../i18n/locales/en/translation.json';
import koTranslation from '../i18n/locales/ko/translation.json';
import jaTranslation from '../i18n/locales/ja/translation.json';
import zhTranslation from '../i18n/locales/zh/translation.json';
import esTranslation from '../i18n/locales/es/translation.json';
import frTranslation from '../i18n/locales/fr/translation.json';
import deTranslation from '../i18n/locales/de/translation.json';
import itTranslation from '../i18n/locales/it/translation.json';
import ptTranslation from '../i18n/locales/pt/translation.json';
import ruTranslation from '../i18n/locales/ru/translation.json';

// The base language is considered the source of truth for keys
const baseLanguage = 'en';
const baseTranslation = enTranslation;

// All translations by language code
const translations: Record<string, any> = {
  en: enTranslation,
  ko: koTranslation,
  ja: jaTranslation,
  zh: zhTranslation,
  es: esTranslation,
  fr: frTranslation,
  de: deTranslation,
  it: itTranslation,
  pt: ptTranslation,
  ru: ruTranslation
};

/**
 * Check for missing translation keys in a target language compared to the base language
 * @param targetLang The target language code to check
 * @param baseKeys Optional starting set of keys to narrow the check
 * @param currentPath Optional current path for recursive checks
 * @returns An array of missing key paths
 */
export const findMissingTranslationKeys = (
  targetLang: string,
  baseKeys: Record<string, any> = baseTranslation,
  currentPath: string = ''
): string[] => {
  if (!translations[targetLang]) {
    console.error(`Translation file not found for language: ${targetLang}`);
    return [];
  }

  const missingKeys: string[] = [];
  const targetTranslation = translations[targetLang];

  // Recursive function to check nested objects
  const checkKeys = (baseObj: any, targetObj: any, path: string = '') => {
    Object.keys(baseObj).forEach(key => {
      const fullPath = path ? `${path}.${key}` : key;
      
      // If key doesn't exist in target language
      if (!(key in targetObj)) {
        missingKeys.push(fullPath);
        return;
      }
      
      // If both values are objects, recurse
      if (
        typeof baseObj[key] === 'object' && 
        baseObj[key] !== null &&
        typeof targetObj[key] === 'object' && 
        targetObj[key] !== null
      ) {
        checkKeys(baseObj[key], targetObj[key], fullPath);
      }
    });
  };

  checkKeys(baseKeys, targetTranslation, currentPath);
  return missingKeys;
};

/**
 * Check all languages for missing translation keys and log them
 */
export const checkAllTranslations = (): void => {
  Object.keys(translations).forEach(lang => {
    if (lang === baseLanguage) return; // Skip base language
    
    const missingKeys = findMissingTranslationKeys(lang);
    
    if (missingKeys.length > 0) {
      console.warn(`[i18n] ${missingKeys.length} missing translation keys in language: ${lang}`);
      console.table(missingKeys.map(key => ({ key })));
    } else {
      console.info(`[i18n] No missing translation keys in language: ${lang}`);
    }
  });
};

/**
 * Add this function to a development page or run from console
 * to check for missing translations.
 */
export const runTranslationCheck = (): void => {
  console.info('[i18n] Running translation completeness check...');
  checkAllTranslations();
};

// Automatically run check in development mode
if (process.env.NODE_ENV === 'development') {
  // Delay to avoid running during initial page load
  setTimeout(() => {
    runTranslationCheck();
  }, 2000);
}

export default {
  findMissingTranslationKeys,
  checkAllTranslations,
  runTranslationCheck
};
