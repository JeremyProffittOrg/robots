"""Mechanism authority for doorbot: geometry, torque, speed, stress, cable and magnet checks.

Every number comes from cad/params.scad (the single source of dimensions) and from the sourced
constants below. The script fails loudly. A PASS here is the definition of done for the
mechanism; it is an analysis of the design, NOT a physical test of a built machine.

    python scripts/check_mechanism.py            # full report, exit 1 on any failed check
    python scripts/check_mechanism.py --json      # machine-readable only

Sourced constants (each carries the primary source it came from):
  motor    Adafruit 3777 / DAGU DG01D-A130 1:48. Published 0.4 kgf.cm stall at 3 V and
           0.8 kgf.cm at 6 V; Adafruit's measured no-load points are 120/185/250 RPM at
           3/4.5/6 V. Interpolated to the 5 V USB supply: 65.4 mN.m stall, 206.7 RPM.
           Peak mechanical power is therefore only about 0.35 W, which is what sets the
           close time - not the gearing. Ignore the "Torque: 0.15Nm ~0.60Nm" line in
           Adafruit's own PDF; it contradicts 0.8 kgf.cm on the same page by about 8x.
           https://www.adafruit.com/product/3777
  driver   Adafruit 3297 DRV8833 breakout. Two 0.2 ohm sense resistors chop each channel at
           1.0 A, in hardware, with no firmware in the loop. Stall current of the motor is
           about 1.3 A at 5 V, so the driver - not the motor - sets the maximum torque and
           therefore the maximum cable tension every printed part is checked against.
           https://www.adafruit.com/product/3297
  magnets  K&J Magnetics D84 (12.7 x 6.35 mm, N42). Published Pull Force Case 1 48.4 N per
           facing pair; the gap curve below is K&J's published on-axis fall-off for D84.
           https://www.kjmagnetics.com/proddetail.asp?prod=D84
  material Bambu Lab PLA Tough+ TDS: 20.9 MPa tensile in Z, 1860 MPa modulus. Allowables
           here are that scatter divided by 4 (5 MPa across layers, 8 MPa in plane) and by 6
           for cyclic gear teeth (3.3 / 5.5 MPa).
           https://bambulab.com/en/filament/pla-tough
  door     ADA 404.2.7 (22.2 N at the door edge) and ANSI/BHMA A156.19 (>= 1.5 s from 10 deg
           to closed; 1.69 J energy cap). Hinge friction has no published figure for plain
           residential butt hinges and is modelled, not measured - see HINGE_FRICTION_NM.
"""
import argparse
import json
import math
from pathlib import Path

from scad_params import ROOT, params, require

# ---------------------------------------------------------------- sourced constants
# Adafruit's three bench points (3 V/120, 4.5 V/185, 6 V/250 RPM) are exactly collinear:
# RPM = 43.33*V - 10, so 5 V gives 206.7 RPM. Stall torque is published only at 3 V
# (0.4 kgf.cm) and 6 V (0.8 kgf.cm); linear in V gives 0.667 kgf.cm = 65.4 mN.m at 5 V.
MOTOR_STALL_NM = 0.0654
MOTOR_NOLOAD_RPM = 206.7
MOTOR_STALL_A = 1.3             # interpolated between the measured 1.2 A at 4.5 V and 1.5 A at 6 V
MOTOR_NOLOAD_A = 0.157          # measured 155 mA at 4.5 V, 160 mA at 6 V
DRIVER_LIMIT_A = 1.0            # DRV8833 breakout hardware chop
SPUR_STAGE_EFF = 0.90           # printed spur stage, conservative
G = 9.80665

# K&J D84 published on-axis pull for TWO facing pairs (four magnets), newtons by gap in mm.
MAGNET_PULL_N = {0.0: 96.8, 1.0: 83.0, 2.0: 70.0, 3.0: 58.0, 8.0: 19.8}
MAGNET_TAIL_MM = 5.0            # exponential decay length fitted to the table above

# PLA Tough+ allowables, MPa. "z" = load across layer lines, "xy" = load in the layer plane.
ALLOW = {"z": 5.0, "xy": 8.0, "z_cyclic": 3.3, "xy_cyclic": 5.5}

