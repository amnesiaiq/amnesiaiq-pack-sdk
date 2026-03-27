"""
Trading Domain Pack — Reference Implementation
================================================

Extends Amnesia with categories and decay windows optimized for
options and equities trading context.

Suitable for:
  - NeoSwarm (SaaS, multi-customer)
  - Personal trading journal (standalone)

Customer namespace stores per-trader context:
  - Their personal risk rules
  - Their preferred strategies and instruments
  - Active positions and recent trade notes
  - Observed behavioral patterns

Global namespace (SaaS, seeded by operator) stores:
  - Options strategy definitions
  - Greek explanations
  - Risk management frameworks
  - Market regime descriptions

Install (standalone):
    cp trading.py ~/.amnesia/packs/

Install (SaaS):
    Copy to configured packs directory and restart amnesia-saas.
    Then seed global knowledge:
        amnesia-saas-admin global seed-file \\
            --product neoswarm \\
            --file neoswarm_trading_knowledge.jsonl
"""

from amnesia.registry import register_domain

register_domain(
    domain="trading",
    description="Options and equities trading context",
    categories=[
        # ── Core trading categories ──────────────────────────────────────────

        "strategy",
        # Trading setups, recurring playbooks, and approaches.
        # e.g. "User prefers selling premium in high IV environments"
        # e.g. "User uses iron condors on SPX every Thursday"

        "risk_rule",
        # Personal risk management rules and position sizing logic.
        # These are the user's non-negotiables — treat them as hard constraints.
        # e.g. "User never risks more than 1% of account on a single trade"
        # e.g. "User does not hold through earnings announcements"

        "market_condition",
        # Current observations about market state.
        # Highly perishable — 3 day decay. Never use stale market context.
        # e.g. "VIX is elevated above 25, IV rank is 80th percentile"
        # e.g. "Market is in a range-bound chop between 4400-4600 on SPX"

        "instrument",
        # Instruments actively traded or on the watchlist.
        # e.g. "User primarily trades SPY, QQQ, and individual tech names"
        # e.g. "User is watching TSLA for a mean-reversion setup"

        "position",
        # Active or recently closed position context.
        # Short decay — stale position data is actively harmful.
        # e.g. "User has an open SPX iron condor expiring Friday"
        # e.g. "Closed AAPL covered call for 60% profit last week"

        "trade_note",
        # Post-trade observations, lessons, and pattern recognition.
        # These build up into behavioral memory over time.
        # e.g. "User tends to close winners too early on momentum trades"
        # e.g. "Entry timing is better when waiting for 9:45am after open"

        # ── NeoSwarm / SaaS additions ────────────────────────────────────────

        "account_context",
        # Account-level constraints and context.
        # e.g. "User has a $50k account, pattern day trader rules apply"
        # e.g. "User is in a Roth IRA — no margin, no short selling"

        "watchlist",
        # Instruments being monitored and the thesis behind watching them.
        # Shorter decay than instrument — watchlist items cycle faster.
        # e.g. "Watching META for a breakout above $500 resistance"

        "tax_consideration",
        # Tax-aware trading context.
        # e.g. "User wants to avoid wash sale rules on MSFT through year-end"
        # e.g. "User prefers long-term holds in taxable account for LTCG rates"
    ],
    decay_windows={
        # Real-time / perishable
        "market_condition":   3,    # market state is stale within days
        "position":           7,    # closed or changed within a week
        "watchlist":         14,    # tickers cycle on and off watchlist

        # Short-lived behavioral context
        "trade_note":        60,    # recent lessons fade but patterns build

        # Stable preferences and context
        "instrument":       180,    # instrument preferences change slowly
        "tax_consideration": 365,   # annual relevance cycle
        "account_context":   365,   # account structure is stable

        # Long-lived rules and strategies
        "strategy":         365,    # hard-won playbooks are stable
        "risk_rule":        730,    # risk rules should almost never expire
    },
)
