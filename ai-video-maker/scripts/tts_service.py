#!/usr/bin/env python3
"""TTS generation service with provider abstraction."""

import os
import subprocess
import time
import wave
from abc import ABC, abstractmethod

from config import TTSConfig


class TTSProvider(ABC):
    @abstractmethod
    def generate(self, text: str, output_path: str) -> bool:
        """Generate TTS audio. Returns True on success."""
        ...


class GeminiTTS(TTSProvider):
    def __init__(self, config: TTSConfig):
        self.config = config
        api_key = os.environ.get(config.api_key_env, "")
        if not api_key:
            raise ValueError(f"Environment variable {config.api_key_env} not set")

        from google import genai
        from google.genai import types
        self.client = genai.Client(api_key=api_key)
        self.types = types

    def generate(self, text: str, output_path: str) -> bool:
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=text,
            config=self.types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=self.types.SpeechConfig(
                    voice_config=self.types.VoiceConfig(
                        prebuilt_voice_config=self.types.PrebuiltVoiceConfig(
                            voice_name=self.config.voice
                        )
                    )
                ),
            ),
        )
        data = response.candidates[0].content.parts[0].inline_data.data
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(data)
        return True


class EdgeTTS(TTSProvider):
    def __init__(self, config: TTSConfig):
        self.config = config
        self.voice = config.voice or "zh-CN-XiaoxiaoNeural"

    def generate(self, text: str, output_path: str) -> bool:
        cmd = [
            "edge-tts",
            "--voice", self.voice,
            "--text", text,
            "--write-media", output_path,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode == 0


def create_tts_provider(config: TTSConfig) -> TTSProvider:
    """Factory function for TTS provider."""
    providers = {
        "gemini": GeminiTTS,
        "edge": EdgeTTS,
    }
    cls = providers.get(config.provider)
    if not cls:
        raise ValueError(f"Unknown TTS provider: {config.provider}. Options: {list(providers.keys())}")
    return cls(config)


def verify_audio(path: str) -> bool:
    """Check audio is not silent (has non-zero amplitude)."""
    try:
        w = wave.open(path, "rb")
        frames = w.readframes(min(w.getnframes(), 5000))
        w.close()
        if not frames:
            return False
        mx = max(
            abs(int.from_bytes(frames[i : i + 2], "little", signed=True))
            for i in range(0, len(frames), 2)
        )
        return mx > 0
    except Exception:
        return False


def apply_speed(input_path: str, output_path: str, speed: float) -> bool:
    """Apply atempo filter via ffmpeg. Returns True on success."""
    if abs(speed - 1.0) < 0.01:
        return True  # No change needed
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:a", f"atempo={speed}",
        "-ar", "24000",
        output_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode == 0:
        # Replace original with speed-adjusted version
        os.replace(output_path, input_path)
        return True
    return False


def generate_tts_with_retry(provider: TTSProvider, text: str, output_path: str,
                             config: TTSConfig) -> bool:
    """Generate TTS with retry loop and silence verification."""
    for attempt in range(1, config.max_retries + 1):
        try:
            success = provider.generate(text, output_path)
            if success and os.path.exists(output_path) and verify_audio(output_path):
                # Apply speed adjustment if needed
                if config.speed != 1.0:
                    tmp = output_path + ".speed.wav"
                    apply_speed(output_path, tmp, config.speed)
                return True
            print(f"    Attempt {attempt}: audio silent or empty, retrying...")
        except Exception as e:
            print(f"    Attempt {attempt} failed: {e}")

        if attempt < config.max_retries:
            time.sleep(config.retry_delay)

    print(f"    FAILED after {config.max_retries} attempts")
    return False