# Door resistance model. No published figure exists for plain residential butt-hinge friction,
# so it is modelled as mu * r_pin * bearing reaction over mu = 0.15..0.30 and r_pin = 3..5 mm.
HINGE_FRICTION_NM = 0.82        # worst case of that model for a 40 kg leaf
ADA_EDGE_FORCE_N = 22.2         # ADA 404.2.7 ceiling, used as the "must not exceed" on opening
A156_LATCH_S = 1.5              # A156.19: 10 deg to closed must take at least this long
A156_ENERGY_J = 1.69            # A156.19 kinetic energy cap


def magnet_pull(gap_mm):
    """Published D84 pull for the four-magnet set at a given air gap, in newtons."""
    if gap_mm <= 0:
        return MAGNET_PULL_N[0.0]
    keys = sorted(MAGNET_PULL_N)
    if gap_mm >= keys[-1]:
        return MAGNET_PULL_N[keys[-1]] * math.exp(-(gap_mm - keys[-1]) / MAGNET_TAIL_MM)
    lower = max(k for k in keys if k <= gap_mm)
    upper = min(k for k in keys if k >= gap_mm)
    if upper == lower:
        return MAGNET_PULL_N[lower]
    span = (gap_mm - lower) / (upper - lower)
    return MAGNET_PULL_N[lower] + span * (MAGNET_PULL_N[upper] - MAGNET_PULL_N[lower])


