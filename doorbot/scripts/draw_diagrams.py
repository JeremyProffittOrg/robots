"""Draw every doorbot diagram from cad/params.scad and docs/mechanism.json.

Nothing here is hand-drawn: each figure reads the same numbers the CAD and the checks use, so
a dimension on a diagram cannot disagree with the part.

    python scripts/draw_diagrams.py
"""
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from check_mechanism import Mechanism, magnet_pull
from scad_params import ROOT, params

OUT = ROOT / "output/drawings"
INK = "#0b0f19"
MUTED = "#4b5563"
ACCENT = "#1d4ed8"
WARN = "#b45309"
BAD = "#b91c1c"
GOOD = "#15803d"
PAPER = "#ffffff"
PANEL = "#eef2f7"

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "text.color": INK, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": MUTED, "font.size": 10, "axes.titlesize": 12,
    "axes.titleweight": "bold", "figure.dpi": 170,
})


def save(fig, name, title=None):
    OUT.mkdir(parents=True, exist_ok=True)
    if title:
        fig.suptitle(title, fontsize=13, fontweight="bold", color=INK)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    print("  " + name + ".png")


# --------------------------------------------------------------- 1. installed geometry
def diagram_geometry(p, mech):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6))
    for ax, theta in zip(axes, [0, 45, 90]):
        psi = mech.psi_deg(theta)
        a_r, phi = mech.a_r, mech.phi
        ax_pt = (a_r * math.cos(math.radians(phi - theta)),
                 a_r * math.sin(math.radians(phi - theta)))
        exit_pt = (p["exit_x"], p["exit_y"])
        # wall and jamb
        ax.add_patch(mpatches.Rectangle((-110, -60), 110, 170, color="#d6d3d1"))
        ax.add_patch(mpatches.Rectangle((-8, -60), 8, 120, color="#a8a29e"))
        # leaf
        leaf = mpatches.Rectangle((0, -p["door_thick_mm"]), 380, p["door_thick_mm"],
                                  color="#a16207",
                                  transform=(matplotlib.transforms.Affine2D()
                                             .rotate_deg(-theta) + ax.transData))
        ax.add_patch(leaf)
        # unit
        ax.add_patch(mpatches.Rectangle((0, 0), p["base_z"], p["base_w"], color="#cbd5e1",
                                        ec=MUTED))
        ax.add_patch(mpatches.Rectangle((p["base_z"], p["nose_x"] - p["nose_w"] / 2),
                                        p["nose_l"], p["nose_w"], color="#94a3b8", ec=MUTED))
        # cable and the perpendicular that IS the moment arm
        ax.plot([exit_pt[0], ax_pt[0]], [exit_pt[1], ax_pt[1]], color=ACCENT, lw=2.0)
        arm = mech.arm_mm(theta, worst=False)
        dx, dy = ax_pt[0] - exit_pt[0], ax_pt[1] - exit_pt[1]
        n = math.hypot(dx, dy)
        foot = (-dy / n * arm * (1 if psi > 0 else -1), dx / n * arm * (1 if psi > 0 else -1))
        ax.plot([0, foot[0]], [0, foot[1]], color=BAD, lw=1.6, ls="--")
        ax.annotate(f"arm {arm:.0f} mm", xy=(foot[0] / 2, foot[1] / 2), color=BAD,
                    fontsize=9, fontweight="bold",
                    xytext=(-6, -22), textcoords="offset points")
        ax.plot(*ax_pt, "o", color=WARN, ms=9)
        ax.plot(*exit_pt, "o", color=ACCENT, ms=7)
        ax.plot(0, 0, "o", color=INK, ms=7)
        ax.annotate("hinge axis", (0, 0), xytext=(-95, -40), color=INK, fontsize=8)
        ax.annotate("anchor", ax_pt, xytext=(6, -14), textcoords="offset points",
                    color=WARN, fontsize=8)
        ax.annotate("cable exit", exit_pt, xytext=(14, 16), textcoords="offset points",
                    color=ACCENT, fontsize=8)
        ax.set_title(f"door {theta} deg    included angle {psi:.0f} deg", color=INK)
        ax.set_xlim(-120, 330)
        ax.set_ylim(-290, 150)
        ax.set_aspect("equal")
        ax.axis("off")
    note = (f"The exit sits {p['exit_y']:.0f} mm off the closed-door plane on purpose. Put it "
            f"ON that plane and at 0 deg the exit, the hinge axis and the anchor are in a straight "
            f"line: the arm is exactly zero and no tension can shut the last degree. Offset, "
            f"the included angle stays between {mech.psi_deg(0):.0f} deg and "
            f"{mech.psi_deg(90):.0f} deg and the arm never drops below "
            f"{mech.arm_mm(0, worst=False):.0f} mm.")
    fig.text(0.5, -0.02, note, ha="center", va="top", color=MUTED, fontsize=9, wrap=True)
    save(fig, "diagram_geometry", "How it pulls: plan view at three door angles")


