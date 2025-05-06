import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';
import { useTranslation } from 'react-i18next';
import { useAuth } from './AuthContext';
import i18n from '../i18n/i18n';
import { runTranslationCheck } from '../utils/translationChecker';

// Language options for the entire application
export const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English', nativeName: 'English' },
  { value: 'ko', label: 'Korean', nativeName: '한국어' },
  { value: 'ja', label: 'Japanese', nativeName: '日本語' },
  { value: 'zh', label: 'Chinese', nativeName: '中文' },
  { value: 'es', label: 'Spanish', nativeName: 'Español' },
  { value: 'fr', label: 'French', nativeName: 'Français' },
  { value: 'de', label: 'German', nativeName: 'Deutsch' },
  { value: 'it', label: 'Italian', nativeName: 'Italiano' },
  { value: 'pt', label: 'Portuguese', nativeName: 'Português' },
  { value: 'ru', label: 'Russian', nativeName: 'Русский' },
];

// Cookie names for storing preferences
const COOKIE_TARGET_LANG = 'lingogi_target_language';
const COOKIE_UI_LANG = 'lingogi_ui_language';
const COOKIE_USE_NATIVE = 'lingogi_use_native_language';

// Define the shape of our language context
interface LanguageContextType {
  // Language the user is learning (target language)
  targetLanguage: string;
  setTargetLanguage: (lang: string) => void;
  
  // UI display language (website interface language)
  uiLanguage: string;
  setUILanguage: (lang: string) => void;
  
  // Whether to use native language for UI automatically
  useNativeLanguage: boolean;
  setUseNativeLanguage: (useNative: boolean) => void;
  
  // Helper functions
  getValidLanguageOptions: (currentLanguage?: string) => typeof LANGUAGE_OPTIONS;
  getLanguageLabel: (code: string) => string;
  getNativeLanguageName: (code: string) => string;
}

// Create the context with default values
const LanguageContext = createContext<LanguageContextType>({
  targetLanguage: 'en',
  setTargetLanguage: () => {},
  uiLanguage: 'en',
  setUILanguage: () => {},
  useNativeLanguage: true,
  setUseNativeLanguage: () => {},
  getValidLanguageOptions: () => LANGUAGE_OPTIONS,
  getLanguageLabel: () => '',
  getNativeLanguageName: () => '',
});

// Create a hook for using the language context
export const useLanguagePreferences = () => useContext(LanguageContext);

// Props for the provider component
interface LanguageProviderProps {
  children: ReactNode;
}

