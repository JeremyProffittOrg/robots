# Original robot voice collection

The sixteen MP3 files are in `firmware/data/audio/`. They are original
synthesized beeps, chirps and whistles. They are not recordings from a film,
and they do not reproduce an actor's voice. Names describe intended moods.

`catalog.csv` provides names, durations and SHA-256 hashes. The phone sound
menu plays every file through the onboard amplifier and speaker. The
collection includes greetings, questions, agreement, concern, excitement,
sleepy sounds, searching, surprise and a longer robot story.

Format: mono MP3, 22,050 Hz, 64 kbit/s. Rebuild with
`python scripts/generate_audio.py`; NumPy and FFmpeg are required. The
deterministic oscillator source and seeds are included. No web audio was
downloaded. These generated audio files may be used, changed and shared
with this robot project. No claim is made to the R2-D2 trademark.

After changing audio, run `pio run -d firmware -t buildfs`, then upload the
filesystem to the disconnected controller as described in the manual.
Firmware playback gain is limited to 0.22. Start with a low listening volume.
