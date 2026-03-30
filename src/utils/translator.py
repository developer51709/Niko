import asyncio
from discord import Locale
from discord.enums import _UNICODE_LANG_MAP

from deep_translator import GoogleTranslator
from langdetect import detect as langdetect_detect

SUPPORTED_LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)

class Translator:
    """Supported languages are correlated to supported discord.Locale."""

    LOCALE_TO_LANGCODE = {
        code: code.split('-')[0]
        for code in _UNICODE_LANG_MAP.keys()
        if code.split('-')[0] in SUPPORTED_LANGUAGES.values()
    }

    LANG_TO_COUNTRY = {
        "en": "gb",
        "sv": "se",
        "zh": "cn",
        "zh-cn": "cn",
        "zh-tw": "tw",
        "ja": "jp",
        "ko": "kr",
        "hi": "in",
        "el": "gr",
        "vi": "vn",
        "cs": "cz",
        "da": "dk",
        "uk": "ua",
    }

    @staticmethod
    async def detect(text: str) -> str:
        loop = asyncio.get_event_loop()
        try:
            lang = await loop.run_in_executor(None, langdetect_detect, text)
            return lang
        except Exception:
            raise RuntimeError("Language not detected.")

    @staticmethod
    async def translate(text: str, dest: str = "en", src: str = "auto") -> str:
        loop = asyncio.get_event_loop()
        def _translate():
            translator = GoogleTranslator(source=src, target=dest)
            return translator.translate(text)
        result = await loop.run_in_executor(None, _translate)
        if result:
            return result
        raise RuntimeError("Translation failed.")

    @staticmethod
    async def translate_to_locale(text: str, locale: Locale, src: str = "auto") -> str:
        dest = Translator.LOCALE_TO_LANGCODE.get(locale.language_code, None)
        return await Translator.translate(text, dest=dest, src=src)

    @staticmethod
    def code_to_flag(code: str) -> str:
        code = Translator.LANG_TO_COUNTRY.get(code.lower(), code)

        if len(code) != 2:
            return '🏳️'

        OFFSET = 0x1F1E6
        return ''.join(chr(OFFSET + ord(c.upper()) - ord('A')) for c in code)

    @staticmethod
    def locale_to_flag(locale: Locale) -> str:
        code = locale.language_code
        region = code.split('-')[-1] if '-' in code else code

        return Translator.code_to_flag(region)
