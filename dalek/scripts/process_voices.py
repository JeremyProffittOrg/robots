"""Make original robotic MP3s from locally synthesized PCM, never TV recordings."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--voice', required=True)
    args = parser.parse_args()
    ffmpeg = shutil.which('ffmpeg')
    ffprobe = shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise SystemExit('FFmpeg and FFprobe must be on PATH.')
    destination = ROOT / 'firmware/data/audio'
    destination.mkdir(parents=True, exist_ok=True)
    catalog = []
    with (ROOT / 'audio/phrases.csv').open(newline='', encoding='utf-8') as handle:
        phrases = list(csv.DictReader(handle))
    for phrase in phrases:
        wav_path = args.input / (Path(phrase['file']).stem + '.wav')
        with wave.open(str(wav_path), 'rb') as source:
            if source.getnchannels() != 1 or source.getsampwidth() != 2:
                raise ValueError('Expected mono 16-bit WAV.')
            rate = source.getframerate()
            signal = np.frombuffer(source.readframes(source.getnframes()), dtype='<i2').astype(np.float64) / 32768
        # Slow and lower the stock voice, then use a 30 Hz oscillator for a metallic texture.
        signal = np.interp(np.arange(0, len(signal) - 1, 0.86), np.arange(len(signal)), signal)
        time = np.arange(len(signal)) / rate
        signal = np.tanh(signal * 3.0) * (0.30 + 0.70 * np.sin(2 * np.pi * 30 * time))
        echo = int(rate * 0.045)
        signal[echo:] += signal[:-echo].copy() * 0.16
        peak = np.max(np.abs(signal))
        if peak == 0:
            raise ValueError('Silent source: ' + phrase['file'])
        signal *= 0.78 / peak
        pcm = (np.clip(signal, -1, 1) * 32767).astype('<i2').tobytes()
        output = destination / phrase['file']
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-f', 's16le',
                        '-ar', str(rate), '-ac', '1', '-i', 'pipe:0', '-af',
                        'highpass=f=170,lowpass=f=3400', '-ar', '22050', '-ac', '1',
                        '-codec:a', 'libmp3lame', '-b:a', '32k', '-map_metadata', '-1',
                        '-metadata', 'title=' + phrase['text'], str(output)], input=pcm, check=True)
        probe = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-show_format',
                         '-show_streams', '-of', 'json', str(output)], text=True))
        stream = probe['streams'][0]
        assert stream['codec_name'] == 'mp3' and stream['channels'] == 1 and int(stream['sample_rate']) == 22050
        subprocess.run([ffmpeg, '-v', 'error', '-i', str(output), '-f', 'null', '-'], check=True)
        catalog.append({**phrase, 'duration_seconds': round(float(probe['format']['duration']), 3),
                        'bytes': output.stat().st_size, 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
    if sum(item['bytes'] for item in catalog) > 1_500_000:
        raise ValueError('Audio exceeds intended filesystem allowance.')
    result = {'source': 'Original text, local System.Speech synthesis; no sampled programme audio.',
              'voice': args.voice, 'effects': '0.86x playback; tanh drive; 30Hz ring modulation; 45ms echo; 170-3400Hz band limit',
              'format': 'MP3 mono 22050Hz 32kbps', 'clips': catalog}
    (ROOT / 'audio/catalog.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f"PASS: {len(catalog)} MP3s decoded; {sum(item['bytes'] for item in catalog)} bytes; "
          f"{sum(item['duration_seconds'] for item in catalog):.1f} seconds")


if __name__ == '__main__':
    main()
