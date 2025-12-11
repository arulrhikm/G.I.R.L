# -*- coding: utf-8 -*-
"""
G.I.R.L - Full Voice + Avatar Interface
Supports: Voice/Text input, Voice/Text output, Visual avatar
"""
from pathlib import Path
import os
import uuid
import sys
import warnings

# Suppress ALL warnings to prevent numpy crash output
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import core module first (this always works)
from process.llm_funcs.llm_scr import llm_response

# Voice output (TTS) - Edge-TTS
VOICE_OUTPUT_AVAILABLE = False
TTS_ENGINE = None
edge_speak = None
try:
    from process.tts_func.edge_tts_func import speak as _edge_speak
    edge_speak = _edge_speak
    VOICE_OUTPUT_AVAILABLE = True
    TTS_ENGINE = "edge-tts"
    print("[OK] Voice output ready (Edge-TTS)")
except Exception as e:
    print(f"[--] Voice output not available: {e}")

# Avatar display
AVATAR_AVAILABLE = False
show_avatar = None
set_speaking = None
set_idle = None
try:
    from avatar_display import show_avatar as _show_avatar, set_speaking as _set_speaking, set_idle as _set_idle
    show_avatar = _show_avatar
    set_speaking = _set_speaking
    set_idle = _set_idle
    AVATAR_AVAILABLE = True
    print("[OK] Avatar display ready")
except Exception as e:
    print(f"[--] Avatar display not available: {e}")

# Voice input (ASR) - try to import in a way that catches crashes
VOICE_INPUT_AVAILABLE = False
WhisperModel = None
record_and_transcribe = None

# Skip voice input for now due to numpy compatibility issues
# Can be enabled later when numpy/whisper versions are compatible
print("[--] Voice input disabled (numpy compatibility)")


def get_user_input(whisper_model=None):
    """Get input from user - voice or text"""
    print("\n" + "="*50)
    print("How do you want to communicate?")
    print("  [1] Type your message")
    if VOICE_INPUT_AVAILABLE and whisper_model:
        print("  [2] Speak (push-to-talk)")
    print("  [q] Quit")
    print("="*50)
    
    choice = input("Your choice: ").strip().lower()
    
    if choice == 'q':
        return None, 'quit'
    
    if choice == '2' and VOICE_INPUT_AVAILABLE and whisper_model and record_and_transcribe:
        conversation_recording = Path("audio") / "conversation.wav"
        conversation_recording.parent.mkdir(parents=True, exist_ok=True)
        user_text = record_and_transcribe(whisper_model, conversation_recording)
        return user_text, 'voice'
    else:
        user_text = input("\nYou: ").strip()
        return user_text, 'text'


def speak_response(text: str):
    """Speak the response using available TTS engine"""
    if not VOICE_OUTPUT_AVAILABLE or not edge_speak:
        return
    
    # Update avatar to speaking state
    if AVATAR_AVAILABLE and set_speaking:
        set_speaking(text)
    
    try:
        edge_speak(text)
    except Exception as e:
        print(f"[!] TTS error: {e}")
    finally:
        # Return avatar to idle
        if AVATAR_AVAILABLE and set_idle:
            set_idle()


def output_response(response_text: str, auto_voice: bool = False):
    """Output response with text and optional voice"""
    print(f"\nRiko: {response_text}")
    
    if not VOICE_OUTPUT_AVAILABLE:
        return
    
    if auto_voice:
        speak_response(response_text)
    else:
        voice_choice = input("\nPlay voice? [y/N]: ").strip().lower()
        if voice_choice == 'y':
            speak_response(response_text)


def main():
    print("")
    print("========================================================")
    print("           G.I.R.L - Project Riko")
    print("       Your AI Waifu Companion is ready!")
    print("========================================================")
    print("")
    
    # Start avatar window if available
    if AVATAR_AVAILABLE and show_avatar:
        print("[*] Opening avatar window...")
        show_avatar()
    
    print("\nReady to chat!\n")
    
    # Ask about auto-voice mode (defaults to YES)
    auto_voice = True  # Default to auto-play
    if VOICE_OUTPUT_AVAILABLE:
        auto_choice = input("Auto-play voice responses? [Y/n]: ").strip().lower()
        auto_voice = auto_choice != 'n'  # Only disable if explicitly 'n'
        if auto_voice:
            print("[OK] Voice auto-play enabled!")
        print("")
    
    # Main conversation loop
    while True:
        try:
            user_text, input_mode = get_user_input(None)
            
            if input_mode == 'quit' or user_text is None:
                handle_quit()
                break
            
            if not user_text:
                print("(No input detected, try again)")
                continue
            
            # Get LLM response
            print("\n[...] Riko is thinking...")
            response = llm_response(user_text)
            
            # Output response
            output_response(response, auto_voice)
            
        except KeyboardInterrupt:
            print("\n")
            handle_quit()
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            continue


def handle_quit():
    """Handle quit with option to save or clear history"""
    print("\n" + "="*50)
    print("Quitting... What about our conversation?")
    print("  [1] Save chat history (default)")
    print("  [2] Clear everything (history + audio files)")
    print("="*50)
    
    choice = input("Your choice [1]: ").strip()
    
    if choice == '2':
        # Clear chat history
        server_history = Path("chat_history.json")
        
        try:
            if server_history.exists():
                server_history.unlink()
                print("[OK] Cleared: chat_history.json")
        except Exception as e:
            print(f"[!] Could not clear history: {e}")
        
        # Clear audio files
        audio_dir = Path("audio")
        if audio_dir.exists():
            audio_count = 0
            for audio_file in audio_dir.glob("*"):
                if audio_file.is_file():
                    try:
                        audio_file.unlink()
                        audio_count += 1
                    except:
                        pass
            if audio_count > 0:
                print(f"[OK] Cleared: {audio_count} audio file(s)")
        
        print("[OK] Fresh start ready for next time!")
    else:
        print("[OK] Chat history saved!")
    
    print("\nBye bye, senpai~!")
    if VOICE_OUTPUT_AVAILABLE:
        speak_response("Bye bye, senpai!")


if __name__ == "__main__":
    main()