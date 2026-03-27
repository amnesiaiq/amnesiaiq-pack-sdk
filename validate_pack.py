#!/usr/bin/env python3
"""
Amnesia Pack Validator
======================

Validates a domain pack file before deployment.

Usage:
    python validate_pack.py my_pack.py
    python validate_pack.py packs/trading.py

Checks:
  - register_domain() is called exactly once
  - domain name is valid
  - all categories are valid identifiers
  - decay windows reference valid category names
  - decay values are positive integers
  - no conflicts with base categories
  - description is present
"""

import importlib.util
import sys
import traceback
from pathlib import Path
from unittest.mock import MagicMock, patch

# Base categories always present — cannot be redefined by a pack
BASE_CATEGORIES = {
    "preference", "fact", "goal", "skill",
    "behavior_pattern", "relationship", "opinion",
}

ERRORS = []
WARNINGS = []


def error(msg: str):
    ERRORS.append(f"  ERROR: {msg}")


def warn(msg: str):
    WARNINGS.append(f"  WARN:  {msg}")


def validate(pack_path: Path):
    print(f"\nValidating: {pack_path}\n{'─' * 50}")

    if not pack_path.exists():
        print(f"  ERROR: File not found: {pack_path}")
        sys.exit(1)

    # ── Step 1: Capture the register_domain call ─────────────────────────────
    calls = []

    def mock_register_domain(domain, categories, decay_windows=None, description=""):
        calls.append({
            "domain": domain,
            "categories": list(categories),
            "decay_windows": dict(decay_windows or {}),
            "description": description,
        })

    # Patch register_domain and execute the pack file
    try:
        spec = importlib.util.spec_from_file_location("pack_under_test", pack_path)
        module = importlib.util.module_from_spec(spec)

        with patch("amnesia.registry.register_domain", side_effect=mock_register_domain):
            # Also patch the direct import in case the pack does:
            # from amnesia.registry import register_domain
            import amnesia.registry as reg_module
            original = reg_module.register_domain
            reg_module.register_domain = mock_register_domain
            try:
                spec.loader.exec_module(module)
            finally:
                reg_module.register_domain = original

    except ImportError as e:
        # amnesia.registry may not be on path when running standalone
        # Fall back to direct execution with a shim
        calls = _execute_with_shim(pack_path)
    except Exception as e:
        print(f"  ERROR: Failed to load pack: {e}")
        traceback.print_exc()
        sys.exit(1)

    # ── Step 2: Check call count ──────────────────────────────────────────────
    if len(calls) == 0:
        error("register_domain() was never called")
        _report()
        return
    if len(calls) > 1:
        error(f"register_domain() was called {len(calls)} times — only one call per pack file")

    reg = calls[0]

    # ── Step 3: Validate domain name ─────────────────────────────────────────
    domain = reg["domain"]
    if not domain:
        error("domain is empty")
    elif not domain.replace("_", "").isalnum():
        error(f"domain '{domain}' must be lowercase alphanumeric with underscores only")
    elif domain != domain.lower():
        error(f"domain '{domain}' must be lowercase")
    else:
        print(f"  domain:      {domain}")

    # ── Step 4: Validate description ─────────────────────────────────────────
    desc = reg["description"]
    if not desc:
        warn("description is empty — it shows in /health and show_memory")
    else:
        print(f"  description: {desc}")

    # ── Step 5: Validate categories ──────────────────────────────────────────
    categories = reg["categories"]
    if not categories:
        error("categories list is empty — a pack must define at least one category")
    else:
        print(f"  categories ({len(categories)}):")
        for cat in categories:
            if not cat:
                error("empty category name found")
            elif not cat.replace("_", "").isalnum():
                error(f"  category '{cat}' must be alphanumeric with underscores only")
            elif cat != cat.lower():
                error(f"  category '{cat}' must be lowercase")
            elif cat in BASE_CATEGORIES:
                warn(f"  category '{cat}' shadows a base category — it's already available without the pack")
            else:
                print(f"    + {cat}")

    # ── Step 6: Validate decay windows ───────────────────────────────────────
    decay = reg["decay_windows"]
    categories_set = set(categories)

    if decay:
        print(f"  decay_windows ({len(decay)}):")
        for cat, days in decay.items():
            if cat not in categories_set:
                error(f"  decay key '{cat}' is not in categories list")
            elif not isinstance(days, int) or days <= 0:
                error(f"  decay value for '{cat}' must be a positive integer (got {days!r})")
            else:
                print(f"    {cat}: {days} days")
    else:
        warn("no decay_windows set — all categories will use source-based defaults (30–90 days)")

    # ── Step 7: Check for missing decay on time-sensitive patterns ─────────────
    time_sensitive_patterns = [
        "condition", "state", "current", "price", "position",
        "open", "active", "live", "realtime", "real_time",
    ]
    for cat in categories:
        if any(p in cat for p in time_sensitive_patterns) and cat not in decay:
            warn(f"  category '{cat}' looks time-sensitive but has no decay window")

    _report()


def _execute_with_shim(pack_path: Path) -> list:
    """
    Execute a pack file with a shim for amnesia.registry
    when the amnesia package is not installed.
    """
    calls = []

    def register_domain(domain, categories, decay_windows=None, description=""):
        calls.append({
            "domain": domain,
            "categories": list(categories),
            "decay_windows": dict(decay_windows or {}),
            "description": description,
        })

    import types
    amnesia_mod = types.ModuleType("amnesia")
    registry_mod = types.ModuleType("amnesia.registry")
    registry_mod.register_domain = register_domain
    amnesia_mod.registry = registry_mod
    sys.modules["amnesia"] = amnesia_mod
    sys.modules["amnesia.registry"] = registry_mod

    spec = importlib.util.spec_from_file_location("pack_under_test", pack_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return calls


def _report():
    print()
    if WARNINGS:
        for w in WARNINGS:
            print(w)
    if ERRORS:
        for e in ERRORS:
            print(e)
        print(f"\nResult: FAILED ({len(ERRORS)} error(s), {len(WARNINGS)} warning(s))\n")
        sys.exit(1)
    else:
        status = f"OK" if not WARNINGS else f"OK with {len(WARNINGS)} warning(s)"
        print(f"Result: {status}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_pack.py <pack_file.py>")
        sys.exit(1)
    validate(Path(sys.argv[1]))
