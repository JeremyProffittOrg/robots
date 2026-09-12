"""Render the doorbot assembly-and-usage video from the CAD, then encode it.

Every frame is an OpenSCAD render of cad/doorbot.scad at a computed set of parameters, with
the caption burned on in PIL. It is a CAD animation, and every frame says so: no hardware has
been built, so there is no footage of one.

    python scripts/render_video.py --preview    # 4 frames into a contact sheet
    python scripts/render_video.py              # the full MP4
"""
import argparse
import hashlib
import json
import math
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from export_cad import EXE, SCAD
from scad_params import ROOT, params

FPS = 12
OUT = ROOT / "output/delivery"
FONT = "C:/Windows/Fonts/arialbd.ttf"
FONT_R = "C:/Windows/Fonts/arial.ttf"
W, H = 1920, 1080
INK = "#0b0f19"
MUTED = "#4b5563"


def smooth(x):
    x = min(1.0, max(0.0, x))
    return (1 - math.cos(math.pi * x)) / 2


def scenes(p, mech):
    """(end_second, part, rotation, extra -D, title, caption, chip) as a function of time."""
    s = mech["summary"]
    close_s = s["close_time_s"]
    return [
        (5, lambda t: ("assembly", f"58,0,{20 + 26 * t / 5}", [],
                       "doorbot", "A door closer, printed in PLA Tough+ and driven by one "
                       "TT motor", "")),
        (12, lambda t: ("exploded", f"{56 + 8 * smooth(t / 7)},0,{28 + 20 * smooth(t / 7)}",
                        [],
                        "Seven printed designs, eight pieces",
                        "Shell, cover, three gears, a door anchor and one magnet pod printed "
                        "twice", "")),
        (20, lambda t: ("section", "58,0,28", [f"spin={t * 300:.1f}"],
                        "One motor, two printed spur stages",
                        f"12T on 48T, then 14T on 42T: {s['ratio']:.0f}:1 onto a "
                        f"{p['drum_r']:.1f} mm drum", "")),
        (26, lambda t: ("drive_train", "58,0,28", [f"spin={t * 300:.1f}"],
                        "The drum reels the cable in",
                        f"{s['cable_travel_mm']:.0f} mm of cable, "
                        f"{s['cable_travel_mm'] / (2 * math.pi * 3.1):.1f} turns, "
                        f"{s['max_tension_n']:.0f} N capped in hardware", "")),
        (32, lambda t: ("installed", "0,0,0", ["door_deg=90"],
                        "Installed: hinge side, behind the door",
                        "The unit and the whole cable run sit on the push side, so the door "
                        "never touches either", "OPEN")),
        (48, lambda t: ("installed", "0,0,0",
                        [f"door_deg={90 * (1 - smooth(t / 15)):.2f}"],
                        "Closing",
                        f"{close_s:.0f} s from wide open. The moment arm stays between "
                        f"{s['arm_min_mm']:.0f} and {s['arm_open_mm']:.0f} mm - it never "
                        f"passes through zero", "CLOSING")),
        (53, lambda t: ("installed", "0,0,0", ["door_deg=0"],
                        "Magnets take the last few millimetres",
                        f"Four D84 discs at the latch edge: "
                        f"{s['magnet_hold_n']:.0f} N of hold at a 2 mm gap", "SHUT")),
        (59, lambda t: ("installed", "0,0,0", ["door_deg=55", "show_hand=1"],
                        "Wave a hand at the target",
                        "Two readings inside 20-250 mm of the engraved ring. One brush past "
                        "does nothing", "CLOSING")),
        (65, lambda t: ("installed", "0,0,0", ["door_deg=55", "show_hand=2"],
                        "Something in the doorway",
                        "It refuses, retries every 19 s for a minute, then buzzes and says "
                        "CLEAR THE WAY", "BLOCKED")),
        (71, lambda t: ("assembly", f"58,0,{28 + 40 * t / 6}", [],
                        "doorbot revision A",
                        f"{s['worst_margin']:.2f}x worst-case torque margin - "
                        f"analysis of the design, not a test of a build", "")),
    ]


def frame_spec(p, mech, index):
    t = index / FPS
    start = 0.0
    for end, fn in scenes(p, mech):
        if t < end:
            return fn(t - start)
        start = end
    return scenes(p, mech)[-1][1](0)


CHIP = {"OPEN": "#1d4ed8", "CLOSING": "#0369a1", "SHUT": "#15803d", "BLOCKED": "#b45309"}


