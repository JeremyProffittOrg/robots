"""Generate the fable-r2d2 sound set.

Writes twelve original synthesized clips to ``firmware/pi/sounds/*.wav`` and a
catalogue of them to ``audio/catalog.csv``.

Nothing is sampled or copied: every clip is built here from swept oscillators
and envelopes, so the set is original work and reproducible byte for byte.  The
voice is a two oscillator "warble" - a carrier that glides between pitches with
a small amount of frequency modulation on top - which is how the character's
beeps were originally made on an analogue synthesiser.

Format: 22050 Hz, 16 bit signed, mono.  ``aplay`` on Raspberry Pi OS plays these
directly, and ``pygame.mixer`` loads them without conversion.

Run:

    python scripts/generate_audio.py
"""

import csv
import hashlib
import math
import os
import wave

import numpy as np

SAMPLE_RATE = 22050
"""Samples per second for every clip."""

BIT_DEPTH = 16
"""Bits per sample."""

PEAK = 0.86
"""Peak amplitude before conversion to 16 bit, leaving headroom."""

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOUND_DIR = os.path.join(ROOT, "firmware", "pi", "sounds")
CATALOG_PATH = os.path.join(ROOT, "audio", "catalog.csv")


# ---------------------------------------------------------------------------
# Synthesis primitives
# ---------------------------------------------------------------------------


def samples_for(seconds):
    """Number of samples in ``seconds`` of audio."""
    return int(round(seconds * SAMPLE_RATE))


def silence(seconds):
    """A block of silence."""
    return np.zeros(samples_for(seconds), dtype=np.float64)


def glide(points, seconds):
    """Build a per-sample frequency curve in Hz.

    ``points`` is a list of ``(position, hertz)`` pairs with position running
    0..1 across the clip.  Pitch is interpolated geometrically (straight lines
    in log frequency) so a glide sounds even rather than bunching at the top.
    """
    count = samples_for(seconds)
    positions = np.array([point[0] for point in points], dtype=np.float64)
    hertz = np.array([point[1] for point in points], dtype=np.float64)
    axis = np.linspace(0.0, 1.0, count, endpoint=False)
    return np.exp(np.interp(axis, positions, np.log(hertz)))


def oscillator(frequency, seconds, waveform="sine", vibrato_hz=0.0, vibrato_depth=0.0):
    """Render one oscillator with a per-sample frequency curve.

    ``frequency`` is either a constant or an array from :func:`glide`.  Phase is
    accumulated rather than computed from ``t * f`` so a glide has no phase
    discontinuity and therefore no click.
    """
    count = samples_for(seconds)
    if np.isscalar(frequency):
        curve = np.full(count, float(frequency))
    else:
        curve = np.asarray(frequency, dtype=np.float64)[:count]
    if vibrato_depth > 0.0 and vibrato_hz > 0.0:
        axis = np.arange(count, dtype=np.float64) / SAMPLE_RATE
        curve = curve * (1.0 + vibrato_depth * np.sin(2.0 * math.pi * vibrato_hz * axis))
    phase = np.cumsum(2.0 * math.pi * curve / SAMPLE_RATE)
    if waveform == "sine":
        return np.sin(phase)
    if waveform == "triangle":
        return 2.0 / math.pi * np.arcsin(np.sin(phase))
    if waveform == "square":
        # Two-term band limited square: enough edge to sound electronic without
        # the aliasing a hard sign() would fold back down the spectrum.
        return 0.72 * np.sin(phase) + 0.24 * np.sin(3.0 * phase) + 0.12 * np.sin(5.0 * phase)
    if waveform == "saw":
        return (
            0.70 * np.sin(phase)
            + 0.35 * np.sin(2.0 * phase)
            + 0.23 * np.sin(3.0 * phase)
            + 0.17 * np.sin(4.0 * phase)
        )
    raise ValueError("unknown waveform {0}".format(waveform))


