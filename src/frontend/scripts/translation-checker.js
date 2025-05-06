#!/usr/bin/env node

/**
 * Translation Checker Script
 * 
 * This script scans all TypeScript/TSX files in the project,
 * extracts translation keys used with t() function,
 * and verifies they exist in all translation files.
 * 
 * Features:
 * - Identifies all translation keys used in the codebase
 * - Checks if keys exist in each language's translation file
 * - Reports missing translations for each language
 * - Generates a template for adding missing keys
 * 
 * Usage:
 *   node translation-checker.js
 * 
 * Related scripts:
 * - translation-updater.js: Generates updated translation files with placeholders
 * - i18n-auto-translator.js: Translates missing entries using an LLM approach
 * 
 * When to use:
 * Use this script during development to identify missing translations,
 * especially after adding new UI text or components.
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Configuration
const SRC_DIR = path.resolve(__dirname, '../src');
const LOCALES_DIR = path.resolve(SRC_DIR, 'i18n/locales');
const LOCALE_FILES = {
  en: path.resolve(LOCALES_DIR, 'en/translation.json'),
  ko: path.resolve(LOCALES_DIR, 'ko/translation.json')
};

// Regular expression to find t() function calls
// This pattern matches t('key'), t("key"), and t(`key`) formats
const T_FUNCTION_REGEX = /t\(['"`]([\w.-]+)['"`]\)/g;

// Store all translation keys found in TypeScript files
const foundKeys = new Set();

// Store missing keys for each locale
const missingKeys = {
  en: [],
  ko: []
};

// Load translation files
const translations = {};
Object.entries(LOCALE_FILES).forEach(([locale, filePath]) => {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    translations[locale] = JSON.parse(fileContent);
  } catch (error) {
    console.error(`Error loading ${locale} translation file:`, error.message);
    process.exit(1);
  }
});

// Helper function to check if a key exists in a translation object
function hasTranslationKey(obj, keyPath) {
  const parts = keyPath.split('.');
  let current = obj;
  
  for (const part of parts) {
    if (current === undefined || current === null || typeof current !== 'object') {
      return false;
    }
    current = current[part];
  }
  
  return current !== undefined;
}

// Find all TypeScript/TSX files
const tsFiles = glob.sync(`${SRC_DIR}/**/*.{ts,tsx}`, {
  ignore: ['**/node_modules/**', '**/*.d.ts']
});

console.log(`Found ${tsFiles.length} TypeScript files to scan`);

// Scan each file for translation keys
tsFiles.forEach(filePath => {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const relativePath = path.relative(SRC_DIR, filePath);
    let match;
    
    // Find all t() function calls in the file
    while ((match = T_FUNCTION_REGEX.exec(fileContent)) !== null) {
      const key = match[1];
      foundKeys.add(key);
      
      // Check if key exists in each translation file
      Object.keys(translations).forEach(locale => {
        if (!hasTranslationKey(translations[locale], key)) {
          missingKeys[locale].push({
            key,
            file: relativePath
          });
        }
      });
    }
  } catch (error) {
    console.error(`Error scanning file ${filePath}:`, error.message);
  }
});

// Print report
console.log(`\nTranslation Key Report`);
console.log(`=====================`);
console.log(`Total unique translation keys found: ${foundKeys.size}`);

Object.keys(translations).forEach(locale => {
  const localeKeys = Object.keys(missingKeys[locale]).length;
  if (missingKeys[locale].length > 0) {
    console.log(`\n${locale.toUpperCase()}: Missing ${missingKeys[locale].length} translation keys:`);
    missingKeys[locale].forEach(({ key, file }) => {
      console.log(`  - ${key} (used in ${file})`);
    });
  } else {
    console.log(`\n${locale.toUpperCase()}: All translation keys are present! 🎉`);
  }
});

// Generate a template for missing Korean translations
if (missingKeys.ko.length > 0) {
  console.log('\nTemplate for adding missing Korean translations:');
  console.log('----------------------------------------');
  
  const missingKeysTemplate = {};
  
  missingKeys.ko.forEach(({ key }) => {
    const parts = key.split('.');
    let current = missingKeysTemplate;
    
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (!current[part]) {
        current[part] = {};
      }
      current = current[part];
    }
    
    const lastPart = parts[parts.length - 1];
    // Get the English translation as reference
    let englishValue = '';
    
    try {
      let englishCurrent = translations.en;
      for (const part of parts) {
        englishCurrent = englishCurrent[part];
      }
      englishValue = englishCurrent || '';
    } catch (e) {
      englishValue = '';
    }
    
    current[lastPart] = `[Korean translation needed for: "${englishValue}"]`;
  });
  
  console.log(JSON.stringify(missingKeysTemplate, null, 2));
}

console.log('\nDone! 🚀');
