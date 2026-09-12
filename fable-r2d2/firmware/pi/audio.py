"""Sound playback for the fable-r2d2 Raspberry Pi control server.

Plays the WAV clips in ``firmware/pi/sounds`` that ``scripts/generate_audio.py``
produced.  Two back ends are supported and chosen at start up:

``aplay``
    The ALSA command line player that ships with Raspberry Pi OS.  Preferred,
    because it needs no Python audio stack and adds no latency to the asyncio
    loop.
``pygame.mixer``
    Used when ``aplay`` is not on the path but pygame is installed.

If neither is available the player logs the reason once at start up and every
request after that returns a clear failure, so a silent robot is visible in the
log rather than a mystery.
"""

import csv
import logging
import os
import shutil
import subprocess
import threading

LOGGER = logging.getLogger("r2d2.audio")

HERE = os.path.dirname(os.path.abspath(__file__))
SOUND_DIR = os.path.join(HERE, "sounds")
CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(HERE)), "audio", "catalog.csv")

APLAY = "aplay"
"""ALSA player binary name."""


def load_catalogue(catalog_path=CATALOG_PATH, sound_dir=SOUND_DIR):
    """Return ``{name: absolute_path}`` for every clip that is really on disk.

    The catalogue CSV is the index, but a name is only offered when its file
    exists, so a half copied card cannot present a button that does nothing.
    Clips found in the sound directory but missing from the catalogue are still
    offered, and logged, because playing them is harmless.
    """
    clips = {}
    if os.path.isfile(catalog_path):
        with open(catalog_path, newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                name = (row.get("name") or "").strip()
                relative = (row.get("file") or "").strip()
                if not name or not relative:
                    continue
                path = os.path.join(sound_dir, os.path.basename(relative))
                if os.path.isfile(path):
                    clips[name] = path
                else:
                    LOGGER.warning("catalogue lists %s but %s is missing", name, path)
    else:
        LOGGER.warning("no sound catalogue at %s", catalog_path)

    if os.path.isdir(sound_dir):
        for filename in sorted(os.listdir(sound_dir)):
            if not filename.lower().endswith(".wav"):
                continue
            name = os.path.splitext(filename)[0]
            if name not in clips:
                LOGGER.info("%s is on disk but not in the catalogue; offering it anyway",
                            filename)
                clips[name] = os.path.join(sound_dir, filename)
    else:
        LOGGER.error("sound directory %s does not exist; run scripts/generate_audio.py",
                     sound_dir)
    return clips


class SoundPlayer:
    """Plays one clip at a time, never blocking the caller."""

    def __init__(self, sound_dir=SOUND_DIR, catalog_path=CATALOG_PATH):
        self.clips = load_catalogue(catalog_path, sound_dir)
        self._lock = threading.Lock()
        self._process = None
        self._mixer = None
        self.backend = None
        self.last_error = None

        if shutil.which(APLAY):
            self.backend = "aplay"
        else:
            try:
                import pygame

                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
                self._mixer = pygame.mixer
                self.backend = "pygame"
            except Exception as error:  # pygame raises its own error types
                self.last_error = (
                    "no audio back end: aplay is not on PATH and pygame could not "
                    "start ({0})".format(error)
                )
                LOGGER.error("%s", self.last_error)

        if self.backend:
            LOGGER.info("audio back end %s, %d clips", self.backend, len(self.clips))

    def names(self):
        """Sorted list of clip names the web page may ask for."""
        return sorted(self.clips)

    def available(self):
        """True when a clip can actually be played."""
        return self.backend is not None and bool(self.clips)

    def play(self, name):
        """Start ``name``, interrupting whatever is playing.  Returns True on success."""
        path = self.clips.get(name)
        if path is None:
            LOGGER.warning("no such clip: %s", name)
            return False
        if self.backend is None:
            LOGGER.warning("cannot play %s: %s", name, self.last_error)
            return False
        with self._lock:
            self._stop_locked()
            if self.backend == "aplay":
                try:
                    self._process = subprocess.Popen(
                        [APLAY, "-q", path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                    )
                except OSError as error:
                    self.last_error = "aplay failed: {0}".format(error)
                    LOGGER.error("%s", self.last_error)
                    return False
            else:
                try:
                    sound = self._mixer.Sound(path)
                    sound.play()
                except Exception as error:
                    self.last_error = "pygame failed: {0}".format(error)
                    LOGGER.error("%s", self.last_error)
                    return False
        LOGGER.info("playing %s", name)
        return True

    def _stop_locked(self):
        """Stop playback.  The caller already holds the lock."""
        if self._process is not None:
            if self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=0.5)
                except subprocess.TimeoutExpired:
                    self._process.kill()
            self._process = None
        if self._mixer is not None:
            self._mixer.stop()

    def stop(self):
        """Stop whatever is playing."""
        with self._lock:
            self._stop_locked()

    def close(self):
        """Stop playback and release the audio device."""
        self.stop()
        if self._mixer is not None:
            try:
                self._mixer.quit()
            except Exception as error:
                LOGGER.warning("closing the pygame mixer failed: %s", error)
            self._mixer = None