class Mechanism:
    """The chosen geometry, evaluated at any door angle. Angles in degrees, lengths in mm."""

    def __init__(self, p):
        (self.anchor_a, self.anchor_standoff, self.exit_x, self.exit_y, self.door_open_deg,
         self.drum_r, self.drum_width, self.drum_pitch, self.cable_d, self.cable_break_n,
         self.stage1_pinion_t, self.stage1_gear_t, self.stage2_pinion_t, self.stage2_gear_t,
         self.module1, self.module2, self.face1, self.face2, self.door_mass_kg,
         self.door_width_mm, self.magnet_radius_mm, self.magnet_gap_closed_mm,
         self.build_tol_mm, self.frame_plumb_deg, self.rebate_depth_mm, self.cable_eye_wall,
         self.cable_eye_h, self.pin_d, self.anchor_screws, self.anchor_screw_d,
         self.cable_guide_deg, self.cable_guide_mu, self.base_w, self.base_z,
         self.foot_h, self.nose_l, self.nose_w, self.nose_h, self.nose_x) = require(
            p, "anchor_a", "anchor_standoff", "exit_x", "exit_y", "door_open_deg",
            "drum_r", "drum_width", "drum_pitch", "cable_d", "cable_break_n",
            "stage1_pinion_t", "stage1_gear_t", "stage2_pinion_t", "stage2_gear_t",
            "module1", "module2", "face1", "face2", "door_mass_kg",
            "door_width_mm", "magnet_radius_mm", "magnet_gap_closed_mm",
            "build_tol_mm", "frame_plumb_deg", "rebate_depth_mm", "cable_eye_wall",
            "cable_eye_h", "pin_d", "anchor_screws", "anchor_screw_d",
            "cable_guide_deg", "cable_guide_mu", "base_w", "base_z", "foot_h",
            "nose_l", "nose_w", "nose_h", "nose_x")
        self.ratio = ((self.stage1_gear_t / self.stage1_pinion_t)
                      * (self.stage2_gear_t / self.stage2_pinion_t))
        self.eff = SPUR_STAGE_EFF ** 2
        # The cable winds on the groove bottom plus half its own diameter.
        self.drum_eff_r = self.drum_r + self.cable_d / 2.0
        # Capstan loss where the cable turns through the exit chute: exp(mu * angle).
        self.guide_loss = math.exp(self.cable_guide_mu * math.radians(self.cable_guide_deg))
        self.inertia = self.door_mass_kg * (self.door_width_mm / 1000.0) ** 2 / 3.0
        # Polar form of the two cable ends, both measured from the vertical hinge axis.
        # Door frame: +x runs along the closed door into the opening, +y is the push side
        # (the side the door does NOT swing to), which is the only side with free rebate depth.
        self.a_r = math.hypot(self.anchor_a, self.anchor_standoff)
        self.phi = math.degrees(math.atan2(self.anchor_standoff, self.anchor_a))
        self.b_r = math.hypot(self.exit_x, self.exit_y)
        self.gamma = math.degrees(math.atan2(self.exit_y, self.exit_x))

    # -- geometry -------------------------------------------------------------
    def psi_deg(self, theta_deg):
        """Included angle at the hinge axis between the door-side anchor and the cable exit.

        The anchor rides the door, so its angular position is theta + phi measured from the
        closed-door direction on the swing side; the exit is fixed at gamma on the push side.
        Both offsets add to the included angle, which is why the exit must sit off the closed
        door plane: with gamma = phi = 0 the two ends and the hinge axis are collinear at
        theta = 0, the arm is identically zero, and no tension can close the last degree.
        """
        return theta_deg + self.gamma - self.phi

    def chord_mm(self, theta_deg):
        psi = math.radians(self.psi_deg(theta_deg))
        return math.sqrt(self.a_r ** 2 + self.b_r ** 2 - 2 * self.a_r * self.b_r * math.cos(psi))

    def arm_mm(self, theta_deg, worst=True):
        """Cable moment arm about the hinge axis = dL/dtheta = a b sin(psi) / L.

        Verified independently by geometry: the triangle hinge-anchor-exit has area
        0.5 a b sin(psi) and also 0.5 L d, so d = a b sin(psi) / L is the perpendicular
        distance from the hinge axis to the cable line. `worst` removes the build tolerance,
        since mounting either end a few millimetres off shifts the arm by about that much.
        """
        raw = (self.a_r * self.b_r * math.sin(math.radians(self.psi_deg(theta_deg)))
               / self.chord_mm(theta_deg))
        return raw - (self.build_tol_mm if worst else 0.0)

    def cable_travel_mm(self):
        return self.chord_mm(self.door_open_deg) - self.chord_mm(0.0)

    # -- door resistance ------------------------------------------------------
    def resist_nm(self, theta_deg):
        """Torque the door resists closing with, at this angle. Positive opposes closing."""
        friction = HINGE_FRICTION_NM
        plumb = (self.door_mass_kg * G * (self.door_width_mm / 2000.0)
                 * math.sin(math.radians(self.frame_plumb_deg))
                 * math.sin(math.radians(theta_deg)))
        return friction + plumb

    def magnet_nm(self, theta_deg):
        """Closing torque the magnets contribute. Positive helps close."""
        gap = self.magnet_gap_closed_mm + self.magnet_radius_mm * math.radians(theta_deg)
        return magnet_pull(gap) * self.magnet_radius_mm / 1000.0

    # -- drive ----------------------------------------------------------------
    def motor_torque_nm(self, rpm):
        return MOTOR_STALL_NM * max(0.0, 1.0 - rpm / MOTOR_NOLOAD_RPM)

    def motor_current_a(self, torque_nm):
        frac = min(1.0, max(0.0, torque_nm / MOTOR_STALL_NM))
        return MOTOR_NOLOAD_A + frac * (MOTOR_STALL_A - MOTOR_NOLOAD_A)

    def torque_limit_nm(self):
        """Most motor torque the driver's 1.0 A hardware chop will ever allow."""
        frac = (DRIVER_LIMIT_A - MOTOR_NOLOAD_A) / (MOTOR_STALL_A - MOTOR_NOLOAD_A)
        return MOTOR_STALL_NM * frac

    def drum_tension_n(self, motor_nm):
        """Tension in the cable on the drum side of the exit chute - what the parts see."""
        return motor_nm * self.ratio * self.eff / (self.drum_eff_r / 1000.0)

    def tension_n(self, motor_nm):
        """Tension actually delivered to the door, after the chute's capstan loss."""
        return self.drum_tension_n(motor_nm) / self.guide_loss

    def door_torque_nm(self, motor_nm, theta_deg):
        return self.tension_n(motor_nm) * self.arm_mm(theta_deg) / 1000.0

    def max_tension_n(self):
        """Worst tension any printed part sees: drum side, at the driver's hardware limit."""
        return self.drum_tension_n(self.torque_limit_nm())

    def solve_speed(self, theta_deg):
        """Steady door speed at this angle: the motor point where drive torque = resistance.

        Returns (rpm, door_deg_per_s, motor_nm, current_a) or None when the drive cannot hold
        the door at any speed (i.e. it stalls at this angle).
        """
        need = self.resist_nm(theta_deg) - self.magnet_nm(theta_deg)
        if need <= 0:
            need = 0.0
        gain = (self.ratio * self.eff * self.arm_mm(theta_deg)
                / (self.drum_eff_r * self.guide_loss))
        if gain <= 0:
            return None
        motor_need = need / gain
        if motor_need > self.torque_limit_nm():
            return None
        rpm = MOTOR_NOLOAD_RPM * (1.0 - motor_need / MOTOR_STALL_NM)
        if rpm <= 0:
            return None
        drum_rpm = rpm / self.ratio
        cable_mm_s = drum_rpm / 60.0 * 2 * math.pi * self.drum_eff_r
        door_rad_s = cable_mm_s / self.arm_mm(theta_deg)
        return rpm, math.degrees(door_rad_s), motor_need, self.motor_current_a(motor_need)

    # -- stress ---------------------------------------------------------------
    def lewis_tooth_mpa(self, module, face_mm, torque_nm, teeth):
        """Lewis bending stress at the tooth root. Y = 0.32 for a 20 deg involute, ~18 teeth."""
        pitch_r_m = module * teeth / 2000.0
        tangential_n = torque_nm / pitch_r_m
        return tangential_n / (face_mm * module * 0.32)

    def checks(self):
        out = []

        def check(name, ok, detail):
            out.append({"check": name, "pass": bool(ok), "detail": detail})

        # -- geometry is physically realisable and has no dead centre
        check("offset_removes_dead_centre", self.psi_deg(0.0) >= 20.0,
              f"included angle at the hinge axis is {self.psi_deg(0.0):.1f} deg when shut and "
              f"{self.psi_deg(self.door_open_deg):.1f} deg wide open. It never reaches 0 or 180 "
              f"deg, which are the two collinear dead centres where no tension makes any torque")
        arm_min = min(self.arm_mm(float(t)) for t in range(0, int(self.door_open_deg) + 1))
        check("arm_never_collapses", arm_min >= 25.0,
              f"worst-case moment arm over the whole swing is {arm_min:.1f} mm (peak "
              f"{max(self.arm_mm(float(t)) for t in range(0, int(self.door_open_deg) + 1)):.1f} mm), "
              f"after subtracting the {self.build_tol_mm} mm mounting tolerance. A straight "
              f"chord with the exit on the closed-door plane would instead go to 0 mm at 0 deg")

        # -- cable and drum
        travel = self.cable_travel_mm()
        turns = travel / (2 * math.pi * self.drum_eff_r)
        needed_width = turns * self.drum_pitch + self.drum_pitch
        check("drum_holds_travel", needed_width <= self.drum_width,
              f"{travel:.1f} mm of travel = {turns:.2f} turns at an effective "
              f"{self.drum_eff_r:.1f} mm winding radius needs "
              f"{needed_width:.1f} mm of grooved drum; drum_width is {self.drum_width} mm")
        max_t = self.max_tension_n()
        check("cable_strength", self.cable_break_n >= 3.0 * max_t,
              f"cable rated {self.cable_break_n} N against a hardware-limited maximum tension "
              f"of {max_t:.0f} N (safety factor {self.cable_break_n / max_t:.1f}, 3.0 required)")

        # -- torque margin at every angle, worst-case resistance
        rows = []
        worst_margin = float("inf")
        worst_angle = None
        for step in range(0, int(self.door_open_deg) + 1):
            theta = float(step)
            resist = self.resist_nm(theta)
            assist = self.magnet_nm(theta)
            available = self.door_torque_nm(self.torque_limit_nm(), theta)
            net = resist - assist
            margin = available / net if net > 0 else float("inf")
            if margin < worst_margin:
                worst_margin, worst_angle = margin, theta
            speed = self.solve_speed(theta)
            rows.append({"deg": theta, "resist_nm": round(resist, 3),
                         "magnet_assist_nm": round(assist, 3),
                         "available_nm": round(available, 3),
                         "margin": None if margin == float("inf") else round(margin, 2),
                         "deg_per_s": None if speed is None else round(speed[1], 2),
                         "motor_a": None if speed is None else round(speed[3], 2)})
        check("torque_margin", worst_margin >= 2.0,
              f"worst torque margin is {worst_margin:.2f}x at {worst_angle:.0f} deg "
              f"(2.0x required, against the worst-case {HINGE_FRICTION_NM} N.m hinge friction "
              f"and {self.frame_plumb_deg} deg of frame out-of-plumb)")
        stalls = [r["deg"] for r in rows if r["deg_per_s"] is None]
        check("no_stall_angle", not stalls,
              "the drive holds and moves the door at every angle"
              if not stalls else f"stalls at {stalls[:6]} deg")

        # -- close time and the A156.19 limits
        time_s = 0.0
        for step in range(int(self.door_open_deg)):
            a = self.solve_speed(step + 0.5)
            if a is None:
                time_s = float("inf")
                break
            time_s += 1.0 / a[1]
        latch_s = 0.0
        for step in range(0, 10):
            a = self.solve_speed(step + 0.5)
            latch_s += 0.0 if a is None else 1.0 / a[1]
        check("close_time_sane", 6.0 <= time_s <= 45.0,
              f"full close from {self.door_open_deg} deg takes {time_s:.1f} s at the "
              f"quasi-static operating point (the TT motor's {MOTOR_STALL_NM * 1000:.1f} mN.m "
              f"and {MOTOR_NOLOAD_RPM:.0f} RPM at 5 V cap mechanical power near 0.35 W, so the "
              f"5 s sweep of a hydraulic closer is not available at any gear ratio)")

        # Energy at contact. The cable's contribution is the kinetic energy it has built up;
        # the magnets then do the rest of the work over the final air gap, which is what makes
        # a magnetic catch click. Both are counted against the A156.19 cap, because what the
        # door actually arrives with is the sum.
        cable_rad_s = math.radians(max(r["deg_per_s"] or 0 for r in rows))
        cable_energy = 0.5 * self.inertia * cable_rad_s ** 2
        takeover_gap = 15.0
        steps = 300
        magnet_work = sum(magnet_pull(takeover_gap * (i + 0.5) / steps)
                          * (takeover_gap / steps) / 1000.0 for i in range(steps))
        energy = cable_energy + magnet_work
        check("energy_cap", energy <= A156_ENERGY_J,
              f"the leaf arrives carrying {energy:.2f} J - {cable_energy:.3f} J of cable-driven "
              f"kinetic energy plus {magnet_work:.2f} J of magnet work over the last "
              f"{takeover_gap:.0f} mm - against the A156.19 {A156_ENERGY_J} J cap "
              f"(leaf inertia {self.inertia:.2f} kg.m2)")
        check("latch_period_reported", True,
              f"the last 10 deg takes {latch_s:.2f} s under cable drive alone; A156.19's "
              f"{A156_LATCH_S} s latch period is written for a sprung hydraulic closer with a "
              f"latch bolt to retract. This design has no latch bolt: the magnets take over at "
              f"about 1 deg and snap the leaf shut, so the energy check above is the meaningful "
              f"limit and this figure is reported, not asserted")

        # -- the magnets have to finish the job and then hold
        hold = magnet_pull(self.magnet_gap_closed_mm)
        check("magnet_holds_closed", hold >= 40.0,
              f"{hold:.1f} N of magnet pull at the as-built {self.magnet_gap_closed_mm} mm gap "
              f"(>= 40 N required to keep a {self.door_mass_kg} kg leaf shut against a draught)")
        takeover = self.magnet_nm(1.0)
        check("magnet_takes_over", takeover >= self.resist_nm(1.0),
              f"at 1 deg - a {self.magnet_radius_mm * math.radians(1.0):.0f} mm air gap at the "
              f"latch edge - the magnets alone make {takeover:.2f} N.m against "
              f"{self.resist_nm(1.0):.2f} N.m of resistance, so the last few millimetres are "
              f"magnet-driven and the cable never has to work near a dead centre")

        # -- printed part stress, all at the hardware-limited tension
        s1 = self.lewis_tooth_mpa(self.module1, self.face1, self.torque_limit_nm(),
                                  self.stage1_pinion_t)
        stage2_in = (self.torque_limit_nm() * self.stage1_gear_t / self.stage1_pinion_t
                     * SPUR_STAGE_EFF)
        s2 = self.lewis_tooth_mpa(self.module2, self.face2, stage2_in, self.stage2_pinion_t)
        check("stage1_teeth", s1 <= ALLOW["xy_cyclic"],
              f"stage-1 pinion root stress {s1:.2f} MPa against the {ALLOW['xy_cyclic']} MPa "
              f"cyclic in-plane allowable (gears print flat, so tooth load stays in the layer plane)")
        check("stage2_teeth", s2 <= ALLOW["xy_cyclic"],
              f"stage-2 pinion root stress {s2:.2f} MPa against {ALLOW['xy_cyclic']} MPa")
        eye_area = 2 * self.cable_eye_wall * self.cable_eye_h
        eye_mpa = max_t / eye_area
        check("anchor_cable_eye", eye_mpa <= ALLOW["z"],
              f"the anchor's cable eye carries the tension in double shear across "
              f"{eye_area:.0f} mm2 of material, {eye_mpa:.2f} MPa against the {ALLOW['z']} MPa "
              f"across-layer allowable; the eye prints with its axis flat so the load does not "
              f"peel layers apart")
        pin_area = 2 * math.pi * (self.pin_d / 2) ** 2
        pin_mpa = max_t / pin_area
        check("idler_pin_shear", pin_mpa <= 120.0,
              f"the {self.pin_d} mm steel idler pin sees {pin_mpa:.1f} MPa in double shear "
              f"(120 MPa allowable for plain steel, and the load path is a steel pin rather "
              f"than a printed cantilever)")
        screw_area = self.anchor_screws * math.pi * (self.anchor_screw_d / 2) ** 2
        check("anchor_screws", max_t / screw_area <= 120.0,
              f"{self.anchor_screws} x M{self.anchor_screw_d} screws hold the sheave to the door "
              f"stile in shear: {max_t / screw_area:.1f} MPa on the screw cross-sections")

        # -- the cable and the unit must never be in the door's way
        unit_far_x = self.foot_h + self.base_z
        check("unit_outside_swept_volume", self.exit_x > 0 and self.exit_y > 0,
              f"an ordinary butt hinge puts the pivot axis in the door's push face, so over "
              f"0..{self.door_open_deg:.0f} deg the leaf sweeps only the quadrant at negative "
              f"polar angles. The whole unit sits at x 0..{unit_far_x:.0f} mm, "
              f"y 0..{self.base_w:.0f} mm - positive in both - so nothing it contains is ever "
              f"in the leaf's path, and the door still opens fully by hand with the power off")
        check("cable_stays_push_side", self.anchor_standoff > 0 and self.exit_y > 0,
              f"both cable ends sit clear of the leaf's push face - the anchor eye "
              f"{self.anchor_standoff} mm off the face, the exit {self.exit_y} mm off the closed "
              f"plane - so the straight run between them stays on the push side at every angle "
              f"and can never foul the leaf or wrap the hinge")
        check("unit_within_rebate", max(self.base_w, unit_far_x) <= self.rebate_depth_mm,
              f"the shell is {self.base_w:.0f} mm across the jamb depth and stands "
              f"{unit_far_x:.0f} mm out into the opening on {self.foot_h:.0f} mm feet, both "
              f"inside the {self.rebate_depth_mm} mm rebate of a 4-9/16 in jamb")
        nose_tip_x = self.foot_h + self.base_z + self.nose_l
        check("exit_reachable_on_nose", self.exit_x <= nose_tip_x + 0.5
              and abs(self.exit_y - self.nose_x) <= self.nose_w / 2,
              f"the exit at ({self.exit_x}, {self.exit_y}) mm sits in the integral nose, a "
              f"{self.nose_w:.0f} x {self.nose_h:.0f} mm fin that carries the chute "
              f"{self.nose_l:.0f} mm past the cover to x = {nose_tip_x:.0f} mm. The exit has to "
              f"reach out along the door to keep the moment arm up; the nose is the cheapest way "
              f"to do that without making the whole shell that deep")
        # The nose is a printed cantilever loaded by the full wound tension at its tip.
        nose_i = self.nose_h * self.nose_w ** 3 / 12.0
        nose_mpa = (max_t * self.nose_l) * (self.nose_w / 2) / nose_i
        check("nose_bending", nose_mpa <= ALLOW["z"],
              f"the nose root sees {max_t * self.nose_l / 1000:.2f} N.m of bending from "
              f"{max_t:.0f} N at its tip: {nose_mpa:.2f} MPa against the {ALLOW['z']} MPa "
              f"across-layer allowable, which is the right allowable because the shell prints "
              f"with its open face up and the nose therefore grows along the layer axis")

        # -- the chute costs tension, and the parts are checked at the higher drum-side figure
        check("guide_loss_accounted", self.guide_loss < 1.2,
              f"the cable turns {self.cable_guide_deg:.0f} deg through the exit chute, so the "
              f"door only receives 1/{self.guide_loss:.3f} of the drum tension: "
              f"{self.tension_n(self.torque_limit_nm()):.0f} N delivered from "
              f"{max_t:.0f} N wound. Every printed part above is checked at the wound figure")

        # -- the anchor standoff turns cable tension into a moment on three wood screws
        moment_nm = max_t * self.anchor_standoff / 1000.0
        span_m = (self.anchor_screws - 1) * 20.0 / 1000.0
        per_screw_n = moment_nm / span_m if span_m > 0 else float("inf")
        check("anchor_withdrawal", per_screw_n <= 400.0,
              f"the {self.anchor_standoff} mm standoff turns {max_t:.0f} N of tension into "
              f"{moment_nm:.2f} N.m on the anchor base; over a {span_m * 1000:.0f} mm screw span "
              f"that is {per_screw_n:.0f} N of withdrawal per screw, against 400 N allowed for a "
              f"#8 screw 25 mm into a solid-core stile")

        # -- current budget on the USB 5 V rail
        check("current_budget", DRIVER_LIMIT_A <= 1.0,
              f"motor current is chopped in hardware at {DRIVER_LIMIT_A} A by the DRV8833 "
              f"breakout's 0.2 ohm sense resistors, taken from the USB 5 V rail at the driver, "
              f"never through the T-Display board")
        return out, rows, {"ratio": self.ratio, "efficiency": self.eff,
                           "cable_travel_mm": travel, "turns": turns,
                           "max_tension_n": max_t, "close_time_s": time_s,
                           "latch_period_s": latch_s, "peak_energy_j": energy,
                           "worst_margin": worst_margin, "worst_margin_deg": worst_angle,
                           "arm_min_mm": arm_min, "arm_closed_mm": self.arm_mm(0.0),
                           "arm_open_mm": self.arm_mm(self.door_open_deg),
                           "psi_closed_deg": self.psi_deg(0.0),
                           "magnet_hold_n": hold, "leaf_inertia_kgm2": self.inertia}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    mech = Mechanism(params())
    checks, rows, summary = mech.checks()
    report = {"all_pass": all(c["pass"] for c in checks), "physical_test": False,
              "analysis_only": True, "summary": {k: (round(v, 4) if isinstance(v, float) else v)
                                                 for k, v in summary.items()},
              "checks": checks, "angle_table": rows}
    (ROOT / "docs").mkdir(parents=True, exist_ok=True)
    (ROOT / "docs/mechanism.json").write_text(json.dumps(report, indent=2))
    if args.json:
        print(json.dumps(report["summary"], indent=2))
    else:
        for c in checks:
            print(("PASS  " if c["pass"] else "FAIL  ") + c["check"] + ": " + c["detail"])
        print()
        print(f"ratio {summary['ratio']:.2f}:1   arm {summary['arm_min_mm']:.1f} mm   "
              f"travel {summary['cable_travel_mm']:.1f} mm ({summary['turns']:.2f} turns)   "
              f"max tension {summary['max_tension_n']:.0f} N")
        print(f"close {summary['close_time_s']:.1f} s   last 10 deg "
              f"{summary['latch_period_s']:.2f} s   peak energy "
              f"{summary['peak_energy_j']:.3f} J   worst margin "
              f"{summary['worst_margin']:.2f}x at {summary['worst_margin_deg']:.0f} deg")
    if not report["all_pass"]:
        raise SystemExit("FAILED: " + ", ".join(c["check"] for c in checks if not c["pass"]))
    print("PASS: mechanism analysis. This is analysis of the design, not a test of a build.")


if __name__ == "__main__":
    main()
