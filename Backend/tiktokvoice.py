import asyncio
import edge_tts

DEFAULT_VOICE = "en-US-ChristopherNeural"

# Map MoneyPrinter's default frontend TikTok voice IDs to Edge neural voices
VOICE_MAPPING = {
    "en_us_001": "en-US-ChristopherNeural",
    "en_us_006": "en-US-GuyNeural",
    "en_us_007": "en-US-JennyNeural",
    "en_us_009": "en-US-AriaNeural",
    "en_us_010": "en-US-EricNeural",
    "en_uk_001": "en-GB-RyanNeural",
    "en_uk_003": "en-GB-SoniaNeural",
    "en_au_001": "en-AU-WilliamNeural",
    "en_au_002": "en-AU-NatashaNeural",
    "en_female_emotional": "en-US-AnaNeural",
}

def tts(text: str, voice: str = "en_us_001", filename: str = "voice.mp3") -> None:
    """
    Drop-in replacement for TikTok TTS using Edge TTS.
    Compatible with MoneyPrinter pipeline calls.
    """
    if not text.strip():
        return

    # Select mapped voice or fall back to default
    selected_voice = VOICE_MAPPING.get(voice, voice if "-" in voice else DEFAULT_VOICE)

    async def _generate():
        communicate = edge_tts.Communicate(text=text, voice=selected_voice)
        await communicate.save(filename)

    asyncio.run(_generate())