// Create the provider component
export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  const { i18n } = useTranslation();
  const { user } = useAuth();
  
  // Initialize state from cookies if available
  const [targetLanguage, setTargetLanguageState] = useState<string>(() => {
    return Cookies.get(COOKIE_TARGET_LANG) || 'en';
  });
  
  const [uiLanguage, setUILanguageState] = useState<string>(() => {
    return Cookies.get(COOKIE_UI_LANG) || 'en';
  });
  
  const [useNativeLanguage, setUseNativeLanguageState] = useState<boolean>(() => {
    return Cookies.get(COOKIE_USE_NATIVE) === 'true'; // Only true if explicitly set
  });

  // Handle user's native language ONLY when useNativeLanguage is true
  useEffect(() => {
    // Only apply if user exists, useNativeLanguage is true, and native language is set
    if (user && useNativeLanguage && user.native_language) {
      console.log(`User loaded/changed, applying native language: ${user.native_language}`);
      // Update state to trigger the language change effect
      setUILanguageState(user.native_language);
      // Save to cookie for persistence
      Cookies.set(COOKIE_UI_LANG, user.native_language, { expires: 30 });
      
      // Log a message about translation behavior for clarity
      console.info(`[i18n] Note: Missing translation keys will fall back to English individually, not affecting the rest of the page.`);
    }
  }, [user, useNativeLanguage]); // Depend on both user and useNativeLanguage flag

  // Effect to update UI language based on priority order - only runs once on mount
  useEffect(() => {
    // Skip this effect if there's already a language set
    if (uiLanguage && uiLanguage !== 'en') return;
    
    // Apply language preferences from user profile or browser/cookies
    const handleLanguagePreference = () => {
      // First priority: Use the stored UI language preference if available
      const storedUILang = Cookies.get(COOKIE_UI_LANG);
      if (storedUILang) {
        console.log(`Setting UI language from cookie: ${storedUILang}`);
        i18n.changeLanguage(storedUILang);
        setUILanguageState(storedUILang);
        return;
      }
      
      // Second priority: Use browser language if available and supported
      const browserLang = navigator.language.split('-')[0];
      const supportedLangs = LANGUAGE_OPTIONS.map(lang => lang.value);
      if (browserLang && supportedLangs.includes(browserLang)) {
        console.log(`Setting UI language from browser: ${browserLang}`);
        i18n.changeLanguage(browserLang);
        setUILanguageState(browserLang);
        Cookies.set(COOKIE_UI_LANG, browserLang, { expires: 30 });
        return;
      }
      
      // Default to English if nothing else is set
      console.log('No language preference found, defaulting to English');
      i18n.changeLanguage('en');
      setUILanguageState('en');
      Cookies.set(COOKIE_UI_LANG, 'en', { expires: 30 });
    };
    
    handleLanguagePreference();
  }, []); // Only run once on mount

  // Effect to actually change the i18n language when uiLanguage changes
  useEffect(() => {
    if (uiLanguage) {
      console.log(`Applying UI language change: ${uiLanguage}`);
      i18n.changeLanguage(uiLanguage);
    }
  }, [uiLanguage]);

  // Update cookie whenever targetLanguage changes
  const setTargetLanguage = (lang: string) => {
    setTargetLanguageState(lang);
    Cookies.set(COOKIE_TARGET_LANG, lang, { expires: 30 });
  };
  
  // Update cookie whenever UI language changes
  const setUILanguage = (lang: string) => {
    console.log(`Setting UI language to: ${lang}`);
    
    try {
      // Important: First update the state so our effects don't interfere
      setUILanguageState(lang);
      
      // Save to cookie for persistence
      Cookies.set(COOKIE_UI_LANG, lang, { expires: 30 });
      
      // Display a notification (this would be better with a toast but we're keeping it simple)
      console.log(`Language successfully changed to: ${lang}`);
      
      // In development, check for missing translations when language changes
      if (process.env.NODE_ENV === 'development') {
        console.info(`[i18n] Checking for missing translations in ${lang}...`);
        // Use setTimeout to ensure this runs after the language change is complete
        setTimeout(() => {
          runTranslationCheck();
        }, 500);
      }
    } catch (error) {
      console.error('Error changing language:', error);
    }
  };

  // Update cookie whenever useNativeLanguage changes
  const setUseNativeLanguage = (useNative: boolean) => {
    // Don't do anything if the value is already set
    if (useNativeLanguage === useNative) return;
    
    setUseNativeLanguageState(useNative);
    Cookies.set(COOKIE_USE_NATIVE, useNative.toString(), { expires: 30 });
    
    // If turning on, set UI language to user's native language
    if (useNative && user?.native_language) {
      setUILanguage(user.native_language);
    }
  };

  // Helper function to get language options excluding the current article language
  const getValidLanguageOptions = (currentLanguage?: string) => {
    if (!currentLanguage) return LANGUAGE_OPTIONS;
    
    return LANGUAGE_OPTIONS.filter(lang => lang.value !== currentLanguage);
  };
  
  // Helper function to get language label from code
  const getLanguageLabel = (code: string): string => {
    const option = LANGUAGE_OPTIONS.find(lang => lang.value === code);
    return option ? option.label : code;
  };
  
  // Helper function to get native name of a language
  const getNativeLanguageName = (langCode: string): string => {
    // Try to find from language options
    const lang = LANGUAGE_OPTIONS.find(option => option.value === langCode);
    // Fall back to just the lang code if not found
    return lang ? lang.nativeName : langCode;
  };

  return (
    <LanguageContext.Provider
      value={{
        targetLanguage,
        setTargetLanguage,
        uiLanguage,
        setUILanguage,
        useNativeLanguage,
        setUseNativeLanguage,
        getValidLanguageOptions,
        getLanguageLabel,
        getNativeLanguageName,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};