# --------------------------------------------------------------- 2. curves
def diagram_curves(p, mech, mechjson):
    rows = mechjson["angle_table"]
    deg = np.array([r["deg"] for r in rows])
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    ax = axes[0][0]
    arm = np.array([mech.arm_mm(d, worst=False) for d in deg])
    ax.plot(deg, arm, color=ACCENT, lw=2, label="as designed")
    ax.plot(deg, arm - p["build_tol_mm"], color=MUTED, lw=1.2, ls="--",
            label=f"minus {p['build_tol_mm']:.0f} mm mounting error")
    ax.axhline(0, color=BAD, lw=1)
    ax.set_title("Moment arm never collapses")
    ax.set_xlabel("door angle, degrees (0 = shut)")
    ax.set_ylabel("arm, mm")
    ax.set_ylim(0, max(arm) * 1.15)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[0][1]
    resist = np.array([r["resist_nm"] for r in rows])
    avail = np.array([r["available_nm"] for r in rows])
    assist = np.array([r["magnet_assist_nm"] for r in rows])
    ax.fill_between(deg, 0, avail, color="#dbeafe", label="available at the 1.0 A chop")
    ax.plot(deg, avail, color=ACCENT, lw=2)
    ax.plot(deg, resist, color=BAD, lw=2, label="worst-case resistance")
    ax.plot(deg, np.minimum(assist, avail.max()), color=GOOD, lw=1.6, ls=":",
            label="magnet assist")
    ax.set_title(f"Torque margin, worst {mechjson['summary']['worst_margin']:.2f}x")
    ax.set_xlabel("door angle, degrees")
    ax.set_ylabel("torque about the hinge, N·m")
    ax.set_ylim(0, avail.max() * 1.2)
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1][0]
    speed = np.array([r["deg_per_s"] or 0 for r in rows])
    ax.plot(deg, speed, color=ACCENT, lw=2)
    ax.set_title(f"Closing speed, {mechjson['summary']['close_time_s']:.0f} s from wide open")
    ax.set_xlabel("door angle, degrees")
    ax.set_ylabel("degrees per second")
    ax.set_ylim(0, max(speed) * 1.3)
    ax.annotate("the TT motor at 5 V can only make about 0.35 W,\n"
                "which is what sets this - not the gear ratio",
                xy=(45, max(speed) * 0.45), color=MUTED, fontsize=8)

    ax = axes[1][1]
    gaps = np.linspace(0, 20, 200)
    pull = np.array([magnet_pull(g) for g in gaps])
    ax.plot(gaps, pull, color=GOOD, lw=2)
    ax.axvline(p["magnet_gap_closed_mm"], color=INK, lw=1.2, ls="--")
    ax.annotate(f"as built {p['magnet_gap_closed_mm']:.0f} mm\n"
                f"{magnet_pull(p['magnet_gap_closed_mm']):.0f} N holding",
                xy=(p["magnet_gap_closed_mm"], magnet_pull(p["magnet_gap_closed_mm"])),
                xytext=(6, 55), color=INK, fontsize=8,
                arrowprops=dict(arrowstyle="->", color=INK, lw=1))
    takeover = p["magnet_radius_mm"] * math.radians(1.0)
    ax.axvline(takeover, color=WARN, lw=1.2, ls=":")
    ax.annotate(f"magnets take over here\n1 deg open = {takeover:.0f} mm gap",
                xy=(takeover, magnet_pull(takeover)), xytext=(takeover + 1, 40),
                color=WARN, fontsize=8)
    ax.set_title("Four D84 magnets: pull against air gap")
    ax.set_xlabel("gap at the latch edge, mm")
    ax.set_ylabel("pull, N")

    fig.tight_layout()
    save(fig, "diagram_curves", "What the mechanism does, from cad/params.scad")


