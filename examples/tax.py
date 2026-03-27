"""
Tax Domain Pack — Reference Implementation
===========================================

Extends Amnesia with categories optimized for tax strategy and
business financial context. Designed for SwarmIQ and similar
AI-assisted tax advisory products.

The AI agent uses this domain to:
  - Avoid repeating questions already answered in prior sessions
  - Remember the user's entity structure, strategies already discussed,
    and their preferences for engagement
  - Surface relevant answers from prior conversations without re-asking

Customer namespace stores per-client context:
  - Entity structure and account facts
  - Strategies discussed and whether client accepted/rejected them
  - Deductions already identified
  - Deadlines and obligations
  - How the client likes to communicate

Global namespace (SaaS, seeded by operator) stores:
  - IRS publication summaries
  - Common strategy explanations
  - Deduction requirement checklists
  - Deadline calendars
  - Tax code frameworks

Install (standalone):
    cp tax.py ~/.amnesia/packs/

Install (SaaS):
    Copy to configured packs directory and restart amnesia-saas.
"""

from amnesia.registry import register_domain

register_domain(
    domain="tax",
    description="Tax strategy and business financial advisory context",
    categories=[
        "entity_structure",
        # Legal and tax structure of the business or individual.
        # Changes rarely — very long decay.
        # e.g. "Client operates as single-member LLC taxed as S-Corp"
        # e.g. "Business has two partners: 60/40 split, both materially participate"

        "deduction",
        # Identified deductions the client qualifies for.
        # e.g. "Home office deduction confirmed: 200 sq ft dedicated space, sole use"
        # e.g. "Vehicle mileage: client uses personal vehicle 80% for business"

        "strategy",
        # Tax strategies discussed and their current status.
        # Always note whether the client accepted, rejected, or is considering.
        # e.g. "Augusta Rule strategy discussed. Client interested but wants to review IRS requirements."
        # e.g. "Backdoor Roth IRA — client rejected, already has pre-tax IRA"

        "obligation",
        # Tax deadlines, estimated payments, and filing obligations.
        # Shorter decay — once the deadline passes, the memory is stale.
        # e.g. "Q3 estimated payment due September 15. Client plans to pay."
        # e.g. "Extension filed — return due October 15"

        "fact",
        # Facts established through conversation that inform strategy.
        # These are answers to questions — stored so they're never re-asked.
        # e.g. "Client's spouse is a W-2 employee, not part of the business"
        # e.g. "Client's primary office is rented, not home-based"

        "preference",
        # How the client prefers to engage and their communication style.
        # e.g. "Client prefers plain language explanations, not tax jargon"
        # e.g. "Client is risk-averse on aggressive strategies — prefers conservative positions"
    ],
    decay_windows={
        # Obligations are time-bound — archive after deadline passes
        "obligation":        90,    # quarterly cadence

        # Strategies and deductions remain relevant for a full tax year
        "strategy":         365,
        "deduction":        365,
        "fact":             365,
        "preference":       730,

        # Entity structure is nearly permanent
        "entity_structure": 1825,   # 5 years
    },
)
