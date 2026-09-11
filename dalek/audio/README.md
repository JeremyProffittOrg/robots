# Original robot voice collection

The 24 MP3 files are in `../firmware/data/audio/`. They are included there so the same files can be uploaded to the robot's LittleFS flash filesystem. `catalog.json` records each exact transcript, duration, size and SHA-256. `phrases.csv` is the editable source list.

These are newly synthesized robot lines, not audio extracted from Doctor Who, a BBC recording, or a particular actor's performance. The text was written for this build. The source is the installed Microsoft David Desktop voice through Windows System.Speech. A low oscillator adds a metallic sound. The collection includes brief familiar words such as “Exterminate” alongside original control and character phrases. No downloaded sound samples are used.

The supplied format is mono MP3, 22,050 Hz, 32 kbit/s. Playback uses the ESP32 and the MAX98357A amplifier in the body. The speaker and all its wires stay stationary during head rotation. The controller lists files automatically. The files are manual sound buttons; the presence of a warning phrase does not mean firmware automatically plays that warning.

To recreate the collection on this Windows machine:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File C:/dev/robots/dalek/scripts/generate_voices.ps1
```

This requires the installed Microsoft desktop voice, Python with NumPy, and FFmpeg/FFprobe on PATH. It runs once. It registers no scheduled task. It creates a unique temporary WAV directory and removes only that directory when finished. The persistent outputs are the MP3s and catalog.

To replace a line, edit its row in `phrases.csv`, regenerate, rebuild the filesystem with PlatformIO, and upload that filesystem while actuator power is off. The waveform effect uses a 0.86 playback-rate multiplier, nonlinear amplitude compression, 30 Hz ring modulation, a quiet 45 ms echo, and a 170–3400 Hz frequency band. Peak amplitude is limited before MP3 encoding. Start with amplifier volume low and check the speaker for distortion.

To add your own recordings, use lowercase filenames with letters, numbers, underscores or hyphens and the `.mp3` suffix. Keep the entire flash filesystem inside its partition. Use only recordings you have permission to use. Character names and third-party voice/tool software retain their respective ownership; this package does not grant rights in third-party material.
