#!/usr/bin/env node

/**
 * Hardcoded Text Detector
 * 
 * This script scans React component files for text that should be internationalized
 * but is currently hardcoded in the JSX/TSX.
 * 
 * Features:
 * - Detects text in JSX elements that should be translated
 * - Ignores common exceptions (variables, imports, code comments)
 * - Reports file paths and line numbers of potential issues
 * - Suggests ways to fix each issue with t() function
 * 
 * Usage:
 *   node hardcoded-text-detector.js [directory]
 * 
 * Example:
 *   node hardcoded-text-detector.js ../src/pages
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

// Configuration
const DEFAULT_DIR = path.resolve(__dirname, '../src');
const INPUT_DIR = process.argv[2] ? path.resolve(process.argv[2]) : DEFAULT_DIR;
const EXTENSIONS = ['.tsx', '.jsx', '.js', '.ts'];

// Important directories to always check, regardless of input
const IMPORTANT_DIRS = [
  path.resolve(__dirname, '../src/components'),
  path.resolve(__dirname, '../src/layouts'),
  path.resolve(__dirname, '../src/pages')
];

// Regex patterns to detect hardcoded text
const HARDCODED_TEXT_PATTERNS = [
  // Text between tags like <Text>Hardcoded text</Text> - expanded element types
  /<(Text|Heading|Button|Link|Title|Label|Span|P|H1|H2|H3|H4|H5|H6|Box|Flex|Container|Card|ListItem|MenuItem|Option|Summary|TableCell|Th|Td)[^>]*>([^{<][A-Za-z0-9\s.,!?-]+[^}>])<\//g,
  
  // Text in props likely to contain user-visible content
  /(title|label|placeholder|aria-label|alt|buttonText|tooltipLabel|description|content|header|footer|tooltip|message|caption|fallback)=["']([A-Za-z0-9\s.,!?-]+)["']/g,
  
  // Text in template strings in JSX props
  /(title|label|placeholder|aria-label|alt|description|content|message|tooltip|caption)={[^}]*`([A-Za-z0-9\s.,!?-]+)`[^}]*}/g,
  
  // Text in curly braces like {'Some text'} or {"Some text"}
  /{\s*['"]([A-Za-z0-9\s.,!?-]+)['"]\s*}/g,
  
  // Variable assignments with hardcoded UI text
  /(?:const|let|var)\s+\w+\s*=\s*['"]([A-Za-z0-9\s.,!?-]+)['"];/g,
  
  // Hardcoded strings in JSX returned from components
  /return\s*\(\s*['"]([A-Za-z0-9\s.,!?-]+)['"]\s*\)/g,
  
  // Hardcoded strings in render methods
  /render\s*\(\s*\)\s*{[^}]*['"]([A-Za-z0-9\s.,!?-]+)['"][^}]*}/g
];

// Words that suggest the text is likely UI content that should be translated
const UI_TEXT_INDICATORS = [
  // UI Actions
  'submit', 'save', 'cancel', 'delete', 'edit', 'view', 'search', 'filter', 'clear',
  'add', 'remove', 'update', 'create', 'modify', 'browse', 'explore', 'find',
  'copyright', 'reserved', 'rights', 'all rights', 'reserved', 'privacy', 'policy', 'terms', 'service',
  'contact', 'about', 'us', 'footer', 'header', 'menu',
  
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

// Common exceptions that shouldn't be flagged
const EXCEPTIONS = [
  // CSS classes and style properties
  /className=/g,
  /style=/g,
  
  // Technical terms/props that don't need translation
  /console\./g,
  /import /g,
  /export /g,
  /const /g,
  /let /g,
  /function /g,
  /return /g,
  /props\./g,
  /\.(js|ts|jsx|tsx)/g,
  
  // Already using t() function
  /\{t\(['"`]/g,
  /\{\s*t\(\s*['"`]/g,
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
  
  // Skip common UI style values that don't need translation
  const uiStyleValues = ['center', 'left', 'right', 'top', 'bottom', 'flex', 'grid', 'block', 'none', 
                         'row', 'column', 'wrap', 'nowrap', 'auto', 'fixed', 'absolute', 'relative',
                         'hidden', 'visible', 'scroll', 'link', 'outline', 'solid', 'dashed', 'dotted'];
  if (uiStyleValues.includes(trimmedText.toLowerCase())) return false;
  
  // Skip form field name attribute values that aren't visible to users
  const formFieldAttributes = ['name', 'id', 'type', 'method', 'action', 'encType', 'autoComplete', 
                               'target', 'rel', 'role', 'tabIndex', 'maxLength', 'minLength', 'step'];
  // Check if text is inside a form field attribute context (heuristic check)
  const isFormAttributeContext = (text.startsWith('name=') || text.includes(' name=') || 
                                text.startsWith('id=') || text.includes(' id='));
  if (isFormAttributeContext && formFieldAttributes.some(attr => trimmedText.startsWith(attr))) return false;
  
  // Skip code fragments that are unlikely to be user-facing text
  if (trimmedText.includes('==') || trimmedText.includes('===') || 
      trimmedText.includes('&&') || trimmedText.includes('||') ||
      /^[a-z]+\([^)]*\)$/.test(trimmedText) || // function calls
      trimmedText.startsWith('return ') || 
      trimmedText.includes('=>') || 
      /^set[A-Z]/.test(trimmedText)) return false; // setState functions
  
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

// Function to scan a file for hardcoded text
function scanFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  let issues = [];
  
  // Check if this is a component file that likely contains UI text
  const isLikelyComponentFile = (
    // File extensions for React components
    filePath.endsWith('.tsx') || 
    filePath.endsWith('.jsx') || 
    
    // Common naming patterns for React components
    filePath.includes('Page') || 
    filePath.includes('Component') ||
    filePath.includes('Card') ||
    filePath.includes('Modal') ||
    filePath.includes('Panel') ||
    filePath.includes('List') ||
    filePath.includes('Item') ||
    filePath.includes('View') ||
    filePath.includes('Bar') ||
    filePath.includes('Section') ||
    filePath.includes('Footer') ||
    filePath.includes('Header') ||
    filePath.includes('Nav') ||
    filePath.includes('Menu') ||
    filePath.includes('Button') ||
    
    // Common React imports and patterns
    content.includes('import React') ||
    content.includes('from \'react\'') ||
    content.includes('useState') ||
    content.includes('useEffect') ||
    
    // JSX indicators
    content.includes('return (') ||
    content.includes('=>') && content.includes('return') ||
    content.includes('className=') ||
    content.includes('style=') ||
    
    // HTML-like elements that might contain text
    content.includes('<div') ||
    content.includes('<span') ||
    content.includes('<p') ||
    content.includes('<h') ||
    content.includes('<a') ||
    content.includes('<button') ||
    content.includes('<Link') ||
    content.includes('<Text') ||
    content.includes('<label') ||
    content.includes('<title')
  );
  
  // Skip files that are clearly not UI components
  const isDefinitelyNotUIFile = (
    // Test files
    filePath.includes('.test.') ||
    filePath.includes('.spec.') ||
    filePath.includes('__tests__') ||
    
    // Configuration and utility files
    filePath.includes('config') ||
    filePath.includes('utils/') ||
    filePath.includes('types.') ||
    filePath.includes('.d.ts') ||
    
    // Files with no UI text indicators
    !content.includes('<') &&
    !content.includes('return') &&
    !content.includes('"') && 
    !content.includes("'")
  );
  
  // Skip files that are definitely not UI components
  if (isDefinitelyNotUIFile) {
    return [];
  }
  
  // Always check likely UI component files
  // But also don't skip other files that might contain text - just be less strict
  
  // Common component patterns that might contain dashboard metrics and descriptions
  const componentPatterns = [
    // Custom card or metric components with descriptions
    /<(Card|Box|Flex|Container|Stat|Metric)[^>]*>[\s\S]*?<\/(Card|Box|Flex|Container|Stat|Metric)>/g,
    
    // Table cells that might contain UI text
    /<(Td|TableCell)[^>]*>([^{<][A-Za-z0-9\s.,!?-]+[^}>])<\/(Td|TableCell)>/g,
    
    // List items that might contain UI text
    /<(ListItem|MenuItem)[^>]*>([^{<][A-Za-z0-9\s.,!?-]+[^}>])<\/(ListItem|MenuItem)>/g,
    
    // Headers or descriptions that might contain UI text
    /<(Heading|Text|Title)[^>]*>([^{<][A-Za-z0-9\s.,!?-]+[^}>])<\/(Heading|Text|Title)>/g,
  ];
  
  // Known false positives to ignore (components, attributes, etc. that don't need translation)
  const knownFalsePositives = [
    // UI/CSS property values
    'center', 'left', 'right', 'top', 'bottom', 'link', 'solid', 'dashed', 'flex', 'row', 'column',
    'auto', 'hidden', 'visible', 'block', 'inline', 'grid', 'fixed', 'relative', 'absolute',
    
    // Form attributes and internal props 
    'name="email"', 'name="password"', 'name="confirmPassword"', 'name="learningLanguage"',
    'name="name"', 'name="agreeToTerms"',
    
    // Code fragments often flagged incorrectly
    'setSelectedTags([]);', 'setSelectedArticle(',
    
    // t() function calls already internationalized but flagged due to formatting
    't("navigation.signIn")', 't("navigation.signUp")', 
    't("admin.clearCache")', 't("admin.checkStatus")', 't("admin.clearAllCache")',
    't("admin.tagName")', 't("admin.language")', 't("admin.translations")',
    't("admin.articles")', 't("admin.status")', 't("admin.delete")',
    't("articles.search")', 't("articles.readMore")',
    't("reading.addedToVocabulary")', 't("articles.viewArticle")',
    't("contact.form.sendButton")', 't("settings.saveSettings")',
    't("auth.sendResetLink")', 't("home.findArticles")',
    't("nav.vocabulary")', 't("profile.signOut")', 't("profile.changePassword")',
    't("profile.deleteAccount")', 't("auth.resetPassword")',
    't("settings.makeDefault")', 't("settings.remove")', 't("settings.saveChanges")',
    't("common.cancel")', 't("settings.addLanguage")', 't("settings.testBackendConnection")',
    't("auth.signIn")', 't("auth.createAccount")', 't("vocabulary.studySessionStarted")',
    't("components.errorBoundary.backToHome")'
  ];
  
  // First check for specialized component patterns
  for (const pattern of componentPatterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      // The captured text might be in different group positions depending on the pattern
      const text = match[2] || match[3] || '';
      
      if (text && shouldTranslate(text)) {
        // Skip known false positives
        if (knownFalsePositives.some(fp => text.trim() === fp || text.includes(fp))) {
          continue;
        }
        
        const upToMatch = content.substring(0, match.index);
        const lineNumber = upToMatch.split('\n').length;
        const lineContent = lines[lineNumber - 1];
        
        const suggestedKey = text
          .toLowerCase()
          .replace(/[^a-z0-9 ]/g, '')
          .replace(/\s+/g, '.');
        
        issues.push({
          file: filePath,
          line: lineNumber,
          content: lineContent.trim(),
          text: text,
          suggestion: `t('${suggestedKey}')`,
          type: 'component_pattern'
        });
      }
    }
  }
  
  // Then scan for our general hardcoded text patterns
  for (const pattern of HARDCODED_TEXT_PATTERNS) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      // The text is in the second capture group for most of our patterns
      const text = match[2] || match[1] || '';
      
      if (text && shouldTranslate(text)) {
        // Find the line number
        const upToMatch = content.substring(0, match.index);
        const lineNumber = upToMatch.split('\n').length;
        
        // Get the line content
        const lineContent = lines[lineNumber - 1];
        
        // Check if this line already has a t() function to avoid false positives
        if (lineContent.includes('t(') && lineContent.includes(text)) {
          continue;
        }
        
        // Generate a reasonable translation key from the text
        const suggestedKey = text
          .toLowerCase()
          .replace(/[^a-z0-9 ]/g, '')
          .replace(/\s+/g, '.');
        
        // Different suggestions based on context
        let suggestionType = 'unknown';
        let suggestedFix = '';
        
        if (match[0].includes('=')) {
          // Handle prop values
          suggestionType = 'prop';
          const propName = match[1] || 'prop';
          suggestedFix = `${propName}={t('${suggestedKey}')}`;
        } else if (match[0].match(/<\w+[^>]*>/)) {
          // Handle text content in JSX tags
          suggestionType = 'jsx_content';
          const tag = match[1] || 'span';
          suggestedFix = `<${tag}>{t('${suggestedKey}')}</${tag}>`;
        } else {
          // Handle other cases like variable assignments
          suggestionType = 'general';
          suggestedFix = `t('${suggestedKey}')`;
        }
        
        issues.push({
          file: filePath,
          line: lineNumber,
          content: lineContent.trim(),
          text: text,
          suggestion: suggestedFix,
          type: suggestionType
        });
      }
    }
  }
  
  return issues;
}

// Main function
function main() {
  console.log(`\n🔍 Scanning for hardcoded text in: ${INPUT_DIR}`);
  
  let files = [];
  let additionalFiles = [];
  
  // Check if input is a directory or a specific file
  const stats = fs.statSync(INPUT_DIR);
  
  if (stats.isDirectory()) {
    // If it's a directory, use glob to find all relevant files
    const globPattern = `${INPUT_DIR}/**/*{${EXTENSIONS.join(',')}}`;  
    files = glob.sync(globPattern, { ignore: '**/node_modules/**' });
  
    // Check if we're not already scanning the entire src directory
    const isFullScan = INPUT_DIR === DEFAULT_DIR;
    
    // If not doing a full scan, also check important directories
    if (!isFullScan) {
      // Make sure we always check important directories like components
      for (const dir of IMPORTANT_DIRS) {
        if (!INPUT_DIR.includes(dir)) {
          const additionalGlobPattern = `${dir}/**/*{${EXTENSIONS.join(',')}}`;  
          const dirFiles = glob.sync(additionalGlobPattern, { ignore: '**/node_modules/**' });
          additionalFiles = [...additionalFiles, ...dirFiles];
        }
      }
      
      // Remove duplicates by converting to Set and back to array
      additionalFiles = additionalFiles.filter(file => !files.includes(file));
      
      if (additionalFiles.length > 0) {
        console.log(`Additionally checking ${additionalFiles.length} files from important directories`);
        files = [...files, ...additionalFiles];
      }
    }
  } else if (stats.isFile()) {
    // If it's a direct file path, check if it has a valid extension
    const ext = path.extname(INPUT_DIR);
    if (EXTENSIONS.includes(ext)) {
      files = [INPUT_DIR];
    }
  }
  
  console.log(`Found ${files.length} files to scan\n`);
  
  // Scan each file
  let allIssues = [];
  files.forEach(file => {
    const issues = scanFile(file);
    allIssues = allIssues.concat(issues);
  });
  
  // Print report
  if (allIssues.length === 0) {
    console.log('✅ No hardcoded text found! All text appears to be properly internationalized.');
  } else {
    console.log(`⚠️ Found ${allIssues.length} instances of potentially hardcoded text:\n`);
    
    // Group issues by file
    const issuesByFile = {};
    allIssues.forEach(issue => {
      const relativePath = path.relative(process.cwd(), issue.file);
      if (!issuesByFile[relativePath]) {
        issuesByFile[relativePath] = [];
      }
      issuesByFile[relativePath].push(issue);
    });
    
    // Print issues by file
    Object.keys(issuesByFile).forEach(file => {
      console.log(`\n📄 ${file}:`);
      issuesByFile[file].forEach(issue => {
        console.log(`  Line ${issue.line}: "${issue.text}"`);
        console.log(`  Suggestion: ${issue.suggestion}\n`);
      });
    });
    
    console.log(`\nConsider using the t() function from 'react-i18next' for these texts.`);
    console.log(`Example: import { useTranslation } from 'react-i18next';\nconst { t } = useTranslation();\n`);
  }
}

// Run the script
main();
