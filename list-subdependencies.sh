#!/usr/bin/env bash
#
# list-subdependencies.sh
# ---------------------------------------------------------------------------
# Emit the full, pinned set of TRANSITIVE subdependencies (everything that is
# NOT already hard-declared as a top-level dependency in pyproject.toml) so they
# can be pasted into the generated block of [project.dependencies].
#
# WHY THIS EXISTS:
#   poetry.lock is NOT published to PyPI and is NOT consulted by `pip install
#   uvicore[...]`.  Without pinning the transitive closure in pyproject.toml
#   itself, a user's subdependencies can silently drift to whatever pip resolves
#   at install time.  These pins freeze the entire tree into the published
#   package metadata (Requires-Dist).
#
# HOW IT WORKS (no fragile hand-maintained grep chain):
#   - The "omit-list" of top-level names is derived automatically from
#     pyproject.toml.  Crucially, only the HUMAN-authored base dependencies
#     (those ABOVE the `# NOTICE:` marker line) plus every [project.optional-
#     dependencies] extra are treated as top-level — otherwise the generated
#     block below the marker would omit itself and the script would emit nothing.
#   - Resolved versions + environment markers come from poetry.lock, the source
#     of truth for the resolved tree.
#   - Only packages in the "main" dependency group are emitted; the "test" group
#     (pytest, coverage, pluggy, iniconfig, ...) is excluded because it is a
#     dev-only poetry group that is never shipped to PyPI.
#   - Each package's "main"-group environment marker is preserved (converted to
#     PEP 508 single-quote form so the line is a valid double-quoted TOML
#     string).  This keeps conditional deps conditional, e.g. hiredis only with
#     the redis extra, tomli/exceptiongroup only on Python 3.10, colorama only
#     on Windows.
#
# Stdlib-only (tomllib + re); no third-party imports, so it runs under any
# Python >= 3.11 whether or not the poetry venv is active.
#
# USAGE:
#   ./list-subdependencies.sh        # regenerate after any dependency upgrade
#   (then paste the output over the generated block in pyproject.toml)
# ---------------------------------------------------------------------------
set -euo pipefail

# Run from the directory this script lives in (the framework root).
cd "$(cd "$(dirname "$0")" && pwd -P)"

# Prefer the project's poetry venv interpreter when available (guaranteed to be
# a modern Python); otherwise fall back to whatever `python`/`python3` is on
# PATH.  tomllib requires Python >= 3.11.
if command -v poetry >/dev/null 2>&1 && poetry env info -p >/dev/null 2>&1; then
    PY=(poetry run python)
elif command -v python3 >/dev/null 2>&1; then
    PY=(python3)
else
    PY=(python)
fi

"${PY[@]}" - <<'PY'
import re, sys, tomllib

# The marker comment in [project.dependencies] that separates human-authored
# top-level deps (above) from this script's generated subdep pins (below).
NOTICE = "NOTICE:"

def canon(name):
    """PEP 503 normalized name (no `packaging` dependency)."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()

def req_name(spec):
    """Package name from a PEP 508 requirement string."""
    return re.split(r"[\s\[=<>!~;]", spec.strip(), 1)[0]

# --- Human-authored top-level names -> the omit-list ----------------------
# Base deps are read from RAW TEXT and truncated at the NOTICE marker, so the
# generated block never omits itself.  Extras are clean tables -> use tomllib.
declared = set()
in_base = False
for line in open("pyproject.toml", encoding="utf-8"):
    s = line.strip()
    if not in_base:
        if s.replace(" ", "").startswith("dependencies=["):
            in_base = True
        continue
    if NOTICE in s or s == "]":
        break
    if not s or s.startswith("#"):
        continue
    m = re.search(r"""["']([^"']+)["']""", s)
    if m:
        declared.add(canon(req_name(m.group(1))))

proj = tomllib.load(open("pyproject.toml", "rb"))["project"]
for specs in proj.get("optional-dependencies", {}).values():
    declared |= {canon(req_name(x)) for x in specs}
declared.add(canon(proj["name"]))  # uvicore itself

# --- Resolved subdeps from the lock ---------------------------------------
def main_marker(pkg):
    """Environment marker that applies to the 'main' group.

    poetry.lock stores `markers` as a plain string (same for all groups) or a
    per-group dict; a dict without a 'main' key means unconditional for 'main'.
    PEP 508 accepts single-quoted marker values, so the whole requirement stays
    a valid double-quoted TOML string.
    """
    m = pkg.get("markers", "")
    if isinstance(m, dict):
        m = m.get("main", "")
    return m.replace('"', "'")

lock = tomllib.load(open("poetry.lock", "rb"))
rows = []
for pkg in lock["package"]:
    if "main" not in pkg.get("groups", []):
        continue  # skip dev/test-only groups (never published)
    name = canon(pkg["name"])
    if name in declared:
        continue  # already pinned at top level
    rows.append((name, pkg["version"], main_marker(pkg)))

if not rows:
    sys.exit(
        "list-subdependencies: produced 0 subdependencies — this usually means "
        "the '# NOTICE:' marker is missing from [project.dependencies] (so every "
        "generated pin was counted as a top-level dep), or poetry.lock is stale. "
        "Run `poetry lock` and ensure the NOTICE marker line is present."
    )

for name, version, marker in sorted(rows):
    req = f"{name}=={version}" + (f" ; {marker}" if marker else "")
    print(f'    "{req}",')

print(f"\n# {len(rows)} subdependencies", file=sys.stderr)
PY
