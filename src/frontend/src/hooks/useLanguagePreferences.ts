import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface LanguagePreferencesHook {
  targetLanguage: string;
  difficulty: string;
  setTargetLanguage: (language: string) => void;
  setDifficulty: (difficulty: string) => void;
}

/**
 * Custom hook to manage language preferences with the following priority:
 * 1. User's local preferences (stored in localStorage)
 * 2. URL parameters (if provided)
 * 3. User settings from AuthContext
 * 
 * Changes made by the user on the article page are persisted to localStorage
 * but don't affect the user's profile settings.
 */
export function useLanguagePreferences(
  urlTargetLanguage: string | null, 
  urlDifficulty: string | null
): LanguagePreferencesHook {
  const { user } = useAuth();

  // Helper function to get user's default target language
  const getUserDefaultTargetLanguage = useCallback((): string => {
    // Check if user has multiple languages with a default marked
    if (user?.additional_languages && Array.isArray(user.additional_languages)) {
      const defaultLang = user.additional_languages.find(lang => lang.isDefault);
      if (defaultLang) {
        return defaultLang.language;
      }
    }
    
    // Fall back to the primary learning language
    if (user?.learning_language) {
      return user.learning_language;
    }
    
    // Last resort default to Korean
    return 'ko';
  }, [user]);

  // Initialize target language with priority order
  const [targetLanguage, setTargetLanguageState] = useState(() => {
    // 1. Check localStorage first
    const storedTargetLang = localStorage.getItem('lingogi_article_target_language');
    if (storedTargetLang) {
      return storedTargetLang;
    }

    // 2. Check URL parameters
    if (urlTargetLanguage) {
      return urlTargetLanguage;
    }
    
    // 3. Use user's default language
    return getUserDefaultTargetLanguage();
  });

  // Initialize difficulty with priority order
  const [difficulty, setDifficultyState] = useState(() => {
    // 1. Check localStorage first
    const storedDifficulty = localStorage.getItem('lingogi_article_difficulty');
    if (storedDifficulty) {
      return storedDifficulty;
    }

    // 2. Check URL parameters
    if (urlDifficulty) {
      return urlDifficulty;
    }

    // 3. Use user's proficiency or default to intermediate
    return user?.proficiency || 'intermediate';
  });

  // Update when user changes (e.g., after login) if no local preferences exist
  useEffect(() => {
    if (user) {
      // Update target language if not set locally
      const storedTargetLang = localStorage.getItem('lingogi_article_target_language');
      if (!storedTargetLang) {
        setTargetLanguageState(getUserDefaultTargetLanguage());
      }

      // Update difficulty if not set locally
      const storedDifficulty = localStorage.getItem('lingogi_article_difficulty');
      if (!storedDifficulty && user.proficiency) {
        setDifficultyState(user.proficiency);
      }
    }
  }, [user, getUserDefaultTargetLanguage]);

  // Wrappers for setters that also update localStorage
  const setTargetLanguage = useCallback((language: string) => {
    setTargetLanguageState(language);
    localStorage.setItem('lingogi_article_target_language', language);
  }, []);

  const setDifficulty = useCallback((diff: string) => {
    setDifficultyState(diff);
    localStorage.setItem('lingogi_article_difficulty', diff);
  }, []);

  return {
    targetLanguage,
    difficulty,
    setTargetLanguage,
    setDifficulty
  };
}
