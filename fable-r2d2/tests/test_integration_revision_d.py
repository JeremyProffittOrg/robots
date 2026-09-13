"""Revision D integration checks for the fable-r2d2 package scripts.

Covers the revision D labels, the counts read from manifests instead of hard-coded, verify.py
refusing revision D when docs/stance-check.json is missing, failed or stale, and the deliver.py
dry run. Run from C:/dev/robots/fable-r2d2:

    python -m unittest discover -s tests -p "test_integration_revision_d.py" -v
"""
import csv
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assembly_layout  # noqa: E402
import build_bom  # noqa: E402
import deliver  # noqa: E402
import render_mockup  # noqa: E402
import render_video  # noqa: E402
import verify  # noqa: E402

INTEGRATION_FILES = ["scripts/verify.py", "scripts/build_bom.py", "scripts/build_manual.py", "scripts/draw_robot.py",
                     "scripts/render_video.py", "scripts/video_storyboard.json", "scripts/video_scene.js",
                     "scripts/render_mockup.py", "scripts/assembly_layout.py", "scripts/deliver.py",
                     "scripts/build_video_audio.ps1", "README.md", "docs/assembly.md"]
REVISION_C_WORDING = [r"\b[Nn]ine STL\b", r"\b[Tt]welve printed\b", r"\b47 \+ 44\b", r"\b136 wires\b",
                      r"\bindex dowels?\b", r"\bindex pins?\b", r"shoulder_index_", r"two-leg display stance",
                      r"\b113 tests\b", r"center_leg_flange", r"\b170-second\b"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(root, relative, content):
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, (dict, list)):
        content = json.dumps(content)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
    return path


class RevisionLabels(unittest.TestCase):
    def test_revision_and_stance_parameter_constants(self):
        self.assertEqual(assembly_layout.REVISION, "D")
        self.assertEqual(assembly_layout.STANCE_PARAMETER, "stance_s")

    def test_every_output_is_labelled_revision_d(self):
        story = json.loads((ROOT / "scripts/video_storyboard.json").read_text(encoding="utf-8"))
        self.assertEqual(story["revision"], "D")
        sources = {name: (ROOT / name).read_text(encoding="utf-8") for name in INTEGRATION_FILES}
        self.assertIn("TITLE = f'fable-r2d2 revision {REVISION}", sources["scripts/build_manual.py"])
        self.assertIn("'revision': REVISION", sources["scripts/build_manual.py"])
        self.assertIn('f"fable-r2d2 revision {REVISION}  /  printable R2-D2', sources["scripts/draw_robot.py"])
        self.assertIn('"revision": REVISION', sources["scripts/draw_robot.py"])
        self.assertIn('f"fable-r2d2 revision {REVISION}  /  final build mock-up', sources["scripts/render_mockup.py"])
        self.assertIn('"revision": REVISION', sources["scripts/render_video.py"])
        self.assertIn("REVISION ${story.revision}", sources["scripts/video_scene.js"])
        self.assertEqual(deliver.KEY_PREFIX, "fable-r2d2/revision-d/")
        self.assertIn("revision D", sources["README.md"].splitlines()[0])
        self.assertIn("Revision D", sources["docs/assembly.md"])

    def test_no_revision_c_wording_or_hard_coded_counts_remain(self):
        for name in INTEGRATION_FILES:
            text = (ROOT / name).read_text(encoding="utf-8")
            for pattern in REVISION_C_WORDING:
                self.assertIsNone(re.search(pattern, text), f"{name} still contains {pattern}")


