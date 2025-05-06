#!/usr/bin/env node

/**
 * Korean Translation Improver Script
 * 
 * This script improves Korean translations by:
 * 1. Finding all entries marked with [자동번역] in the Korean translation file
 * 2. Using OpenAI's API to generate proper Korean translations
 * 3. Updating the translation file with improved translations
 * 
 * Usage:
 *   node improve-korean-translations.js
 */

const fs = require('fs');
const path = require('path');
const { OpenAI } = require('openai');
const readline = require('readline');

// Configuration
const CONFIG = {
  localesDir: path.resolve(__dirname, '../src/i18n/locales'),
  koFile: path.resolve(__dirname, '../src/i18n/locales/ko/translation.json'),
  enFile: path.resolve(__dirname, '../src/i18n/locales/en/translation.json'),
  createBackup: true,
  batchSize: 25 // Process this many translations at once to reduce API calls
};

// OpenAI configuration
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

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

// Helper function to get a nested value from an object
function getNestedValue(obj, path) {
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current === undefined || current === null) {
      return undefined;
    }
    current = current[key];
  }
  
  return current;
}

// Collect all paths and values from a nested object
function getAllPaths(obj, prefix = '') {
  const paths = {};
  
  for (const key in obj) {
    const newPrefix = prefix ? `${prefix}.${key}` : key;
    
    if (typeof obj[key] === 'object' && obj[key] !== null) {
      Object.assign(paths, getAllPaths(obj[key], newPrefix));
    } else {
      paths[newPrefix] = obj[key];
    }
  }
  
  return paths;
}

// Improve translation using OpenAI
async function improveTranslation(englishText, currentKoreanText, key) {
  const prompt = `
Translate the following English text to proper, natural-sounding Korean:

English text: "${englishText}"
Current machine translation: "${currentKoreanText.replace('[자동번역] ', '')}"

Guidelines:
- Translate for a Korean audience with clear, natural phrasing
- Maintain the original meaning and intent
- Use appropriate Korean honorifics
- For UI elements, keep translations concise
- For technical terms, use standard Korean terminology

Respond with ONLY the improved Korean translation, nothing else.
`;

  try {
    const response = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        { role: "system", content: "You are a highly skilled Korean translator specializing in software localization." },
        { role: "user", content: prompt }
      ],
      temperature: 0.3,
      max_tokens: 300
    });

    return response.choices[0].message.content.trim();
  } catch (error) {
    console.error(`Error calling OpenAI API: ${error.message}`);
    return currentKoreanText; // Return original if API call fails
  }
}

// Process translations in batches
async function processBatch(batch, englishTranslations) {
  const promptsArray = batch.map(({ path, value }) => ({
    path,
    englishText: getNestedValue(englishTranslations, path) || '',
    currentKoreanText: value
  }));

  console.log(`\nProcessing batch of ${promptsArray.length} translations...`);
  
  const results = [];
  
  for (const item of promptsArray) {
    if (!item.englishText) {
      console.log(`Warning: No English text found for path ${item.path}, skipping`);
      continue;
    }
    
    process.stdout.write('.');
    const improvedTranslation = await improveTranslation(
      item.englishText, 
      item.currentKoreanText,
      item.path
    );
    
    results.push({
      path: item.path,
      original: item.currentKoreanText,
      improved: improvedTranslation
    });
  }
  
  console.log('\nBatch complete');
  return results;
}

// Main function to improve translations
async function improveTranslations() {
  console.log('===== Korean Translation Improver =====');
  
  try {
    // Load translation files
    const koTranslations = JSON.parse(fs.readFileSync(CONFIG.koFile, 'utf8'));
    const enTranslations = JSON.parse(fs.readFileSync(CONFIG.enFile, 'utf8'));
    
    // Get all paths and values
    const koPaths = getAllPaths(koTranslations);
    
    // Find all entries marked with [자동번역]
    const autoTranslatedEntries = Object.entries(koPaths)
      .filter(([_, value]) => typeof value === 'string' && value.startsWith('[자동번역]'))
      .map(([path, value]) => ({ path, value }));
    
    console.log(`Found ${autoTranslatedEntries.length} entries marked with [자동번역]`);
    
    if (autoTranslatedEntries.length === 0) {
      console.log('No entries to improve. Exiting...');
      return;
    }
    
    // Create backup if needed
    if (CONFIG.createBackup) {
      const backupFile = `${CONFIG.koFile}.backup.${Date.now()}.json`;
      fs.copyFileSync(CONFIG.koFile, backupFile);
      console.log(`Created backup at: ${backupFile}`);
    }
    
    // Process in batches to reduce API calls
    const batches = [];
    for (let i = 0; i < autoTranslatedEntries.length; i += CONFIG.batchSize) {
      batches.push(autoTranslatedEntries.slice(i, i + CONFIG.batchSize));
    }
    
    console.log(`Will process in ${batches.length} batches of up to ${CONFIG.batchSize} translations each`);
    
    // Check for OpenAI API key
    if (!process.env.OPENAI_API_KEY) {
      console.error('Error: OPENAI_API_KEY environment variable is not set');
      console.error('Please set it before running this script, e.g.:');
      console.error('OPENAI_API_KEY=your-key-here node improve-korean-translations.js');
      process.exit(1);
    }
    
    // Process each batch
    let allImprovedTranslations = [];
    for (let i = 0; i < batches.length; i++) {
      console.log(`\nProcessing batch ${i + 1} of ${batches.length}...`);
      const batchResults = await processBatch(batches[i], enTranslations);
      allImprovedTranslations = [...allImprovedTranslations, ...batchResults];
      
      // Show progress
      console.log(`Progress: ${allImprovedTranslations.length}/${autoTranslatedEntries.length} (${Math.round(allImprovedTranslations.length / autoTranslatedEntries.length * 100)}%)`);
    }
    
    // Update translations
    const newKoTranslations = JSON.parse(JSON.stringify(koTranslations));
    for (const { path, improved } of allImprovedTranslations) {
      setNestedValue(newKoTranslations, path, improved);
    }
    
    // Write updated translations
    fs.writeFileSync(CONFIG.koFile, JSON.stringify(newKoTranslations, null, 2), 'utf8');
    console.log(`\nTranslations written to: ${CONFIG.koFile}`);
    
    // Summary
    console.log(`\nImproved ${allImprovedTranslations.length} translations`);
    console.log('\nDone! 🎉');
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

// Run the script
improveTranslations().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