def render_frame(index, tmp, p, mech):
    part, rot, extra, title, caption, chip = frame_spec(p, mech, index)
    raw = tmp / f"raw-{index:05}.png"
    args = [EXE, "-o", str(raw), f"--imgsize={W},{H - 210}", "--colorscheme=Tomorrow",
            "--projection=o", "--viewall", "--autocenter", f"--camera=0,0,0,{rot},0",
            "-D", f'part="{part}"']
    for e in extra:
        args += ["-D", e]
    args.append(str(SCAD))
    result = subprocess.run(args, capture_output=True, text=True, timeout=90)
    if result.returncode or "ERROR" in result.stderr or "WARNING" in result.stderr:
        raise RuntimeError(f"frame {index}: {result.stderr.strip()[:300]}")

    canvas = Image.new("RGB", (W, H), "#ffffff")
    with Image.open(raw) as art:
        canvas.paste(art.convert("RGB"), (0, 130))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, W, 126), fill="#ffffff")
    draw.text((54, 26), title, font=ImageFont.truetype(FONT, 46), fill=INK)
    draw.text((56, 84), caption, font=ImageFont.truetype(FONT_R, 26), fill=MUTED)
    if chip:
        draw.rounded_rectangle((W - 330, 26, W - 54, 96), 14, fill=CHIP.get(chip, MUTED))
        draw.text((W - 316, 42), chip, font=ImageFont.truetype(FONT, 38), fill="#ffffff")
    draw.rectangle((0, H - 76, W, H), fill="#0f172a")
    draw.text((54, H - 62), "CAD ANIMATION - NO PROTOTYPE HAS BEEN BUILT OR TESTED",
              font=ImageFont.truetype(FONT, 26), fill="#ffffff")
    draw.text((54, H - 30),
              "Purchased parts are drawn as dimensional envelopes. Motion timing follows the "
              "analysed operating point, not a measured speed.",
              font=ImageFont.truetype(FONT_R, 19), fill="#e2e8f0")
    canvas.save(tmp / f"frame-{index:05}.png")
    raw.unlink()
    return index


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()
    p = params()
    mech = json.loads((ROOT / "docs/mechanism.json").read_text())
    seconds = scenes(p, mech)[-1][0]
    total = FPS * seconds
    OUT.mkdir(parents=True, exist_ok=True)

    sources = sorted((ROOT / "cad").glob("*.scad")) + [Path(__file__).resolve()]
    before = {str(q): hashlib.sha256(q.read_bytes()).hexdigest() for q in sources}

    with tempfile.TemporaryDirectory(prefix="doorbot-video-") as name:
        tmp = Path(name)
        indices = [30, 200, 500, 700] if args.preview else list(range(total))
        with ThreadPoolExecutor(max_workers=4) as pool:
            jobs = [pool.submit(render_frame, i, tmp, p, mech) for i in indices]
            done = 0
            for f in as_completed(jobs):
                f.result()
                done += 1
                if done % 60 == 0 or done == len(indices):
                    print(f"  rendered {done}/{len(indices)} frames", flush=True)
        if args.preview:
            sheet = Image.new("RGB", (W, H), "#ffffff")
            for n, i in enumerate(indices):
                with Image.open(tmp / f"frame-{i:05}.png") as im:
                    sheet.paste(im.resize((W // 2, H // 2)), ((n % 2) * W // 2,
                                                              (n // 2) * H // 2))
            (ROOT / "tmp").mkdir(exist_ok=True)
            sheet.save(ROOT / "tmp/video-preview.png")
            print("wrote tmp/video-preview.png")
            return
        after = {str(q): hashlib.sha256(q.read_bytes()).hexdigest() for q in sources}
        assert before == after, "the CAD changed while the video was rendering"
        target = OUT / "doorbot-assembly-and-usage.mp4"
        encode = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
             "-i", str(tmp / "frame-%05d.png"), "-c:v", "libx264", "-preset", "medium",
             "-crf", "19", "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart",
             str(target)], capture_output=True, text=True, timeout=900)
        if encode.returncode:
            raise RuntimeError(encode.stderr[-800:])

    probe = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json",
         str(target)]))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    assert int(video["width"]) == W and int(video["height"]) == H, video
    duration = float(probe["format"]["duration"])
    assert abs(duration - seconds) < 0.5, duration
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(target), "-f", "null", "-"],
                   check=True, timeout=600)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (OUT / "video.json").write_text(json.dumps(
        {"file": target.name, "seconds": round(duration, 2), "width": W, "height": H,
         "fps_out": 24, "frames_rendered": total, "bytes": target.stat().st_size,
         "sha256": digest, "simulation": True, "physical_test": False,
         "source_sha256": {str(Path(k).relative_to(ROOT)).replace("\\", "/"): v
                           for k, v in after.items()}}, indent=2))
    print(f"{target} - {duration:.1f} s, {target.stat().st_size / 1e6:.1f} MB")
    print("SHA256 " + digest)


if __name__ == "__main__":
    main()
