"""
Amnesia Domain Pack Template
=============================

Copy this file, rename it to your domain (e.g. cooking.py, legal.py),
and fill in the sections marked with TODO.

Deployment:
  Standalone:  cp my_pack.py ~/.amnesia/packs/
  SaaS:        copy to your configured packs directory and restart amnesia-saas

See PACK_DEVELOPER_GUIDE.md for full documentation.
"""

from amnesia.registry import register_domain

# ---------------------------------------------------------------------------
# TODO: Replace all values below with your domain specifics
# ---------------------------------------------------------------------------

register_domain(

    # ── Identity ──────────────────────────────────────────────────────────────
    # Unique name for this domain. Lowercase, underscores ok.
    # Used as the `domain` field on every memory in this pack.
    domain="my_domain",  # TODO: e.g. "cooking", "legal", "fitness"

    # Human-readable description. Shown in /health output and show_memory.
    description="TODO: one-line description of this domain",

    # ── Categories ────────────────────────────────────────────────────────────
    # Custom category names for this domain.
    # These ADD TO the seven base categories (preference, fact, goal, skill,
    # behavior_pattern, relationship, opinion) — they do not replace them.
    #
    # Naming rules:
    #   - Lowercase only
    #   - Underscores for multi-word names
    #   - Nouns or noun phrases (not verbs)
    #   - Should be self-explanatory to an AI without extra context
    #
    # Each category should have a clear, distinct purpose.
    # If you can't define it in one sentence, reconsider the granularity.
    categories=[
        # TODO: Replace with your domain-specific categories.
        # Include a comment for each explaining what belongs here.

        "category_one",     # TODO: what belongs in this category
        "category_two",     # TODO: what belongs in this category
        "category_three",   # TODO: what belongs in this category
    ],

    # ── Decay Windows ─────────────────────────────────────────────────────────
    # How long (in days) memories in each category stay active before
    # becoming eligible for archiving.
    #
    # Set for every category that has a meaningful shelf life.
    # Categories without a decay window use source-based defaults:
    #   explicit_statement: 90 days
    #   observed_behavior:  60 days
    #   inferred:           30 days
    #   third_party:        45 days
    #
    # Decay guidelines:
    #   Real-time / rapidly changing data    →   1–7 days
    #   Short-lived state / current context  →   7–30 days
    #   Behavioral patterns forming          →   30–90 days
    #   Preferences and tendencies           →   180–365 days
    #   Stable rules / frameworks            →   365–730 days
    #   Near-permanent facts                 →   730–3650 days
    #
    # Keys must exactly match category names above.
    decay_windows={
        # TODO: Set decay for each category.
        # Delete this comment and the examples, keep only your real windows.

        "category_one":   90,   # TODO: why this many days?
        "category_two":  365,   # TODO: why this many days?
        # category_three intentionally omitted — falls back to source default
    },
)


# ---------------------------------------------------------------------------
# PHASE 3 HOOKS (not yet active — implement when Phase 3 ships)
# ---------------------------------------------------------------------------
# Uncomment and implement when Phase 3 is released.
# These hooks are loaded automatically if present in the file.

# def validate(content: str, category: str, domain: str) -> str | None:
#     """
#     Called before a memory is stored in this domain.
#     Return an error string to reject. Return None to accept.
#
#     Example: enforce minimum length on certain categories.
#     """
#     # TODO: Add domain-specific validation rules
#     return None


# def on_recall(memories: list, context) -> list:
#     """
#     Called after recall returns results. Allows domain-specific reranking.
#     Must return a non-empty subset of the input list.
#
#     Example: push high-priority categories to the top.
#     """
#     # TODO: Add domain-specific ranking logic
#     return memories
