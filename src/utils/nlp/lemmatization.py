"""
Lemmatization utilities for Lingogi application.

This module provides functions to convert words from different languages
into their base/infinitive forms. This is particularly useful for:
- Creating consistent flashcards
- Building a vocabulary bank
- Tracking users' vocabulary knowledge regardless of conjugation

The main function supports multiple languages by using appropriate NLP libraries
for each supported language.
"""

from typing import Dict, Optional, List, Tuple, Any
import logging
from loguru import logger
import os
import re

# We'll use spaCy as our primary NLP library
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Word lemmatization will be limited.")

# For Korean, we'll use specialized libraries
try:
    # Using KoNLPy for Korean lemmatization
    from konlpy.tag import Okt, Mecab, Hannanum, Kkma
    KONLPY_AVAILABLE = True
    
    # Try to initialize the Korean NLP processors
    try:
        okt = Okt()
        KONLPY_OKT_AVAILABLE = True
    except:
        KONLPY_OKT_AVAILABLE = False
        logger.warning("KoNLPy Okt not available. Korean lemmatization will be limited.")
        
    try:
        # Mecab is often faster and more accurate but requires additional setup
        mecab = Mecab()
        KONLPY_MECAB_AVAILABLE = True
    except:
        KONLPY_MECAB_AVAILABLE = False
        logger.warning("KoNLPy Mecab not available. Falling back to other Korean processors.")
except ImportError:
    KONLPY_AVAILABLE = False
    KONLPY_OKT_AVAILABLE = False
    KONLPY_MECAB_AVAILABLE = False
    logger.warning("KoNLPy not available. Korean lemmatization will be limited.")

# For Japanese, we'll use specialized libraries
try:
    import fugashi
    FUGASHI_AVAILABLE = True
    
    # Initialize the Japanese tokenizer
    try:
        japanese_tagger = fugashi.Tagger()
        JAPANESE_TAGGER_AVAILABLE = True
    except:
        JAPANESE_TAGGER_AVAILABLE = False
        logger.warning("Fugashi tagger initialization failed. Japanese lemmatization will be limited.")
except ImportError:
    FUGASHI_AVAILABLE = False
    JAPANESE_TAGGER_AVAILABLE = False
    logger.warning("Fugashi not available. Japanese lemmatization will be limited.")

# Cache for loaded spaCy models to avoid repeatedly loading them
SPACY_MODELS = {}

# Language code mappings to spaCy models
SPACY_MODEL_MAP = {
    'en': 'en_core_web_sm',    # English
    'es': 'es_core_news_sm',    # Spanish
    'fr': 'fr_core_news_sm',    # French
    'de': 'de_core_news_sm',    # German
    'it': 'it_core_news_sm',    # Italian
    'pt': 'pt_core_news_sm',    # Portuguese
    'nl': 'nl_core_news_sm',    # Dutch
    'zh': 'zh_core_web_sm',     # Chinese
    'ru': 'ru_core_news_sm',    # Russian
}

def _load_spacy_model(lang_code: str) -> Optional[Any]:
    """
    Load a spaCy model for the given language code.
    
    Args:
        lang_code: ISO language code (e.g., 'en', 'es')
        
    Returns:
        Loaded spaCy model or None if not available
    """
    if not SPACY_AVAILABLE:
        return None
        
    if lang_code in SPACY_MODELS:
        return SPACY_MODELS[lang_code]
        
    model_name = SPACY_MODEL_MAP.get(lang_code)
    if not model_name:
        logger.warning(f"No spaCy model mapping for language code: {lang_code}")
        return None
        
    try:
        # Try to load the model
        try:
            nlp = spacy.load(model_name)
            SPACY_MODELS[lang_code] = nlp
            return nlp
        except OSError:
            # If the model isn't installed, suggest downloading it
            logger.warning(f"spaCy model {model_name} not found. "
                          f"Install it using: python -m spacy download {model_name}")
            return None
    except Exception as e:
        logger.error(f"Error loading spaCy model for {lang_code}: {str(e)}")
        return None

def _lemmatize_with_spacy(word: str, lang_code: str) -> str:
    """
    Lemmatize a word using spaCy for the given language.
    
    Args:
        word: Word to lemmatize
        lang_code: ISO language code
        
    Returns:
        Lemmatized word or original word if lemmatization fails
    """
    nlp = _load_spacy_model(lang_code)
    if not nlp:
        return word
        
    doc = nlp(word)
    if len(doc) == 0:
        return word
        
    # Return the lemma of the first token
    # If multiple tokens, we would need more complex logic
    return doc[0].lemma_

def _lemmatize_korean(word: str) -> str:
    """
    Lemmatize a Korean word using available Korean NLP libraries.
    
    Args:
        word: Korean word to lemmatize
        
    Returns:
        Lemmatized Korean word or original word if lemmatization fails
    """
    if not KONLPY_AVAILABLE:
        return word
        
    try:
        # Try with Mecab first if available (generally more accurate)
        if KONLPY_MECAB_AVAILABLE:
            # Get the morphological analysis
            morphs = mecab.pos(word)
            if morphs:
                # Extract the base form (usually the first morpheme is the root)
                root = morphs[0][0]
                # Check for Korean verb endings and strip them
                if len(morphs) > 1 and morphs[-1][1].startswith('E'):
                    return root
                return root
                
        # Fall back to Okt if Mecab failed or isn't available
        if KONLPY_OKT_AVAILABLE:
            # Get the morphological analysis with Okt
            morphs = okt.pos(word, norm=True)
            if morphs:
                # Extract the base form
                return morphs[0][0]
                
    except Exception as e:
        logger.error(f"Error in Korean lemmatization: {str(e)}")
        
    # Return original word if all methods fail
    return word