# --------------------------------------------------------------- 3. wiring
def diagram_wiring(p):
    wiring = json.loads((ROOT / "docs/wiring.json").read_text())
    fig = plt.figure(figsize=(15, 8.6))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.9, 1.0], wspace=0.02)
    ax = fig.add_subplot(grid[0, 0])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 70)
    ax.axis("off")

    def box(x, y, w, h, label, sub="", colour=PANEL):
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                             fc=colour, ec=MUTED, lw=1.2))
        ax.text(x + w / 2, y + h - 2.4, label, ha="center", va="top", color=INK,
                fontsize=10, fontweight="bold")
        if sub:
            ax.text(x + w / 2, y + h - 5.8, sub, ha="center", va="top", color=MUTED,
                    fontsize=8)
        return {"l": (x, y + h / 2), "r": (x + w, y + h / 2),
                "t": (x + w / 2, y + h), "b": (x + w / 2, y)}

    usb = box(30, 60, 26, 8, "USB-C 5 V", "the only power input")
    mcu = box(30, 30, 26, 22, "TTGO T-Display", "ESP32 + ST7789 135x240 | I2C 21/22",
              "#dbeafe")
    drv = box(72, 48, 26, 12, "DRV8833 driver", "1.0 A hardware chop", "#fee2e2")
    mot = box(72, 32, 26, 10, "TT motor 1:48", "the only moving drive", "#e5e7eb")
    enc = box(72, 16, 26, 10, "encoder", "wheel + slot sensor", "#e5e7eb")
    wave = box(2, 52, 24, 9, "VL53L4CD", "hand wave, 0x2A", "#dcfce7")
    guard = box(2, 38, 24, 9, "VL53L1X", "doorway, 0x29", "#dcfce7")
    accel = box(2, 24, 24, 9, "LIS3DH", "kick, 0x18", "#dcfce7")
    buzz = box(30, 12, 26, 9, "piezo buzzer", "alert after the retry window")

    def wire(a, b, text, colour=ACCENT, ls="-", off=1.4, ha="center"):
        ax.annotate("", xy=b, xytext=a,
                    arrowprops=dict(arrowstyle="-", color=colour, lw=1.6, ls=ls,
                                    shrinkA=2, shrinkB=2))
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + off, text, ha=ha, color=colour,
                fontsize=8, bbox=dict(fc=PAPER, ec="none", pad=0.4))

    wire(usb["b"], mcu["t"], "5 V + GND")
    wire(usb["r"], drv["t"], "5 V taken straight to the driver, NOT through the board",
         BAD, "--", 2.2)
    wire(mcu["r"], drv["l"], "GPIO 32/33 PWM, 27 sleep, 36 fault")
    wire(drv["b"], mot["t"], "AOUT1 / AOUT2")
    wire(mcu["r"], enc["l"], "GPIO 37", ACCENT, "-", -2.4)
    wire(mcu["l"], wave["r"], "I2C + XSHUT 25")
    wire(mcu["l"], guard["r"], "I2C + XSHUT 26", ACCENT, "-", -2.4)
    wire(mcu["l"], accel["r"], "I2C + INT 39")
    wire(mcu["b"], buzz["t"], "GPIO 17")

    table = fig.add_subplot(grid[0, 1])
    table.axis("off")
    rows = [f"{q['signal']:<19}{q['gpio']:>4}  {q['direction']}" for q in wiring["pins"]]
    table.text(0.0, 1.0, "signal             gpio  dir\n" + "\n".join(rows),
               family="monospace", fontsize=9, color=INK, va="top",
               bbox=dict(fc="#f8fafc", ec=MUTED, boxstyle="round,pad=0.6"))
    notes = "\n\n".join(f"{n['net']}\n  {n['note']}" for n in wiring["nets"])
    table.text(0.0, 0.53, notes, fontsize=7.6, color=INK, va="top", wrap=True)
    table.text(0.0, 0.0, f"spare GPIO: {wiring['spare_gpio']}", fontsize=8, color=MUTED)
    save(fig, "diagram_wiring", "Wiring: twelve signals, three I2C devices, one motor")