def envelope(seconds, attack=0.010, release=0.040, hold=1.0):
    """Amplitude envelope: linear attack, flat hold at ``hold``, cosine release."""
    count = samples_for(seconds)
    curve = np.full(count, float(hold))
    attack_samples = min(samples_for(attack), count)
    release_samples = min(samples_for(release), count - attack_samples)
    if attack_samples > 0:
        curve[:attack_samples] *= np.linspace(0.0, 1.0, attack_samples)
    if release_samples > 0:
        tail = np.linspace(0.0, math.pi / 2.0, release_samples)
        curve[count - release_samples :] *= np.cos(tail)
    return curve


def note(points, seconds, waveform="sine", vibrato_hz=0.0, vibrato_depth=0.0,
         attack=0.010, release=0.040, gain=1.0):
    """One gliding, enveloped note."""
    curve = glide(points, seconds)
    tone = oscillator(curve, seconds, waveform, vibrato_hz, vibrato_depth)
    return tone * envelope(seconds, attack, release) * gain


def sequence(blocks):
    """Concatenate blocks of audio end to end."""
    return np.concatenate(blocks) if blocks else np.zeros(0, dtype=np.float64)


def layer(blocks):
    """Sum blocks on top of each other, padding the short ones with silence."""
    length = max(len(block) for block in blocks)
    total = np.zeros(length, dtype=np.float64)
    for block in blocks:
        total[: len(block)] += block
    return total


