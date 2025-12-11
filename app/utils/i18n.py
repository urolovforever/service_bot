"""Internationalization helper"""

import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

# Load all translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {}
LOCALES_DIR = Path(__file__).parent.parent / "locales"


def load_translations():
    """Load all translation files"""
    global TRANSLATIONS

    for locale_file in LOCALES_DIR.glob("*.json"):
        lang_code = locale_file.stem
        try:
            with open(locale_file, "r", encoding="utf-8") as f:
                TRANSLATIONS[lang_code] = json.load(f)
            logger.info(f"Loaded translations for {lang_code}")
        except Exception as e:
            logger.error(f"Failed to load translations for {lang_code}: {e}")


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Get translated text"""
    if lang not in TRANSLATIONS:
        lang = "en"

    text = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS.get("en", {}).get(key, key))

    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing format key {e} for text: {key}")

    return text


# Load translations on module import
load_translations()