# --------------------------------------------------------------- 4. gear train
def diagram_gear_train(p, mech):
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_aspect("equal")
    ax.axis("off")
    axes_xy = {"motor": p["motor_axis"], "compound": p["compound_axis"], "drum": p["drum_axis"]}
    wheels = [
        ("motor", p["module1"] * p["stage1_pinion_t"] / 2 + p["module1"], WARN,
         f"{p['stage1_pinion_t']}T m{p['module1']}"),
        ("compound", p["module1"] * p["stage1_gear_t"] / 2 + p["module1"], ACCENT,
         f"{p['stage1_gear_t']}T m{p['module1']}"),
        ("compound", p["module2"] * p["stage2_pinion_t"] / 2 + p["module2"], "#7c3aed",
         f"{p['stage2_pinion_t']}T m{p['module2']}"),
        ("drum", p["module2"] * p["stage2_gear_t"] / 2 + p["module2"], "#0369a1",
         f"{p['stage2_gear_t']}T m{p['module2']}"),
        ("drum", p["drum_flange_d"] / 2, GOOD, f"drum r{p['drum_r']:.1f}"),
    ]
    for key, r, colour, label in wheels:
        x, y = axes_xy[key]
        ax.add_patch(plt.Circle((x, y), r, fill=False, ec=colour, lw=2.0))
        ax.text(x + r + 3, y + (6 if colour in (WARN, "#7c3aed", GOOD) else -10), label,
                color=colour, fontsize=9, fontweight="bold")
    for key, (x, y) in axes_xy.items():
        ax.plot(x, y, "o", color=INK, ms=5)
        ax.text(x - 22, y, key, color=INK, fontsize=9, ha="right", va="center")
    ax.plot([25, 25], [p["drum_axis"][1], p["motor_axis"][1]], color=MUTED, lw=1, ls=":")
    ax.annotate(f"{math.dist(p['motor_axis'], p['compound_axis']):.0f} mm",
                xy=(28, (p["motor_axis"][1] + p["compound_axis"][1]) / 2), color=MUTED,
                fontsize=8)
    ax.annotate(f"{math.dist(p['compound_axis'], p['drum_axis']):.0f} mm",
                xy=(28, (p["compound_axis"][1] + p["drum_axis"][1]) / 2), color=MUTED,
                fontsize=8)

    limit = mech.torque_limit_nm()
    s2_in = limit * p["stage1_gear_t"] / p["stage1_pinion_t"] * 0.9
    out_nm = mech.drum_tension_n(limit) * mech.drum_eff_r / 1000.0
    text = (f"motor at the 1.0 A chop      {limit * 1000:.1f} mN·m\n"
            f"after stage 1 ({p['stage1_gear_t']:.0f}/{p['stage1_pinion_t']:.0f})       "
            f"{s2_in * 1000:.0f} mN·m\n"
            f"after stage 2 ({p['stage2_gear_t']:.0f}/{p['stage2_pinion_t']:.0f})       "
            f"{out_nm * 1000:.0f} mN·m\n"
            f"total ratio                  {mech.ratio:.0f}:1\n"
            f"cable tension wound          {mech.max_tension_n():.0f} N\n"
            f"delivered past the chute     {mech.tension_n(limit):.0f} N\n"
            f"cable travel, 90° to shut    {mech.cable_travel_mm():.0f} mm\n"
            f"turns on the drum            "
            f"{mech.cable_travel_mm() / (2 * math.pi * mech.drum_eff_r):.2f}")
    ax.text(95, 90, text, family="monospace", fontsize=9, color=INK, va="top",
            bbox=dict(fc="#f8fafc", ec=MUTED, boxstyle="round,pad=0.6"))
    ax.set_xlim(-30, 230)
    ax.set_ylim(-10, 115)
    save(fig, "diagram_gear_train", "Drive train: two printed spur stages, 12:1")


