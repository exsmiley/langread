# Lingogi Internationalization (i18n) Guide

This guide explains how to work with translations in the Lingogi application, including how to use our tools for managing internationalization and ensuring text is properly translated.

## Table of Contents

- [Overview](#overview)
- [Translation Files](#translation-files)
- [Using Translations in Code](#using-translations-in-code)
- [Translation Tools](#translation-tools)
- [Running Tests](#running-tests)
- [Best Practices](#best-practices)

## Overview

Lingogi uses `react-i18next` for internationalization. All user-facing text should be internationalized to support multiple languages. Currently, we support:

- English (en)
- Korean (ko)

## Translation Files

Translation files are stored in JSON format at:

```
src/i18n/locales/[language-code]/translation.json
```

These files use a nested structure with dot notation for organizing translations by feature or section.

Example:
```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel"
  },
  "nav": {
    "home": "Home",
    "about": "About"
  }
}
```

## Using Translations in Code

Import the `useTranslation` hook and use the `t()` function:

```tsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('page.title')}</h1>
      <button>{t('common.save')}</button>
    </div>
  );
}
```

## Translation Tools

We have several tools to help manage translations:

### 1. Translation Checker

Identifies missing translation keys in all language files.

```bash
cd src/frontend
node scripts/translation-checker.js
```

### 2. Translation Updater

Generates updated translation files with placeholders for missing keys.

```bash
cd src/frontend
node scripts/translation-updater.js
```

### 3. Automatic Translator

Translates missing entries in a target language file from the source language.

```bash
cd src/frontend
node scripts/i18n-auto-translator.js --source en --target ko
```

Options:
- `--source <language>`: Source language code (default: 'en')
- `--target <language>`: Target language code (default: 'ko')
- `--backup`: Create backup of original file (default: true)
- `--no-backup`: Don't create backup
- `--dry-run`: Show translations without writing to file

### 4. Hardcoded Text Detector

Scans component files for text that should be internationalized but is currently hardcoded.

```bash
cd src/frontend
node scripts/hardcoded-text-detector.js [directory]
```

Example:
```bash
node scripts/hardcoded-text-detector.js src/pages
```

## Running Tests

We have automated tests to ensure all translations are complete and no text is hardcoded.

```bash
cd src/frontend
npm test -- -t "Translation Completeness"
```

This will run all translation-related tests:
- Verifies all translation keys used in code exist in all translation files
- Checks that all keys in English translation exist in other translation files
- Ensures no text is hardcoded in component files

## Best Practices

1. **Never hardcode text** - Always use the `t()` function for user-facing text
2. **Run tests before commits** - Make sure no translation issues are introduced
3. **Use meaningful keys** - Organize keys by feature/section for better maintainability
4. **Keep translations consistent** - Use the same terms across the application
5. **Check for missing translations** regularly

## Workflow for Adding New Features

1. Add new UI components using the `t()` function with appropriate keys
2. Run `node scripts/translation-updater.js` to generate updated translation files
3. Fill in translations for non-English languages
4. Run tests to verify all translations are complete
5. Commit changes

## Troubleshooting

- **Missing translation keys**: Run translation-checker.js to identify missing keys
- **Hardcoded text**: Run hardcoded-text-detector.js to find hardcoded text
- **Translation not showing**: Check that the key exists in all translation files
- **Wrong language displayed**: Check the language context and language switcher
