/**
 * Translation Completeness Tests
 * 
 * This test suite ensures that all text in the application is properly internationalized
 * and that all translation files are complete and consistent.
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Configuration
const SRC_DIR = path.resolve(__dirname, '../..');
const LOCALES_DIR = path.resolve(SRC_DIR, 'i18n/locales');
const LOCALE_FILES = {
  en: path.resolve(LOCALES_DIR, 'en/translation.json'),
  ko: path.resolve(LOCALES_DIR, 'ko/translation.json')
};

console.log('SRC_DIR:', SRC_DIR);
console.log('EN translation file path:', LOCALE_FILES.en);
console.log('KO translation file path:', LOCALE_FILES.ko);

// Regular expression to find t() function calls
// This pattern matches t('key'), t("key"), and t(`key`) formats
const T_FUNCTION_REGEX = /t\(['"`]([\w.-]+)['"`]\)/g;

// Regex patterns to detect hardcoded text - expanded from the original patterns
const HARDCODED_TEXT_PATTERNS = [
  // Text between tags like <Text>Hardcoded text</Text> - expanded element types
  /<(Text|Heading|Button|Link|Title|Label|Span|P|H1|H2|H3|H4|H5|H6|Box|Flex|Container|Card|ListItem|MenuItem|Option|Summary|TableCell|Th|Td)[^>]*>([^{<][A-Za-z0-9\s.,!?-]+[^}>])<\//g,
  
  // Text in string props like label="Hardcoded text" - expanded prop types
  /(title|label|placeholder|aria-label|alt|buttonText|tooltipLabel|description|value|content|name|header|footer|tooltip|message|caption|fallback)=["']([A-Za-z0-9\s.,!?-]+)["']/g,
  
  // Text in template strings in JSX props - expanded prop types
  /(title|label|placeholder|aria-label|alt|description|content|message|tooltip|caption)={[^}]*`([A-Za-z0-9\s.,!?-]+)`[^}]*}/g,
  
  // Text in curly braces like {'Some text'} or {"Some text"}
  /{\s*['"]([A-Za-z0-9\s.,!?-]+)['"]\s*}/g,
  
  // Variable assignments with hardcoded UI text
  /(?:const|let|var)\s+\w+\s*=\s*['"]([A-Za-z0-9\s.,!?-]+)['"];/g,
  
  // Dashboard metrics and descriptions - specific to our recent issue
  /(value|description)="([A-Za-z0-9\s.,!?-]+)"/g,
  
  // Special component props like in StatCard
  /<\w+Card\s+[^>]*description=["']([A-Za-z0-9\s.,!?-]+)["'][^>]*>/g
];


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

// Words that suggest the text is likely UI content that should be translated
const UI_TEXT_INDICATORS = [
  // UI Actions
  'submit', 'save', 'cancel', 'delete', 'edit', 'view', 'search', 'filter', 'clear',
  'add', 'remove', 'update', 'create', 'modify', 'browse', 'explore', 'find',
  
  // Navigation & UI Elements
  'welcome', 'login', 'logout', 'signup', 'signin', 'profile', 'settings', 'home',
  'menu', 'dashboard', 'page', 'section', 'panel', 'tab', 'button', 'link',
  'sidebar', 'header', 'footer', 'navigation', 'articles', 'list', 'table',
  
  // Form Elements
  'password', 'email', 'username', 'name', 'address', 'phone', 'input', 'field',
  'required', 'optional', 'form', 'checkbox', 'radio', 'dropdown', 'select',
  
  // Status & Feedback
  'error', 'success', 'warning', 'info', 'loading', 'processing', 'complete',
  'failed', 'retry', 'pending', 'progress', 'status', 'notification',
  
  // Instructions
  'please', 'click', 'select', 'choose', 'enter', 'type', 'provide', 'confirm',
  'review', 'check', 'verify', 'read', 'write', 'follow', 'try', 'learn',
  
  // Time & Date
  'today', 'yesterday', 'tomorrow', 'day', 'week', 'month', 'year', 'date', 'time',
  'morning', 'afternoon', 'evening', 'schedule', 'calendar', 'appointment',
  
  // Metrics & Statistics
  'total', 'count', 'average', 'summary', 'statistics', 'metrics', 'progress',
  'score', 'level', 'rank', 'rating', 'performance', 'activity', 'session',
  
  // Content Types
  'message', 'comment', 'post', 'article', 'news', 'blog', 'story', 'title',
  'description', 'content', 'text', 'summary', 'detail', 'information',
  
  // Domain-Specific (Lingogi/Language Learning)
  'language', 'translation', 'word', 'sentence', 'vocabulary', 'grammar', 'study',
  'practice', 'learn', 'read', 'write', 'speak', 'listen', 'flashcard', 'quiz',
  'beginner', 'intermediate', 'advanced', 'native', 'target', 'foreign'
];

// Helper function to check if text is likely to need translation
function shouldTranslate(text) {
  const trimmedText = text.trim();
  
  // If text is empty or just whitespace, skip it
  if (!trimmedText) return false;
  
  // If text is very short, it might not need translation (but check for UI words first)
  if (trimmedText.length < 2) {
    // Check if it's a single UI word before skipping
    for (const indicator of UI_TEXT_INDICATORS) {
      if (trimmedText.toLowerCase() === indicator.toLowerCase()) return true;
    }
    return false;
  }
  
  // Skip if text is ONLY uppercase or a constant-like name
  if (/^[A-Z_0-9]+$/.test(trimmedText)) return false;
  
  // Skip if it's a URL, path, or file reference
  if (trimmedText.includes('http') || (/\.\w{2,4}$/.test(trimmedText)) || 
      (trimmedText.includes('/') && !trimmedText.match(/\s\/\s/))) return false;
  
  // Skip if it looks like a variable, function, or component name (camelCase/PascalCase with no spaces)
  if (/^[A-Z][a-zA-Z0-9]*$/.test(trimmedText) && !trimmedText.includes(' ')) return false;
  
  // Skip if it looks like a prop name
  if (/^\{[a-zA-Z0-9_.]+\}$/.test(trimmedText)) return false;
  
  // Skip CSS-related content
  if (trimmedText.startsWith('#') && /^#[0-9a-fA-F]{3,8}$/.test(trimmedText)) return false;
  if (/^\d+(\.\d+)?(px|em|rem|vh|vw|%)$/.test(trimmedText)) return false;
  
  // Skip numbers and simple punctuation
  if (/^\d+(\.\d+)?$/.test(trimmedText)) return false;
  if (/^[!@#$%^&*()_\-+=<>?.\/;:"']+$/.test(trimmedText)) return false;
  
  // If it contains UI text indicators, it likely needs translation
  for (const indicator of UI_TEXT_INDICATORS) {
    if (trimmedText.toLowerCase().includes(indicator.toLowerCase())) return true;
  }
  
  // Special case for dashboard metrics and descriptions we missed
  if (trimmedText.includes('Read') || 
      trimmedText.includes('Words') || 
      trimmedText.includes('Sessions') ||
      trimmedText.includes('track progress') ||
      trimmedText.includes('collection') ||
      trimmedText.includes('completed')) return true;
  
  // Consider capitalalized words that aren't at the beginning of a sentence as proper nouns
  const wordsInMiddle = trimmedText.split(' ').slice(1);
  const hasProperNoun = wordsInMiddle.some(word => word.length > 1 && /^[A-Z][a-z]+$/.test(word));
  
  // If it has multiple words or ends with punctuation, it's likely a phrase that needs translation
  const hasMultipleWords = trimmedText.includes(' ');
  const endsWithPunctuation = /[.!?]$/.test(trimmedText);
  const startsWithCapital = /^[A-Z]/.test(trimmedText);
  
  // Return true if it looks like a sentence or phrase
  return hasMultipleWords || endsWithPunctuation || (startsWithCapital && trimmedText.length > 3);
}

describe('Translation Completeness Tests', () => {
  // Load translation files once before all tests
  let translations = {};
  
  beforeAll(() => {
    Object.entries(LOCALE_FILES).forEach(([locale, filePath]) => {
      try {
        const fileContent = fs.readFileSync(filePath, 'utf8');
        translations[locale] = JSON.parse(fileContent);
      } catch (error) {
        throw new Error(`Error loading ${locale} translation file: ${error.message}`);
      }
    });
  });
  
  // Test that all translation keys used in the code exist in all translation files
  test('All translation keys used in code exist in all translation files', () => {
    // Find all TypeScript/TSX files
    const tsFiles = glob.sync(`${SRC_DIR}/**/*.{ts,tsx}`, {
      ignore: ['**/node_modules/**', '**/*.d.ts', '**/tests/**']
    });
    
    // Store all translation keys found in TypeScript files
    const foundKeys = new Set();
    
    // Scan each file for translation keys
    tsFiles.forEach(filePath => {
      try {
        const fileContent = fs.readFileSync(filePath, 'utf8');
        const relativePath = path.relative(SRC_DIR, filePath);
        let match;
        
        // Find all t() function calls in the file
        while ((match = T_FUNCTION_REGEX.exec(fileContent)) !== null) {
          const key = match[1];
          if (key && key.trim()) {
            foundKeys.add(key);
          }
        }
      } catch (error) {
        throw new Error(`Error scanning file ${filePath}: ${error.message}`);
      }
    });
    
    // Check each key in each translation file
    const missingKeys = {
      en: [],
      ko: []
    };
    
    foundKeys.forEach(key => {
      Object.keys(translations).forEach(locale => {
        if (!hasTranslationKey(translations[locale], key)) {
          missingKeys[locale].push(key);
        }
      });
    });
    
    // Generate error message for missing keys
    Object.entries(missingKeys).forEach(([locale, keys]) => {
      if (keys.length > 0) {
        const missingKeysMessage = `Missing ${keys.length} keys in ${locale} translation:\n${keys.join('\n')}`;
        expect(keys.length).toBe(0, missingKeysMessage);
      }
    });
  });
  
  // Test that all keys in English translation file exist in all other translation files
  test('All keys in English translation exist in other translation files', () => {
    // Get all keys from English translation
    function getAllKeys(obj, prefix = '') {
      let keys = [];
      for (const key in obj) {
        const newKey = prefix ? `${prefix}.${key}` : key;
        if (typeof obj[key] === 'object' && obj[key] !== null) {
          keys = keys.concat(getAllKeys(obj[key], newKey));
        } else {
          keys.push(newKey);
        }
      }
      return keys;
    }
    
    const englishKeys = getAllKeys(translations.en);
    
    // Check each key in other translation files
    Object.entries(translations).forEach(([locale, translation]) => {
      if (locale === 'en') return; // Skip English
      
      const missingKeys = [];
      englishKeys.forEach(key => {
        if (!hasTranslationKey(translation, key)) {
          missingKeys.push(key);
        }
      });
      
      // Generate error message for missing keys
      if (missingKeys.length > 0) {
        const missingKeysMessage = `Missing ${missingKeys.length} keys in ${locale} translation:\n${missingKeys.join('\n')}`;
        expect(missingKeys.length).toBe(0, missingKeysMessage);
      }
    });
  });
  
  // Test that no text is hardcoded in component files
  test('No hardcoded text in component files', () => {
    // Common exceptions that shouldn't be flagged
    const EXCEPTIONS = [
      /className=/g,
      /style=/g,
      /console\./g,
      /import /g,
      /export /g,
      /const /g,
      /let /g,
      /function /g,
      /return /g,
      /props\./g,
      /\.(js|ts|jsx|tsx)/g,
      /\{t\(['"`]/g,
      /\{\s*t\(\s*['"`]/g,
    ];
    
    // Find all component files
    const componentFiles = glob.sync(`${SRC_DIR}/**/*.{tsx,jsx}`, {
      ignore: ['**/node_modules/**', '**/tests/**']
    });
    
    const hardcodedTextIssues = [];
    
    // Scan each file for hardcoded text
    componentFiles.forEach(filePath => {
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        const relativePath = path.relative(SRC_DIR, filePath);
        
        // Skip files that are not component files
        if (
          !filePath.includes('Page') && 
          !filePath.includes('Component') && 
          !filePath.toLowerCase().includes('card') &&
          !filePath.toLowerCase().includes('modal')
        ) {
          return;
        }
        
        // Scan for hardcoded text patterns
        for (const pattern of HARDCODED_TEXT_PATTERNS) {
          let match;
          while ((match = pattern.exec(content)) !== null) {
            // The text is in the second capture group for all our patterns
            const text = match[2];
            
            if (text && shouldTranslate(text)) {
              // Find the line number
              const upToMatch = content.substring(0, match.index);
              const lineNumber = upToMatch.split('\n').length;
              
              hardcodedTextIssues.push({
                file: relativePath,
                line: lineNumber,
                text: text
              });
            }
          }
        }
      } catch (error) {
        throw new Error(`Error scanning file ${filePath}: ${error.message}`);
      }
    });
    
    // Generate error message for hardcoded text
    if (hardcodedTextIssues.length > 0) {
      let message = `Found ${hardcodedTextIssues.length} instances of hardcoded text:\n`;
      hardcodedTextIssues.forEach(issue => {
        message += `${issue.file} (line ${issue.line}): "${issue.text}"\n`;
      });
      expect(hardcodedTextIssues.length).toBe(0, message);
    }
  });
});
