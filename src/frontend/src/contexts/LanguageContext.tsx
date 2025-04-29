import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import Cookies from 'js-cookie';

// Language options for the entire application
export const LANGUAGE_OPTIONS = [
  { value: 'en', label: 'English' },
  { value: 'ko', label: 'Korean (한국어)' },
  { value: 'fr', label: 'Français' },
  { value: 'es', label: 'Español' },
  { value: 'de', label: 'Deutsch' },
  { value: 'ja', label: 'Japanese (日本語)' },
  { value: 'zh', label: 'Chinese (中文)' },
];

// Cookie names for storing preferences
const COOKIE_TARGET_LANG = 'langread_target_language';
const COOKIE_USE_NATIVE = 'langread_use_native_language';

// Define the shape of our language context
interface LanguageContextType {
  targetLanguage: string;
  setTargetLanguage: (lang: string) => void;
  useNativeLanguage: boolean;
  setUseNativeLanguage: (useNative: boolean) => void;
  getValidLanguageOptions: (currentLanguage?: string) => typeof LANGUAGE_OPTIONS;
}

// Create the context with default values
const LanguageContext = createContext<LanguageContextType>({
  targetLanguage: 'en',
  setTargetLanguage: () => {},
  useNativeLanguage: false,
  setUseNativeLanguage: () => {},
  getValidLanguageOptions: () => LANGUAGE_OPTIONS,
});

// Create a hook for using the language context
export const useLanguagePreferences = () => useContext(LanguageContext);

// Props for the provider component
interface LanguageProviderProps {
  children: ReactNode;
}

// Create the provider component
export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  // Initialize state from cookies if available
  const [targetLanguage, setTargetLanguageState] = useState<string>(() => {
    return Cookies.get(COOKIE_TARGET_LANG) || 'en';
  });
  
  const [useNativeLanguage, setUseNativeLanguageState] = useState<boolean>(() => {
    return Cookies.get(COOKIE_USE_NATIVE) === 'true';
  });

  // Update cookie whenever targetLanguage changes
  const setTargetLanguage = (lang: string) => {
    setTargetLanguageState(lang);
    Cookies.set(COOKIE_TARGET_LANG, lang, { expires: 30 });
  };

  // Update cookie whenever useNativeLanguage changes
  const setUseNativeLanguage = (useNative: boolean) => {
    setUseNativeLanguageState(useNative);
    Cookies.set(COOKIE_USE_NATIVE, useNative.toString(), { expires: 30 });
  };

  // Helper function to get language options excluding the current article language
  const getValidLanguageOptions = (currentLanguage?: string) => {
    if (!currentLanguage) return LANGUAGE_OPTIONS;
    
    return LANGUAGE_OPTIONS.filter(lang => lang.value !== currentLanguage);
  };

  return (
    <LanguageContext.Provider
      value={{
        targetLanguage,
        setTargetLanguage,
        useNativeLanguage,
        setUseNativeLanguage,
        getValidLanguageOptions,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};