class ManifestDerivedCounts(unittest.TestCase):
    def test_package_counts_come_from_parts_json(self):
        parts = json.loads((ROOT / "scripts/parts.json").read_text(encoding="utf-8"))["parts"]
        counts = assembly_layout.package_counts(ROOT)
        self.assertEqual(counts["designs"], len(parts))
        self.assertEqual(counts["pieces"], sum(int(row["quantity"]) for row in parts.values()))
        self.assertEqual(counts["mirrored"], [name for name, row in parts.items() if row.get("mirror")])

    def test_layout_places_exactly_the_parts_json_pieces(self):
        lay = assembly_layout.Layout(ROOT)
        self.assertEqual(len(lay.instances()), assembly_layout.package_counts(ROOT)["pieces"])

    def test_storyboard_counts_are_filled_from_parts_json(self):
        counts = assembly_layout.package_counts(ROOT)
        story = render_video.load_story()
        title = story["chapters"][0]["title"]
        self.assertEqual(title, f"{assembly_layout.number_word(counts['designs']).capitalize()} STL files. "
                                f"{assembly_layout.number_word(counts['pieces']).capitalize()} printed pieces.")
        for chapter in story["chapters"]:
            self.assertNotRegex(chapter["narration"], r"\{[A-Z_]+\}")
            self.assertEqual(set(re.findall(r"\{([A-Z_]+)\}", chapter["title"] + chapter["instruction"])) - {"HEIGHT"}, set())

    def test_unknown_storyboard_token_is_refused(self):
        broken = {"chapters": [{"name": "x", "title": "{NOT_A_TOKEN}", "instruction": "", "narration": ""}]}
        with self.assertRaises(ValueError):
            render_video.resolve_story(broken, {"DESIGNS": "10"})

    def test_storyboard_structure_and_both_stance_changes(self):
        story = json.loads((ROOT / "scripts/video_storyboard.json").read_text(encoding="utf-8"))
        self.assertTrue(render_video.validate_story(story))
        phases = render_video.phase_windows(story)
        self.assertIn(("stance-retract", "TILT"), {(c, p) for c, p, _, _ in phases})
        self.assertIn(("stance-deploy", "TILT"), {(c, p) for c, p, _, _ in phases})
        gap = json.loads(json.dumps(story))
        gap["chapters"][3]["start"] += 1
        with self.assertRaises(ValueError):
            render_video.validate_story(gap)

    def test_revision_d_purchases_match_the_electrical_record(self):
        record = re.search(r"That is (\d+) pieces", (ROOT / "docs/electrical.md").read_text(encoding="utf-8"))
        self.assertIsNotNone(record, "docs/electrical.md section 11 no longer states the added piece count")
        delta = build_bom.purchased_delta("electronics.csv")
        self.assertEqual(delta["pieces"], int(record.group(1)))
        self.assertGreater(delta["usd"], 0)

    def test_printed_delta_reads_both_part_lists(self):
        printed = build_bom.printed_delta()
        self.assertEqual(printed["designs"]["after"], assembly_layout.package_counts(ROOT)["designs"])
        self.assertEqual(printed["designs"]["before"], 9)

    def test_wire_count_comes_from_wiring_csv(self):
        with (ROOT / "electronics/wiring.csv").open(newline="", encoding="utf-8") as handle:
            rows = sum(1 for _ in csv.DictReader(handle))
        verify.RESULTS.clear()
        verify.check_wiring()
        self.assertTrue(verify.RESULTS[-1]["detail"].startswith(f"{rows} wires"))

    def test_test_count_parser(self):
        self.assertEqual(verify.parse_test_count("....\n----\nRan 120 tests in 1.225s\n\nOK"), 120)
        self.assertEqual(verify.parse_test_count("Ran 1 test in 0.001s\n\nOK"), 1)
        self.assertIsNone(verify.parse_test_count("ImportError: no module\n"))

    def test_firmware_test_counts_come_from_the_real_runs(self):
        verify.RESULTS.clear()
        verify.FIRMWARE_TESTS.clear()
        verify.check_firmware()
        result = verify.RESULTS[-1]
        self.assertEqual(set(verify.FIRMWARE_TESTS), {"firmware/kb2040", "firmware/pi"})
        for suite, count in verify.FIRMWARE_TESTS.items():
            self.assertIsInstance(count, int)
            self.assertGreater(count, 0)
            self.assertIn(f"{suite}: Ran {count} tests", result["detail"])

    def test_stance_parameter_is_declared_in_the_cad(self):
        self.assertIsNotNone(assembly_layout.declared_stance_parameter(ROOT))

    def test_stance_kinematics_endpoints(self):
        lay = assembly_layout.Layout(ROOT)
        ends = lay.endpoints()
        self.assertEqual(lay.stance.tilt(ends["two_foot"]), 0.0)
        self.assertAlmostEqual(lay.stance.tilt(ends["three_leg"]), lay.p["body_tilt"], delta=0.05)
        self.assertAlmostEqual(lay.centre_foot_lift(ends["two_foot"]), lay.p["st_stow_lift"], delta=0.01)
        with self.assertRaises(ValueError):
            lay.at_stroke(ends["three_leg"] + 5)

    def test_mockup_shows_both_stances_and_a_transition(self):
        lay = assembly_layout.Layout(ROOT)
        ends = lay.endpoints()
        strokes = [tile["stroke_mm"] for tile in render_mockup.view_plan(lay)]
        self.assertTrue(any(abs(s - ends["two_foot"]) < 1e-3 for s in strokes))
        self.assertTrue(any(abs(s - ends["three_leg"]) < 1e-3 for s in strokes))
        self.assertTrue(any(ends["contact"] < s < ends["three_leg"] for s in strokes))