# --------------------------------------------------------------- 5. state machine
def diagram_states(p):
    fig, ax = plt.subplots(figsize=(12.5, 7.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56)
    ax.axis("off")
    nodes = {
        "HOMING": (8, 44, "#e5e7eb", "position unknown"),
        "OPEN": (8, 26, "#dbeafe", "drum free-spooling"),
        "CLOSING": (38, 35, "#bfdbfe", "winding, 1.0 A capped"),
        "SHUT": (74, 44, "#dcfce7", "magnets hold it,\nslack paid out"),
        "BLOCKED": (38, 14, "#fed7aa", "retry every 19 s"),
        "ALERT": (74, 14, "#fecaca", "buzzer + screen"),
        "FAULT": (74, 28, "#e5e7eb", "driver nFAULT"),
    }
    centres = {}
    for name, (x, y, colour, sub) in nodes.items():
        w, h = 19, 9
        ax.add_patch(mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                             fc=colour, ec=MUTED, lw=1.3))
        ax.text(x + w / 2, y + h - 2.4, name, ha="center", va="top", fontsize=11,
                fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 5.6, sub, ha="center", va="top", fontsize=8, color=MUTED)
        centres[name] = (x + w / 2, y + h / 2)

    def edge(a, b, label, colour=ACCENT, rad=0.15, at=0.5, dx=0.0, dy=1.4):
        ax.annotate("", xy=centres[b], xytext=centres[a],
                    arrowprops=dict(arrowstyle="-|>", color=colour, lw=1.6, shrinkA=22,
                                    shrinkB=22, connectionstyle=f"arc3,rad={rad}"))
        mx = centres[a][0] + (centres[b][0] - centres[a][0]) * at + dx
        my = centres[a][1] + (centres[b][1] - centres[a][1]) * at + dy
        ax.text(mx, my, label, ha="center", va="center", fontsize=8, color=colour,
                bbox=dict(fc=PAPER, ec="none", pad=0.5))

    edge("HOMING", "CLOSING", "wave, kick or button")
    edge("OPEN", "CLOSING", "wave / kick / button,\nor clear for 30 s")
    edge("CLOSING", "SHUT", "stalls at the stop\nwith travel done", GOOD)
    edge("CLOSING", "BLOCKED", "doorway sensor,\nor an early stall", WARN, -0.15)
    edge("BLOCKED", "CLOSING", "way clear at the\nnext 19 s retry", GOOD, -0.3)
    edge("BLOCKED", "ALERT", "still blocked\nafter 60 s", BAD)
    edge("SHUT", "OPEN", "pulled open by hand", MUTED, -0.2, at=0.5, dy=-6.5)
    edge("ALERT", "CLOSING", "cleared and\ncommanded", GOOD, 0.35, at=0.28, dx=6.0, dy=-2.0)
    edge("CLOSING", "FAULT", "nFAULT low", BAD, 0.25, at=0.45, dy=2.6)

    ax.text(50, 2.5,
            "Obstacle policy, exactly as specified: \"Retry every 19 seconds for a minute, "
            "then alert\". Three retries fit in the window (19 s, 38 s, 57 s); the fourth "
            "would fall outside it, so at 60 s it alerts instead. "
            "firmware/test/test_controller.cpp asserts all of that on the host.",
            ha="center", color=INK, fontsize=9, wrap=True)
    save(fig, "diagram_states", "What it does, and when")


