"""Retro sound effects manager for PyArcade Studio."""

from __future__ import annotations

import atexit
import logging
import math
import os
import struct
import tempfile
import wave
from typing import Any

try:
    from PyQt5.QtCore import QSettings, QUrl
    from PyQt5.QtMultimedia import QAudioDeviceInfo, QSoundEffect

    QT_MULTIMEDIA_AVAILABLE = True
except Exception:  # pragma: no cover - environment-dependent
    QSettings = None
    QUrl = None
    QAudioDeviceInfo = None
    QSoundEffect = None
    QT_MULTIMEDIA_AVAILABLE = False

logger = logging.getLogger(__name__)

SAMPLE_RATE = 22050


class SoundManager:
    """Singleton manager for retro UI sound effects.

    The manager generates small WAV files at runtime and plays them with
    PyQt5.QtMultimedia.QSoundEffect. If Qt Multimedia is unavailable, all
    playback methods degrade gracefully to no-ops.
    """

    _instance: SoundManager | None = None

    def __init__(self) -> None:
        """Initialize the sound manager. Use SoundManager.instance()."""
        self._muted: bool = False
        self._enabled: bool = QT_MULTIMEDIA_AVAILABLE
        self._effects: dict[str, Any] = {}
        self._sound_paths: dict[str, str] = {}
        self._temp_files: list[str] = []
        self._temp_dir: str | None = None
        self._settings: Any = None

        if QSettings is not None:
            try:
                self._settings = QSettings("PyArcadeStudio", "PyArcade")
                self._muted = bool(self._settings.value("audio/muted", False, type=bool))
            except Exception:
                self._settings = None

        if not self._enabled or QSoundEffect is None:
            self._enabled = False
            return

        try:
            if QAudioDeviceInfo is not None:
                try:
                    default_device = QAudioDeviceInfo.defaultOutputDevice()
                    if default_device.isNull():
                        logger.info("No default audio output device; sound disabled.")
                        self._enabled = False
                        return
                except Exception:
                    pass

            self._temp_dir = tempfile.mkdtemp(prefix="pyarcade_sounds_")
            self._generate_sound_files()
            self._create_effects()

            if not self._effects:
                self._enabled = False
                return

            atexit.register(self._cleanup)
        except Exception as exc:
            logger.warning("Sound manager initialization failed: %s", exc)
            self._enabled = False

    @classmethod
    def instance(cls) -> SoundManager:
        """Return the shared SoundManager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def enabled(self) -> bool:
        """Whether sound playback is enabled."""
        return self._enabled

    @property
    def muted(self) -> bool:
        """Whether sound playback is muted."""
        return self._muted

    def is_muted(self) -> bool:
        """Return True if sounds are muted."""
        return self._muted

    def set_muted(self, muted: bool) -> None:
        """Set mute state and persist it when possible."""
        self._muted = bool(muted)
        self._persist_muted()
        if self._muted:
            self.stop_all()

    def toggle_mute(self) -> bool:
        """Toggle mute state and return the new muted state."""
        self._muted = not self._muted
        self._persist_muted()
        if self._muted:
            self.stop_all()
        return self._muted

    def play_click(self) -> None:
        """Play a short click sound for buttons and UI actions."""
        self.play("click")

    def play_move(self) -> None:
        """Play a move/interaction sound."""
        self.play("move")

    def play_win(self) -> None:
        """Play a winning jingle."""
        self.play("win")

    def play_lose(self) -> None:
        """Play a losing jingle."""
        self.play("lose")

    def play(self, name: str) -> None:
        """Play a registered sound by name."""
        if self._muted or not self._enabled:
            return

        effect = self._effects.get(name)
        if effect is None:
            return

        try:
            if effect.isPlaying():
                effect.stop()
            effect.play()
        except Exception as exc:
            logger.debug("Could not play sound '%s': %s", name, exc)

    def stop_all(self) -> None:
        """Stop all active sounds."""
        for effect in self._effects.values():
            try:
                if effect.isPlaying():
                    effect.stop()
            except Exception as exc:
                logger.debug("Could not stop sound effect: %s", exc)

    def _persist_muted(self) -> None:
        """Persist mute state using QSettings if available."""
        if self._settings is None:
            return
        try:
            self._settings.setValue("audio/muted", self._muted)
            self._settings.sync()
        except Exception as exc:
            logger.debug("Could not persist mute state: %s", exc)

    def _generate_sound_files(self) -> None:
        """Generate temporary retro WAV files."""
        if not self._temp_dir:
            return

        click_frames = self._tone(880.0, 0.035, volume=0.45)
        move_frames = self._tone(320.0, 0.055, volume=0.40)

        win_frames = self._sequence(
            [523.25, 659.25, 783.99, 1046.50],
            note_duration=0.085,
            volume=0.55,
        )
        lose_frames = self._sequence(
            [392.00, 329.63, 261.63, 196.00],
            note_duration=0.110,
            volume=0.55,
        )

        self._sound_paths = {
            "click": self._write_wav("click.wav", click_frames),
            "move": self._write_wav("move.wav", move_frames),
            "win": self._write_wav("win.wav", win_frames),
            "lose": self._write_wav("lose.wav", lose_frames),
        }

    def _create_effects(self) -> None:
        """Create QSoundEffect objects for each generated sound."""
        if QSoundEffect is None or QUrl is None:
            return

        for name, path in self._sound_paths.items():
            effect = QSoundEffect()
            effect.setSource(QUrl.fromLocalFile(path))
            effect.setVolume(1.0)
            effect.setLoopCount(1)
            self._effects[name] = effect

    def _write_wav(self, filename: str, frames: bytes) -> str:
        """Write raw PCM frames to a mono 16-bit WAV file."""
        if not self._temp_dir:
            raise RuntimeError("Temporary sound directory is not initialized.")

        path = os.path.join(self._temp_dir, filename)
        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(frames)

        self._temp_files.append(path)
        return path

    def _tone(self, frequency: float, duration: float, volume: float = 0.5) -> bytes:
        """Generate a simple fading sine tone."""
        total_samples = max(1, int(SAMPLE_RATE * duration))
        fade_samples = max(1, int(SAMPLE_RATE * min(0.005, duration / 3.0)))
        frames = bytearray()

        for i in range(total_samples):
            t = i / SAMPLE_RATE
            sample = volume * math.sin(2.0 * math.pi * frequency * t)

            if i < fade_samples:
                sample *= i / fade_samples
            elif i > total_samples - fade_samples:
                sample *= max(0.0, (total_samples - i) / fade_samples)

            sample = max(-1.0, min(1.0, sample))
            frames.extend(struct.pack("<h", int(sample * 32767)))

        return bytes(frames)

    def _sequence(self, frequencies: list[float], note_duration: float, volume: float = 0.5) -> bytes:
        """Generate a sequence of tones separated by short silence."""
        chunks: list[bytes] = []
        gap = self._silence(0.02)

        for frequency in frequencies:
            if frequency <= 0:
                chunks.append(self._silence(note_duration))
            else:
                chunks.append(self._tone(frequency, note_duration, volume))
            chunks.append(gap)

        return b"".join(chunks)

    def _silence(self, duration: float) -> bytes:
        """Generate silent PCM frames."""
        sample_count = max(0, int(SAMPLE_RATE * duration))
        return b"\x00\x00" * sample_count

    def _cleanup(self) -> None:
        """Remove generated temporary sound files."""
        for path in self._temp_files:
            try:
                os.remove(path)
            except OSError:
                pass

        if self._temp_dir:
            try:
                os.rmdir(self._temp_dir)
            except OSError:
                pass