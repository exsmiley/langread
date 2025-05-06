"""
Centralized configuration of supported languages for Lingogi.

This module serves as the source of truth for all language-related configuration.
All components of the application should reference these constants rather than
hardcoding language codes or support levels.
"""

from typing import Dict, List, Optional, Tuple, Set, Literal
from pydantic import BaseModel
from enum import Enum


class SupportLevel(str, Enum):
    """Enum representing the level of support for a language feature."""
    FULL = "full"         # Full feature support
    ADVANCED = "advanced" # Advanced features supported
    BASIC = "basic"       # Basic functionality only
    EXPERIMENTAL = "experimental"  # Experimental/beta support


class LanguageInfo(BaseModel):
    """Information about a supported language."""
    code: str             # ISO 639-1 language code
    english_name: str     # Name in English
    native_name: str      # Name in the native language
    rtl: bool = False     # Right-to-left script
    lemmatization: SupportLevel  # Level of lemmatization support
    translation: SupportLevel    # Level of translation support
    speech_synthesis: SupportLevel = SupportLevel.EXPERIMENTAL  # Text-to-speech support
    speech_recognition: SupportLevel = SupportLevel.EXPERIMENTAL  # Speech-to-text support
    default_enabled: bool = True  # Whether enabled by default in language selection UI


# The central registry of all supported languages
# This is the source of truth for language support in the application
SUPPORTED_LANGUAGES: Dict[str, LanguageInfo] = {
    # Asian languages
    "ko": LanguageInfo(
        code="ko",
        english_name="Korean",
        native_name="한국어",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "ja": LanguageInfo(
        code="ja",
        english_name="Japanese",
        native_name="日本語",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "zh": LanguageInfo(
        code="zh",
        english_name="Chinese (Simplified)",
        native_name="中文",
        lemmatization=SupportLevel.BASIC,
        translation=SupportLevel.ADVANCED,
        default_enabled=True,
    ),
    
    # European languages
    "en": LanguageInfo(
        code="en",
        english_name="English",
        native_name="English",
        lemmatization=SupportLevel.FULL,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "es": LanguageInfo(
        code="es",
        english_name="Spanish",
        native_name="Español",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "fr": LanguageInfo(
        code="fr",
        english_name="French",
        native_name="Français",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "de": LanguageInfo(
        code="de",
        english_name="German",
        native_name="Deutsch",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "it": LanguageInfo(
        code="it",
        english_name="Italian",
        native_name="Italiano",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "pt": LanguageInfo(
        code="pt",
        english_name="Portuguese",
        native_name="Português",
        lemmatization=SupportLevel.ADVANCED,
        translation=SupportLevel.FULL,
        default_enabled=True,
    ),
    "ru": LanguageInfo(
        code="ru",
        english_name="Russian",
        native_name="Русский",
        lemmatization=SupportLevel.BASIC,
        translation=SupportLevel.ADVANCED,
        default_enabled=True,
    ),
    
    # Middle Eastern languages
    "ar": LanguageInfo(
        code="ar",
        english_name="Arabic",
        native_name="العربية",
        rtl=True,
        lemmatization=SupportLevel.BASIC,
        translation=SupportLevel.ADVANCED,
        default_enabled=True,
    ),
    "he": LanguageInfo(
        code="he",
        english_name="Hebrew",
        native_name="עברית",
        rtl=True,
        lemmatization=SupportLevel.BASIC,
        translation=SupportLevel.BASIC,
        default_enabled=False,
    ),
}

# Common utility functions for working with the language registry

def get_language_info(language_code: str) -> Optional[LanguageInfo]:
    """Get information about a language by its code."""
    return SUPPORTED_LANGUAGES.get(language_code)

def get_supported_language_codes() -> List[str]:
    """Get a list of all supported language codes."""
    return list(SUPPORTED_LANGUAGES.keys())

def get_language_name(language_code: str, native: bool = False) -> str:
    """Get the name of a language, either in English or native form."""
    info = get_language_info(language_code)
    if not info:
        return language_code
    return info.native_name if native else info.english_name

def get_languages_by_support_level(feature: str, level: SupportLevel) -> List[str]:
    """Get languages that have a specific support level for a given feature."""
    result = []
    for code, info in SUPPORTED_LANGUAGES.items():
        if hasattr(info, feature) and getattr(info, feature) == level:
            result.append(code)
    return result

def get_languages_with_lemmatization() -> List[str]:
    """Get all languages that have at least basic lemmatization support."""
    return [
        code for code, info in SUPPORTED_LANGUAGES.items()
        if info.lemmatization in [SupportLevel.BASIC, SupportLevel.ADVANCED, SupportLevel.FULL]
    ]