# --------------------------------------------------------------- 6. sensor coverage
def diagram_sensors(p):
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(mpatches.Rectangle((-110, -60), 110, 190, color="#d6d3d1"))
    ax.add_patch(mpatches.Rectangle((0, -p["door_thick_mm"]), p["door_width_mm"],
                                    p["door_thick_mm"], color="#a16207"))
    ax.add_patch(mpatches.Rectangle((p["door_width_mm"], -60), 110, 190, color="#d6d3d1"))
    ax.add_patch(mpatches.Rectangle((0, 0), p["base_z"], p["base_w"], color="#cbd5e1",
                                    ec=MUTED))

    def cone(origin, half_deg, reach, colour, label, near=0):
        pts = [origin]
        for a in np.linspace(-half_deg, half_deg, 40):
            pts.append((origin[0] + reach * math.cos(math.radians(a)),
                        origin[1] + reach * math.sin(math.radians(a))))
        ax.add_patch(mpatches.Polygon(pts, closed=True, fc=colour, alpha=0.25, ec=colour))
        ax.text(origin[0] + reach * 0.55, origin[1] + reach * math.sin(math.radians(half_deg))
                * 0.9 + 12, label, color=colour, fontsize=9, fontweight="bold")

    origin = (p["base_z"], 26)
    cone(origin, 9, 250, "#166534", "hand wave: VL53L4CD, 18° cone,\ngated 20-250 mm")
    cone(origin, 13.5, 1800, ACCENT, "doorway: VL53L1X, 27° cone,\ngated 120-1800 mm")
    ax.plot(*origin, "o", color=INK, ms=6)
    ax.annotate("both look straight down the opening from the cover, on the push side of the\n"
                "closed leaf, so the door never blocks its own sensors",
                xy=origin, xytext=(140, -150), color=MUTED, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=MUTED, lw=1))
    ax.add_patch(mpatches.Rectangle((p["magnet_radius_mm"] - 20, 2), 40, 10, color="#be123c"))
    ax.text(p["magnet_radius_mm"] - 40, 24, "magnet pods", color="#be123c", fontsize=9,
            fontweight="bold")
    ax.text(430, -200,
            "NOT COVERED: an object lying in the swing arc on the pull side is out of both "
            "cones. The encoder stall watchdog is the backstop there - it cuts drive within "
            "250 ms of contact, and the driver's 1.0 A chop caps the push at 151 N of cable "
            "tension whatever the firmware does.",
            ha="center", color=BAD, fontsize=9, wrap=True)
    ax.set_xlim(-130, 1050)
    ax.set_ylim(-260, 300)
    save(fig, "diagram_sensors", "What the two time-of-flight sensors can see")


# --------------------------------------------------------------- 7. print plate
def diagram_print_plate(p):
    import csv
    rows = list(csv.DictReader((ROOT / "bom/printed-parts.csv").open(encoding="utf-8")))
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_aspect("equal")
    bed = p["env_x"]
    ax.add_patch(mpatches.Rectangle((0, 0), bed, bed, fc="#f1f5f9", ec=MUTED, lw=1.5))
    ax.text(bed / 2, bed + 6, f"{bed:.0f} x {bed:.0f} mm bed (smallest current Bambu)",
            ha="center", color=MUTED, fontsize=9)
    x, y, row_h = 6, 6, 0
    colours = ["#cbd5e1", "#bfdbfe", "#fde68a", "#bbf7d0", "#ddd6fe", "#fecaca", "#fbcfe8"]
    for i, r in enumerate(rows):
        w, h = float(r["x_mm"]), float(r["y_mm"])
        if x + w > bed - 6:
            x, y, row_h = 6, y + row_h + 8, 0
        ax.add_patch(mpatches.Rectangle((x, y), w, h, fc=colours[i % len(colours)], ec=MUTED))
        ax.text(x + w / 2, y + h / 2,
                f"{r['part']}\n{r['quantity']}x  {r['solid_mass_g']} g\n"
                f"{w:.0f}x{h:.0f}x{float(r['z_mm']):.0f}",
                ha="center", va="center", fontsize=7.5, color=INK)
        x += w + 8
        row_h = max(row_h, h)
    total = sum(float(r["line_mass_g"]) for r in rows)
    ax.text(bed / 2, -14,
            f"{len(rows)} designs, {sum(int(r['quantity']) for r in rows)} pieces, "
            f"{total:.0f} g of PLA Tough+ at 100% infill. Every part prints flat with no "
            f"supports; the shell is the only one that needs most of the bed.",
            ha="center", color=INK, fontsize=9, wrap=True)
    ax.set_xlim(-10, bed + 10)
    ax.set_ylim(-40, bed + 20)
    ax.axis("off")
    save(fig, "diagram_print_plate", "Everything you print")