class VerifyRevisionGate(unittest.TestCase):
    def fixture(self, root):
        write(root, "scripts/parts.json", {"parts": {"part_a": {"quantity": 1}}})
        write(root, "cad/params.scad", "st_s_two = 5;\n")
        write(root, "cad/stance.scad", "module st() {}\n")
        write(root, "stl/part_a.stl", b"solid a\nendsolid a\n")
        write(root, "scripts/check_stance.py", "print('check')\n")
        write(root, "scripts/stability.py", "print('stability')\n")
        design = ["cad/params.scad", "cad/stance.scad", "scripts/stability.py"]
        required = design + ["stl/part_a.stl", "scripts/check_stance.py"]
        return design, {rel: sha(Path(root) / rel) for rel in required}

    def test_missing_stance_check_is_refused(self):
        with tempfile.TemporaryDirectory() as root:
            self.fixture(root)
            problems = verify.stance_check_problems(root)
            self.assertTrue(problems and "missing" in problems[0])

    def test_stance_check_without_source_hashes_is_refused(self):
        with tempfile.TemporaryDirectory() as root:
            design, _ = self.fixture(root)
            write(root, verify.STANCE_CHECK, {"passed": True, "design_source": design})
            self.assertTrue(any("no source hashes" in p for p in verify.stance_check_problems(root)))

    def test_failed_stance_check_is_refused(self):
        with tempfile.TemporaryDirectory() as root:
            design, hashes = self.fixture(root)
            write(root, verify.STANCE_CHECK, {"passed": False, "failures": [{}], "design_source": design,
                                              "source_sha256": hashes})
            self.assertTrue(any("passed=False" in p for p in verify.stance_check_problems(root)))

    def test_current_stance_check_is_accepted_and_goes_stale_when_the_cad_changes(self):
        with tempfile.TemporaryDirectory() as root:
            design, hashes = self.fixture(root)
            write(root, verify.STANCE_CHECK, {"passed": True, "design_source": design, "source_sha256": hashes})
            self.assertEqual(verify.stance_check_problems(root), [])
            write(root, "cad/params.scad", "st_s_two = 6;\n")
            problems = verify.stance_check_problems(root)
            self.assertTrue(any("changed since" in p and "cad/params.scad" in p for p in problems))

    def test_stance_check_must_cover_every_cad_file(self):
        with tempfile.TemporaryDirectory() as root:
            design, hashes = self.fixture(root)
            write(root, "cad/body.scad", "module body() {}\n")
            write(root, verify.STANCE_CHECK, {"passed": True, "design_source": design, "source_sha256": hashes})
            self.assertTrue(any("do not cover" in p and "cad/body.scad" in p for p in verify.stance_check_problems(root)))

    def test_revision_d_only_for_a_complete_passing_run(self):
        names = list(verify.CHECKS)
        passing = [{"check": n, "pass": True, "detail": ""} for n in names]
        self.assertEqual(verify.build_report(passing, names, {})["revision"], "D")
        failing = [dict(r) for r in passing]
        failing[names.index("stance")]["pass"] = False
        report = verify.build_report(failing, names, {})
        self.assertIsNone(report["revision"])
        self.assertFalse(report["all_pass"])
        partial = verify.build_report(passing[:3], names[:3], {})
        self.assertIsNone(partial["revision"])
        self.assertEqual(partial["partial_run"], names[:3])

    def test_stance_and_mockup_are_package_checks(self):
        self.assertIn("stance", verify.CHECKS)
        self.assertIn("mockup", verify.CHECKS)


class DeliverDryRun(unittest.TestCase):
    def test_dry_run_builds_the_mime_and_sends_nothing(self):
        watched = [ROOT / "output/delivery-receipt.json", ROOT / "output/delivery-preview.html"]
        before = {path: sha(path) for path in watched if path.exists()}
        result = subprocess.run([sys.executable, "scripts/deliver.py", "--dry-run"], cwd=ROOT,
                                capture_output=True, text=True, timeout=600)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"MIME size \d+ bytes")
        self.assertIn("DRY RUN: nothing uploaded, nothing sent", result.stdout)
        self.assertIn("s3://robots-deliverables-759775734231/fable-r2d2/revision-d/", result.stdout)
        self.assertEqual(before, {path: sha(path) for path in watched if path.exists()})

    def test_a_real_send_requires_a_verified_revision_d_package(self):
        with tempfile.TemporaryDirectory() as root:
            pdf = write(root, "output/pdf/r2d2-assembly-manual.pdf", b"%PDF-1.7 test")
            video = write(root, "output/video/r2d2-assembly-and-operation.mp4", b"video bytes")
            write(root, "docs/verification.json", {"all_pass": True, "revision": None, "checks": []})
            write(root, "docs/pdf-check.json", {"revision": "D", "all_pass": True, "sha256": sha(pdf)})
            write(root, "output/video/video-manifest.json", {"revision": "C", "video_sha256": sha(video)})
            blockers = deliver.send_blockers(root)
            self.assertTrue(any("verification.json" in b for b in blockers))
            self.assertTrue(any("video-manifest.json" in b for b in blockers))
            write(root, "docs/verification.json", {"all_pass": True, "revision": "D", "checks": []})
            write(root, "output/video/video-manifest.json", {"revision": "D", "video_sha256": sha(video)})
            self.assertEqual(deliver.send_blockers(root), [])

    def test_revision_c_receipt_does_not_block_revision_d(self):
        receipt = json.loads((ROOT / "output/delivery-receipt.json").read_text(encoding="utf-8"))
        if receipt.get("revision") == "D":
            self.skipTest("the revision D email has been sent")
        self.assertEqual(deliver.receipt_revision(receipt), "C")


if __name__ == "__main__":
    unittest.main()
