#!/usr/bin/env node

/**
 * Translation Updater Script
 * 
 * This script:
 * 1. Scans all TypeScript/TSX files for t() function calls
 * 2. Extracts all translation keys
 * 3. Checks if they exist in both English and Korean translation files
 * 4. Generates updated translation files with all missing keys added
 * 
 * Features:
 * - Identifies all translation keys used in the codebase
 * - Creates updated translation files with placeholders for missing keys
 * - Preserves existing translations
 * - Creates updated files (.updated.json) without modifying originals
 * 
 * Usage:
 *   node translation-updater.js
 * 
 * Related scripts:
 * - translation-checker.js: Reports missing translation keys without modifying files
 * - i18n-auto-translator.js: Translates missing entries using an LLM approach
 * 
 * When to use:
 * Use this script after adding new UI text or components to generate updated
 * translation files that include placeholders for all missing keys.
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

// Regular expressions to find t() function calls
// These patterns match different ways t() might be called in the code
const T_FUNCTION_PATTERNS = [
  /t\(['"`]([\w.-]+)['"`]\)/g,                          // t('key')
  /useTranslation\(\)\.t\(['"`]([\w.-]+)['"`]\)/g,      // useTranslation().t('key')
  /\{\s*t\(['"`]([\w.-]+)['"`]\)\s*\}/g,                // { t('key') }
  /t\(`([\w.-]+)`\)/g,                                  // t(`key`)
  /t\(['"`]([\w.-]+)['"`],\s*\{[^}]*\}\)/g              // t('key', { options })
];

// Additional patterns for specific AboutPage component translations
// Matches t('about.features.key.title') and similar patterns
const ADDITIONAL_PATTERNS = [
  /t\(['"`](about\.features\.[a-zA-Z]+\.title)['"`]\)/g,
  /t\(['"`](about\.features\.[a-zA-Z]+\.description)['"`]\)/g,
  /t\(['"`](about\.mascot\.[a-zA-Z]+)['"`]\)/g
];

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

// Helper function to get a value from a nested object using a dot-notation path
function getNestedValue(obj, path) {
  return path.split('.').reduce((o, key) => (o && o[key] !== undefined) ? o[key] : undefined, obj);
}

// Helper function to set a nested value in an object
function setNestedValue(obj, path, value) {
  const keys = path.split('.');
  let current = obj;
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!current[key] || typeof current[key] !== 'object') {
      current[key] = {};
    }
    current = current[key];
  }
  
  current[keys[keys.length - 1]] = value;
}

// Find all TypeScript/TSX files
const tsFiles = glob.sync(`${SRC_DIR}/**/*.{ts,tsx}`, {
  ignore: ['**/node_modules/**', '**/*.d.ts', '**/scripts/**']
});

console.log(`Found ${tsFiles.length} TypeScript files to scan`);

// Scan each file for translation keys
tsFiles.forEach(filePath => {
  try {
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const relativePath = path.relative(SRC_DIR, filePath);
    
    // Check all regex patterns for translation keys
    T_FUNCTION_PATTERNS.forEach(pattern => {
      let match;
      while ((match = pattern.exec(fileContent)) !== null) {
        const key = match[1];
        if (key && key.trim() && !key.includes('${')) { // Skip dynamic keys with template literals
          foundKeys.add(key);
        }
      }
    });
    
    // Check additional patterns for AboutPage specific translations
    if (filePath.includes('AboutPage')) {
      ADDITIONAL_PATTERNS.forEach(pattern => {
        let match;
        while ((match = pattern.exec(fileContent)) !== null) {
          const key = match[1];
          if (key && key.trim()) {
            foundKeys.add(key);
          }
        }
      });
    }
    
  } catch (error) {
    console.error(`Error scanning file ${filePath}:`, error.message);
  }
});

// Check which keys are missing in each translation file
foundKeys.forEach(key => {
  Object.keys(translations).forEach(locale => {
    if (!hasTranslationKey(translations[locale], key)) {
      missingKeys[locale].push({
        key,
        englishValue: getNestedValue(translations.en, key) || ''
      });
    }
  });
});

// Special handling for about.mascot section as seen in AboutPage.tsx
['about.mascot.title', 'about.mascot.alt', 'about.mascot.name', 'about.mascot.description'].forEach(key => {
  if (!foundKeys.has(key)) {
    foundKeys.add(key);
    
    Object.keys(translations).forEach(locale => {
      if (!hasTranslationKey(translations[locale], key)) {
        missingKeys[locale].push({
          key,
          englishValue: ''
        });
      }
    });
  }
});

// Special handling for about.features section
['about.features.quality.title', 'about.features.quality.description', 
 'about.features.innovation.title', 'about.features.innovation.description',
 'about.features.accessibility.title', 'about.features.accessibility.description',
 'about.features.comprehension.title', 'about.features.comprehension.description'].forEach(key => {
  if (!foundKeys.has(key)) {
    foundKeys.add(key);
    
    Object.keys(translations).forEach(locale => {
      if (!hasTranslationKey(translations[locale], key)) {
        missingKeys[locale].push({
          key,
          englishValue: ''
        });
      }
    });
  }
});

// Handle special case for common.and
if (!foundKeys.has('common.and')) {
  foundKeys.add('common.and');
  Object.keys(translations).forEach(locale => {
    if (!hasTranslationKey(translations[locale], 'common.and')) {
      missingKeys[locale].push({
        key: 'common.and',
        englishValue: 'and'
      });
    }
  });
}

// Print report
console.log(`\nTranslation Key Report`);
console.log(`=====================`);
console.log(`Total unique translation keys found: ${foundKeys.size}`);

Object.keys(translations).forEach(locale => {
  if (missingKeys[locale].length > 0) {
    console.log(`\n${locale.toUpperCase()}: Missing ${missingKeys[locale].length} translation keys`);
  } else {
    console.log(`\n${locale.toUpperCase()}: All translation keys are present! 🎉`);
  }
});

// Create updated translation files
Object.keys(translations).forEach(locale => {
  const updatedTranslation = { ...translations[locale] };
  
  missingKeys[locale].forEach(({ key, englishValue }) => {
    let value = '';
    
    if (locale === 'en') {
      // For English, use empty string or the key itself as a fallback
      value = englishValue || key.split('.').pop() || '';
    } else {
      // For Korean and other languages, indicate that translation is needed
      if (englishValue) {
        value = `[${locale.toUpperCase()}] ${englishValue}`;
      } else {
        value = `[${locale.toUpperCase()}] ${key.split('.').pop() || ''}`;
      }
    }
    
    setNestedValue(updatedTranslation, key, value);
  });
  
  // Write updated translation file
  const outputPath = path.resolve(__dirname, `../src/i18n/locales/${locale}/translation.updated.json`);
  fs.writeFileSync(outputPath, JSON.stringify(updatedTranslation, null, 2), 'utf8');
  
  console.log(`\nUpdated translation file for ${locale.toUpperCase()} created at:`);
  console.log(outputPath);
});

console.log('\nDone! 🚀');
console.log('\nNext steps:');
console.log('1. Review the .updated.json files');
console.log('2. Translate the missing keys in Korean');
console.log('3. Replace the original translation.json files with the updated ones');