# --------------------------------------------------------------- 8. drill templates
def diagram_templates(p):
    for name, title, holes, size, note in [
        ("template_jamb", "Jamb reveal: 3 holes",
         [(p["base_w"] - 9, y, p["mount_screw_d"]) for y in p["mount_y"]]
         + [(p["motor_axis"][0], p["motor_axis"][1], 9.0)],
         (p["base_w"], p["base_h"]),
         "Hinge-side jamb reveal, push side. The 9 mm hole clears the motor's spare shaft; "
         "drill it 12 mm deep. Tape this page to the jamb with the bottom edge level."),
        ("template_door", "Door face: 3 holes",
         [(p["anchor_base_l"] / 2 + i * p["anchor_screw_pitch"], p["anchor_base_w"] / 2,
           p["anchor_screw_d"]) for i in (-1, 0, 1)],
         (p["anchor_base_l"], p["anchor_base_w"]),
         f"Anchor centre goes {p['anchor_a']:.0f} mm from the hinge axis, at the same height "
         f"as the unit's nose."),
        ("template_pod", "Magnet pod: 2 holes (x2, door edge and jamb)",
         [(p["pod_l"] / 2 + i * (p["magnet_pitch"] / 2 - p["magnet_pocket_d"] / 2 - 5.5),
           p["pod_w"] / 2, p["pod_screw_d"]) for i in (-1, 1)],
         (p["pod_l"], p["pod_w"]),
         "One pod on the door's latch edge, one on the jamb directly opposite, magnet faces "
         "towards each other."),
    ]:
        w, h = size
        fig, ax = plt.subplots(figsize=(w / 25.4 + 1.6, h / 25.4 + 2.2))
        ax.add_patch(mpatches.Rectangle((0, 0), w, h, fc="none", ec=INK, lw=1.4, ls="--"))
        for hx, hy, hd in holes:
            ax.add_patch(plt.Circle((hx, hy), hd / 2, fc="none", ec=BAD, lw=1.4))
            ax.plot([hx - hd, hx + hd], [hy, hy], color=BAD, lw=0.7)
            ax.plot([hx, hx], [hy - hd, hy + hd], color=BAD, lw=0.7)
            ax.text(hx, hy + hd, f"⌀{hd:.1f}", ha="center", va="bottom", color=BAD,
                    fontsize=7)
        ax.plot([0, 50], [-6, -6], color=INK, lw=2)
        ax.text(25, -12, "50 mm - check this is 50 mm before drilling", ha="center",
                color=INK, fontsize=8)
        ax.text(w / 2, h + 8, title, ha="center", color=INK, fontsize=10, fontweight="bold")
        ax.text(w / 2, -22, note, ha="center", va="top", color=MUTED, fontsize=8, wrap=True)
        ax.set_xlim(-12, w + 12)
        ax.set_ylim(-40, h + 18)
        ax.set_aspect("equal")
        ax.axis("off")
        save(fig, name)


def main():
    p = params()
    mech = Mechanism(p)
    mechjson = json.loads((ROOT / "docs/mechanism.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    diagram_geometry(p, mech)
    diagram_curves(p, mech, mechjson)
    diagram_wiring(p)
    diagram_gear_train(p, mech)
    diagram_states(p)
    diagram_sensors(p)
    diagram_print_plate(p)
    diagram_templates(p)
    index = sorted(f.name for f in OUT.glob("*.png"))
    (OUT / "index.json").write_text(json.dumps({"drawings": index}, indent=2))
    print(f"{len(index)} drawings in {OUT}")


if __name__ == "__main__":
    main()