def _lemmatize_japanese(word: str) -> str:
    """
    Lemmatize a Japanese word using available Japanese NLP libraries.
    
    Args:
        word: Japanese word to lemmatize
        
    Returns:
        Lemmatized Japanese word or original word if lemmatization fails
    """
    if not FUGASHI_AVAILABLE or not JAPANESE_TAGGER_AVAILABLE:
        return word
        
    try:
        # Parse the word with Fugashi
        parsed = japanese_tagger.parse(word)
        
        # For a single token, return its dictionary form (lemma)
        if len(parsed) == 1:
            return parsed[0].feature.lemma or word
            
        # For multiple tokens, join their lemmas
        lemmas = []
        for token in parsed:
            # Use the lemma if available, otherwise use the surface form
            lemma = token.feature.lemma or token.surface
            lemmas.append(lemma)
            
        return ''.join(lemmas)
        
    except Exception as e:
        logger.error(f"Error in Japanese lemmatization: {str(e)}")
        
    # Return original word if all methods fail
    return word

def _apply_fallback_rules(word: str, lang_code: str) -> str:
    """
    Apply basic language-specific fallback rules for lemmatization when NLP libraries aren't available.
    
    Args:
        word: Word to lemmatize
        lang_code: ISO language code
        
    Returns:
        Lemmatized word based on simple rules
    """
    # English fallback rules
    if lang_code == 'en':
        # Handle basic English verb forms
        if word.endswith('ing'):
            # swimming -> swim, running -> run
            if len(word) > 4 and word[-4] == word[-5]:  # Double consonant
                return word[:-4]
            # walking -> walk
            return word[:-3]
        elif word.endswith('ed'):
            # walked -> walk
            return word[:-2]
        elif word.endswith('s') and not word.endswith('ss'):
            # runs -> run, cars -> car (but not pass -> pa)
            return word[:-1]
            
    # Spanish fallback rules
    elif lang_code == 'es':
        # Very basic handling of regular verb forms
        if word.endswith('ar') or word.endswith('er') or word.endswith('ir'):
            return word  # Already infinitive
        if word.endswith('ando') or word.endswith('endo'):
            # hablando -> habl + ar = hablar
            return word[:-4] + 'ar'
            
    # French fallback rules
    elif lang_code == 'fr':
        # Very basic handling of regular verb forms
        if word.endswith('er') or word.endswith('ir') or word.endswith('re'):
            return word  # Already infinitive
            
    # Add more language-specific rules as needed
    
    # Return original word if no rules match
    return word

def get_word_base_form(word: str, lang_code: str, context: Optional[str] = None) -> str:
    """
    Convert a word to its base/infinitive form.
    
    This function handles words in multiple languages and tries to return the lemma
    (dictionary form) of the word, which is essential for consistent vocabulary tracking.
    For example:
    - English: "running" -> "run", "ate" -> "eat"
    - Spanish: "hablando" -> "hablar", "comí" -> "comer"
    - Korean: "먹었어요" -> "먹다", "갔습니다" -> "가다"
    
    Args:
        word: The word to convert to base form
        lang_code: ISO language code (e.g., 'en', 'ko', 'es')
        context: Optional surrounding text for better disambiguation
        
    Returns:
        The base form of the word, or the original word if conversion fails
    """
    # Clean the input word
    word = word.strip()
    if not word:
        return word
        
    # Log the lemmatization attempt
    logger.debug(f"Lemmatizing word '{word}' in language '{lang_code}'")
    
    # Handle language-specific lemmatization
    if lang_code == 'ko':
        return _lemmatize_korean(word)
    elif lang_code == 'ja':
        return _lemmatize_japanese(word)
    elif lang_code in SPACY_MODEL_MAP and SPACY_AVAILABLE:
        return _lemmatize_with_spacy(word, lang_code)
        
    # Use fallback rules if specialized handling isn't available
    return _apply_fallback_rules(word, lang_code)

def get_word_info(word: str, lang_code: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Get comprehensive information about a word, including its base form and other linguistic details.
    
    Args:
        word: The word to analyze
        lang_code: ISO language code
        context: Optional surrounding text for better disambiguation
        
    Returns:
        Dictionary with word information:
        - base_form: The lemmatized/infinitive form
        - pos: Part of speech (if available)
        - is_conjugated: Whether the word appears to be conjugated
        - original_word: The original word
    """
    base_form = get_word_base_form(word, lang_code, context)
    
    # Initialize result with basic info
    result = {
        'original_word': word,
        'base_form': base_form,
        'language': lang_code,
        'pos': None,  # Part of speech
        'is_conjugated': base_form != word
    }
    
    # Add part of speech information if possible
    if lang_code in SPACY_MODEL_MAP and SPACY_AVAILABLE:
        nlp = _load_spacy_model(lang_code)
        if nlp:
            doc = nlp(word)
            if len(doc) > 0:
                result['pos'] = doc[0].pos_
    elif lang_code == 'ko' and KONLPY_AVAILABLE:
        # Try to get part of speech for Korean
        if KONLPY_OKT_AVAILABLE:
            try:
                pos = okt.pos(word)
                if pos:
                    result['pos'] = pos[0][1]
            except:
                pass
                
    return result