def normalise(audio, peak=PEAK):
    """Scale to ``peak`` and apply a short fade at both ends."""
    highest = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if highest > 0.0:
        audio = audio * (peak / highest)
    edge = min(samples_for(0.004), len(audio) // 2)
    if edge > 0:
        audio[:edge] *= np.linspace(0.0, 1.0, edge)
        audio[-edge:] *= np.linspace(1.0, 0.0, edge)
    return audio


def write_wav(path, audio):
    """Write mono 16 bit PCM and return the duration in seconds."""
    data = np.clip(audio, -1.0, 1.0)
    pcm = np.round(data * 32767.0).astype("<i2")
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(BIT_DEPTH // 8)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(pcm.tobytes())
    return len(pcm) / float(SAMPLE_RATE)


def sha256_of(path):
    """Hex SHA-256 of a file."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# The twelve clips
# ---------------------------------------------------------------------------


def clip_greet():
    """Rising three note hello with a warble on the last note."""
    return sequence([
        note([(0.0, 520), (1.0, 700)], 0.12, "square", gain=0.9),
        silence(0.025),
        note([(0.0, 700), (1.0, 940)], 0.12, "square", gain=0.95),
        silence(0.025),
        note([(0.0, 940), (0.5, 1180), (1.0, 1050)], 0.26, "square",
             vibrato_hz=17.0, vibrato_depth=0.05, release=0.09),
    ])


def clip_acknowledge():
    """Short flat double blip: understood."""
    return sequence([
        note([(0.0, 880), (1.0, 880)], 0.07, "square", release=0.02),
        silence(0.035),
        note([(0.0, 1170), (1.0, 1170)], 0.09, "square", release=0.035),
    ])


def clip_alarm():
    """Two tone klaxon, four cycles, with a growl underneath."""
    cycles = []
    for _ in range(4):
        cycles.append(note([(0.0, 780), (1.0, 780)], 0.09, "saw", attack=0.004, release=0.012))
        cycles.append(note([(0.0, 560), (1.0, 560)], 0.09, "saw", attack=0.004, release=0.012))
    siren = sequence(cycles)
    growl = oscillator(glide([(0.0, 96), (1.0, 84)], len(siren) / SAMPLE_RATE),
                       len(siren) / SAMPLE_RATE, "square") * 0.32
    return layer([siren, growl[: len(siren)]])


def clip_question():
    """Short blip then a long rise: is that so?"""
    return sequence([
        note([(0.0, 640), (1.0, 640)], 0.08, "square", release=0.03),
        silence(0.03),
        note([(0.0, 600), (0.6, 900), (1.0, 1420)], 0.30, "square",
             vibrato_hz=11.0, vibrato_depth=0.03, release=0.10),
    ])


def clip_sad():
    """Slow descending wobble."""
    return note([(0.0, 760), (0.35, 620), (0.7, 440), (1.0, 300)], 0.85, "triangle",
                vibrato_hz=6.5, vibrato_depth=0.055, attack=0.03, release=0.30)


def clip_happy():
    """Bright ascending arpeggio with a final flourish."""
    return sequence([
        note([(0.0, 660), (1.0, 660)], 0.07, "square", release=0.02),
        note([(0.0, 880), (1.0, 880)], 0.07, "square", release=0.02),
        note([(0.0, 1100), (1.0, 1100)], 0.07, "square", release=0.02),
        note([(0.0, 1320), (0.5, 1760), (1.0, 1500)], 0.28, "square",
             vibrato_hz=19.0, vibrato_depth=0.06, release=0.11),
    ])


def clip_scan():
    """Repeating sonar sweep, five passes, quietening as it goes."""
    passes = []
    for index in range(5):
        gain = 1.0 - 0.12 * index
        passes.append(note([(0.0, 420), (1.0, 1500)], 0.14, "sine",
                           attack=0.02, release=0.06, gain=gain))
        passes.append(silence(0.06))
    return sequence(passes)


def clip_whistle_up():
    """One clean rising whistle."""
    return note([(0.0, 480), (1.0, 1850)], 0.40, "sine",
                attack=0.03, release=0.12, vibrato_hz=5.0, vibrato_depth=0.015)


def clip_whistle_down():
    """One clean falling whistle."""
    return note([(0.0, 1850), (1.0, 480)], 0.40, "sine",
                attack=0.03, release=0.14, vibrato_hz=5.0, vibrato_depth=0.015)


def clip_chirp_double():
    """Two quick up-chirps, the second higher."""
    return sequence([
        note([(0.0, 900), (1.0, 1500)], 0.06, "square", attack=0.004, release=0.02),
        silence(0.04),
        note([(0.0, 1100), (1.0, 1900)], 0.06, "square", attack=0.004, release=0.02),
    ])


def clip_power_on():
    """Capacitors charging: a long rise with a settling warble at the top."""
    rise = note([(0.0, 90), (0.55, 520), (1.0, 1020)], 0.70, "saw",
                attack=0.12, release=0.05)
    settle = note([(0.0, 1020), (0.4, 1240), (1.0, 1120)], 0.30, "square",
                  vibrato_hz=15.0, vibrato_depth=0.05, release=0.14, gain=0.85)
    return sequence([rise, settle])


def clip_power_off():
    """Everything winding down to nothing."""
    fall = note([(0.0, 1120), (0.35, 780), (1.0, 70)], 0.85, "saw",
                attack=0.02, release=0.40)
    flutter = oscillator(glide([(0.0, 640), (1.0, 60)], 0.85), 0.85, "square")
    flutter = flutter * envelope(0.85, attack=0.02, release=0.55, hold=0.30)
    return layer([fall, flutter])


CLIPS = (
    ("greet", clip_greet),
    ("acknowledge", clip_acknowledge),
    ("alarm", clip_alarm),
    ("question", clip_question),
    ("sad", clip_sad),
    ("happy", clip_happy),
    ("scan", clip_scan),
    ("whistle-up", clip_whistle_up),
    ("whistle-down", clip_whistle_down),
    ("chirp-double", clip_chirp_double),
    ("power-on", clip_power_on),
    ("power-off", clip_power_off),
)


def main():
    """Render every clip, write the WAV files and the catalogue."""
    os.makedirs(SOUND_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(CATALOG_PATH), exist_ok=True)

    rows = []
    for name, builder in CLIPS:
        audio = normalise(builder())
        filename = name + ".wav"
        path = os.path.join(SOUND_DIR, filename)
        seconds = write_wav(path, audio)
        rows.append({
            "name": name,
            "file": "firmware/pi/sounds/" + filename,
            "seconds": "{0:.3f}".format(seconds),
            "sha256": sha256_of(path),
        })
        print("{0:<14} {1:>6} s  {2}".format(name, "{0:.3f}".format(seconds), path))

    with open(CATALOG_PATH, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "file", "seconds", "sha256"])
        writer.writeheader()
        writer.writerows(rows)

    total = sum(float(row["seconds"]) for row in rows)
    print("wrote {0} clips, {1:.2f} s total, catalogue {2}".format(
        len(rows), total, CATALOG_PATH))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
