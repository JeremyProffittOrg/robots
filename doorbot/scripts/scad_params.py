"""Read the numeric parameters out of doorbot/cad/params.scad.

cad/params.scad is the single source of truth for every dimension. Python reads it so a CAD
change cannot silently diverge from the mechanism checks, the BOM or the drawings. Parser
adapted from fable-r2d2/scripts/assembly_layout.py so both projects share one dialect.
"""
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_SCOPE = {
    "sin": lambda a: math.sin(math.radians(a)), "cos": lambda a: math.cos(math.radians(a)),
    "tan": lambda a: math.tan(math.radians(a)), "asin": lambda v: math.degrees(math.asin(v)),
    "acos": lambda v: math.degrees(math.acos(v)), "atan": lambda v: math.degrees(math.atan(v)),
    "atan2": lambda y, x: math.degrees(math.atan2(y, x)), "sqrt": math.sqrt, "abs": abs,
    "min": min, "max": max, "floor": math.floor, "ceil": math.ceil, "round": round, "pow": pow,
    "true": True, "false": False, "PI": math.pi,
}


def read_scad(path, base=None):
    """Evaluate the `name = expr;` statements of an OpenSCAD file into a dict."""
    text = Path(path).read_text(encoding="utf-8")
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    env = dict(base or {})
    for chunk in text.split(";"):
        match = re.match(r"\s*([A-Za-z_$][A-Za-z0-9_]*)\s*=\s*(.+)$", chunk.strip(), flags=re.S)
        if not match:
            continue
        name, expr = match.group(1), match.group(2).strip()
        if name.startswith("$"):
            continue
        try:
            env[name] = eval(expr, {"__builtins__": {}}, {**_SCOPE, **env})
        except Exception:
            continue
    return env


def params(root=ROOT):
    """Every parameter in cad/params.scad, as a plain dict of numbers."""
    return read_scad(Path(root) / "cad/params.scad")


def require(env, *names):
    """Fetch parameters, failing loudly rather than defaulting a missing dimension to zero."""
    missing = [n for n in names if n not in env]
    if missing:
        raise SystemExit("cad/params.scad is missing: " + ", ".join(missing))
    return [env[n] for n in names]
