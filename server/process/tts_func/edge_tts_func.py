"""
Edge-TTS Voice Synthesis
Uses Microsoft's free Edge TTS API with anime-appropriate voices.
Uses playsound for simple, reliable audio playback.
"""
import asyncio
import edge_tts
from pathlib import Path
import uuid
import time
import yaml


# Load voice from config
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / 'character_config.yaml'

try:
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    DEFAULT_VOICE = config.get('voice', 'en-US-JennyNeural')
except:
    DEFAULT_VOICE = 'en-US-JennyNeural'

# Available voices for reference
VOICE_OPTIONS = {
    "mature": "en-US-JennyNeural",    # Mature, confident
    "friendly": "en-US-AriaNeural",    # Friendly, warm
    "cute": "en-US-AnaNeural",         # Young, cute
    "energetic": "en-US-SaraNeural",   # Energetic
    "british": "en-GB-SoniaNeural",    # British accent
    "british_young": "en-GB-LibbyNeural",
}


async def _generate_audio_async(text: str, output_path: str, voice: str = DEFAULT_VOICE):
    """Generate audio file from text using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path


def generate_speech(text: str, output_path: str = "output.mp3", voice: str = DEFAULT_VOICE) -> str:
    """
    Generate speech audio from text.
    """
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Run async function
    asyncio.run(_generate_audio_async(text, output_path, voice))
    return output_path


def play_audio(path: str):
    """Play an audio file using playsound"""
    try:
        from playsound import playsound
        abs_path = str(Path(path).resolve())
        playsound(abs_path)
    except Exception as e:
        print(f"[!] Audio playback error: {e}")
        # Fallback: open with default player
        try:
            import os
            os.startfile(str(Path(path).resolve()))
            time.sleep(2)
        except:
            pass


def speak(text: str, voice: str = DEFAULT_VOICE):
    """Generate and play speech in one call"""
    output_path = Path("audio") / f"tts_{uuid.uuid4().hex}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"[TTS] Generating audio...")
    generate_speech(text, str(output_path), voice)
    print(f"[TTS] Playing...")
    play_audio(str(output_path))
    print(f"[TTS] Done!")
    
    # Cleanup
    try:
        output_path.unlink()
    except:
        pass


if __name__ == "__main__":
    # Test the TTS
    print("Testing Edge TTS...")
    speak("Hello senpai! I'm Riko, your AI companion. Nice to meet you!")
    print("Test complete!")
