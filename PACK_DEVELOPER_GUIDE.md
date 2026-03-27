# Amnesia Pack Developer Guide
_Version 0.1.0 | amnesia-core_

---

## What Is a Domain Pack?

Amnesia is a universal memory engine for AI agents. Out of the box it stores and retrieves memories using seven generic categories: `preference`, `fact`, `goal`, `skill`, `behavior_pattern`, `relationship`, `opinion`.

A **domain pack** extends this with vocabulary specific to a context — trading, tax, gaming, cooking, legal, fitness, whatever. The memory engine stays identical. The pack just tells it what words to use and how long things should stay relevant.

**One Python file. One function call. That's it.**

A pack that took 10 minutes to write gives every customer of a vertical SaaS product a memory system that speaks their language natively.

---

## Quick Start

```python
# my_pack.py
from amnesia.registry import register_domain

register_domain(
    domain="cooking",
    description="Culinary preferences, techniques, and recipe context",
    categories=[
        "recipe",
        "technique",
        "ingredient",
        "dietary_restriction",
    ],
    decay_windows={
        "recipe":              180,
        "technique":           365,
        "ingredient":          365,
        "dietary_restriction": 1825,  # 5 years — allergies don't go away
    },
)
```

Drop this file in `~/.amnesia/packs/` and restart Amnesia. Done. The AI can now store and retrieve memories in these categories using natural language.

---

## The API

### `register_domain(domain, categories, decay_windows, description)`

**`amnesia.registry.register_domain`**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | `str` | Yes | Unique identifier. Lowercase, underscores ok. e.g. `"trading"`, `"tax"` |
| `categories` | `list[str]` | Yes | Custom category names for this domain |
| `decay_windows` | `dict[str, int]` | No | Per-category decay in days. Keys must be in `categories`. |
| `description` | `str` | No | Human-readable description shown in `/health` and `show_memory` |

**Rules:**
- `domain` must be unique across all installed packs
- Category names must be valid Python identifiers (lowercase, underscores)
- Decay windows are in days; must be positive integers
- Categories extend the base set — they do not replace it
- A category without a decay window falls back to source-based defaults (see below)

**Source-based decay defaults (when no pack override is set):**

| Source | Default decay |
|--------|---------------|
| `explicit_statement` | 90 days |
| `observed_behavior` | 60 days |
| `inferred` | 30 days |
| `third_party` | 45 days |

---

## Base Categories (Always Available)

These seven categories are always available in every domain. You do not need to include them in your pack — they're automatic.

| Category | What goes here |
|----------|----------------|
| `preference` | Things the user likes, dislikes, or prefers |
| `fact` | Factual information about the user |
| `goal` | Things the user is working toward |
| `skill` | Areas of expertise or things being learned |
| `behavior_pattern` | How the user tends to approach things |
| `relationship` | People in the user's life |
| `opinion` | The user's views on topics |

Your pack categories are additive. A memory in the `trading` domain can use both `risk_rule` (pack category) and `preference` (base category).

---

## Designing Categories

### The right granularity

Too broad and the AI stores everything in one category — hard to filter and recall precisely. Too narrow and categories overlap — the AI gets confused about where to file things.

**Good:** `strategy`, `risk_rule`, `market_condition`, `instrument`
**Too broad:** `trading_stuff`
**Too narrow:** `covered_call_strategy`, `put_spread_strategy`, `iron_condor_strategy`

A good rule of thumb: if you can't write a one-sentence definition of what belongs in a category, split it or merge it.

### Category naming

- Lowercase only
- Underscores for multi-word names
- Nouns or noun phrases, not verbs
- Should be self-explanatory to the AI without additional context

```python
# Good
categories=["strategy", "risk_rule", "market_condition", "trade_note"]

# Bad
categories=["doStrategy", "RiskRule", "what-market-is-doing", "notes"]
```

### When to use base categories vs. custom ones

Ask: "would this make sense outside this domain?"

- "User prefers dark mode" → `preference` (base) — not domain-specific
- "User's risk tolerance is conservative" → `preference` or domain-specific `risk_profile` depending on how much trading detail you need
- "User never holds overnight during earnings" → `risk_rule` (domain-specific) — this is specifically a trading construct

---

## Designing Decay Windows

Decay is how long a memory stays active before it becomes eligible for archiving. Set it based on how quickly the information becomes stale or misleading.

### Decision guide

| Type of information | Suggested range | Rationale |
|---------------------|-----------------|-----------|
| Real-time state (prices, conditions, availability) | 1–3 days | Stale data is actively harmful |
| Short-lived context (open positions, current projects, appointments) | 7–14 days | Changes frequently |
| Behavioral patterns being formed | 30–60 days | Needs time to establish |
| Preferences and tendencies | 180–365 days | Stable but can evolve |
| Stable facts (account type, expertise level) | 365–730 days | Rarely changes |
| Core rules and values | 730–1825 days | Almost permanent |
| Permanent facts (allergies, disabilities, identity) | 3650+ days | Never expires |

### What happens when a memory expires?

It moves to `archive` layer. It stops appearing in recalls and semantic search. It is NOT deleted — the full lineage is preserved. If the same information is restated, a new memory is created.

### Don't over-decay

Setting everything to 7 days will cause Amnesia to forget useful context before it can be consolidated into long-term memory. Users will feel like it "never remembers anything." When in doubt, err toward longer decay and let the AI's consolidation process trim the noise.

### Don't under-decay

Stale data in an active recall causes the AI to use outdated context confidently. A position that closed two weeks ago should not be surfacing as current. Market conditions from last month are worse than useless. Be aggressive on time-sensitive categories.

---

## Standalone vs. SaaS Deployment

### Standalone (local, personal use)

Pack file goes in `~/.amnesia/packs/`. Loaded at server startup. All memories are single-user.

```bash
cp my_pack.py ~/.amnesia/packs/
amnesia-serve   # or restart if already running
```

Verify it loaded:
```bash
curl http://localhost:18788/health
# "domain_packs": [{"domain": "my_domain", ...}]
```

### SaaS (multi-tenant, NeoSwarm / SwarmIQ / etc.)

The SaaS adapter loads packs at server startup from a configured directory. Pack installation is the same file-drop mechanism.

Additionally, the SaaS adapter has a **global namespace** — a shared pool of memories accessible to every customer of a product, maintained by the product operator (you). This is where domain knowledge lives.

**Customer namespace** (per-tenant):
- Customer-specific preferences, patterns, history
- Written by the AI during conversations
- Queried first, highest relevance

**Global namespace** (product-level, admin-managed):
- Domain knowledge, reference material, frameworks
- Written by the operator via the admin CLI
- Merged into every customer's recall at 0.95x relevance weight

The pack file defines the categories used in both namespaces. The categories are the same — the namespace just controls who can see what.

**Seeding the global namespace:**

```bash
# Single entry
amnesia-saas-admin global seed \
  --product neoswarm \
  --category strategy \
  --domain trading \
  --content "Iron condor: sell OTM call spread + OTM put spread simultaneously. Max profit when underlying stays between short strikes at expiration. Best in high IV environments (IVR > 50)."

# Bulk from file (JSONL)
amnesia-saas-admin global seed-file \
  --product neoswarm \
  --file knowledge_base.jsonl
```

**JSONL format:**
```json
{"content": "...", "category": "strategy", "domain": "trading", "confidence": 0.95}
{"content": "...", "category": "risk_rule", "domain": "trading", "confidence": 0.95}
```

---

## Memory Flow in a Domain Pack

When a customer of a NeoSwarm-style product interacts with the AI:

```
1. User says something relevant to trading
       ↓
2. AI calls remember_context(
       content="User never holds positions overnight during earnings",
       category="risk_rule",
       domain="trading",
       confidence=1.0,
       source="explicit_statement"
   )
       ↓
3. Amnesia validates: is "risk_rule" a valid category in domain "trading"? Yes.
       ↓
4. Decay window looked up: risk_rule → 730 days
       ↓
5. Memory stored in customer namespace with decay_at = now + 730 days

--- Next session ---

6. AI calls recall_context(query="what are this user's trading rules", domain="trading")
       ↓
7. Amnesia searches customer namespace → finds risk_rule memory
   Also searches global namespace → finds product risk frameworks
       ↓
8. Merged results returned, customer memory ranked above global at equal score
       ↓
9. AI uses context naturally: "Given your rule about overnight holds during earnings..."
```

---

## Confidences and Sources

When the AI stores a memory, it assigns a confidence and source. Your pack doesn't control these directly, but understanding them helps you design the right categories.

| Source | When used | Default confidence |
|--------|-----------|-------------------|
| `explicit_statement` | User directly stated something | 0.9–1.0 |
| `observed_behavior` | Inferred from how the user acted | 0.5–0.7 |
| `inferred` | Logical deduction from context | 0.4–0.6 |
| `third_party` | Information about someone else | 0.5–0.8 |

High-confidence explicit statements go directly to `long_term` layer. Lower-confidence items start in `short_term` and are promoted over time through repeated access.

**Design implication:** Categories for things users explicitly state (risk rules, preferences) will accumulate high-confidence memories. Categories for observed patterns (behavior_pattern, trade_note) will accumulate lower-confidence memories that strengthen over time. Design your decay windows accordingly.

---

## Validation

Before deploying, run the validator:

```bash
python validate_pack.py my_pack.py
```

The validator checks:
- `register_domain` was called exactly once
- Domain name is valid (lowercase, no spaces)
- All categories are valid Python identifiers
- Decay windows reference valid category names
- No category name conflicts with base categories
- Decay values are positive integers

---

## SaaS Pack Design — When Your Pack Runs Invisibly

In a standalone deployment, the user knows AmnesiaIQ exists. They can run CLI commands, see memory categories in `show_memory` output, and ask the AI what it remembers about them. The memory system is a visible feature.

In a SaaS deployment — NeoSwarm, SwarmIQ, ZofiaTrail — the user never knows AmnesiaIQ exists. They interact with the product's AI, and that AI simply knows things about them. There is no exposed memory layer. No commands to run. No categories to browse. The memory system is infrastructure, not a feature.

This changes what good pack design looks like.

---

### 1. Category names must make sense to the AI, not to the user

In standalone, category names appear in `show_memory` output that users see directly. Friendly names matter: "Your Trading Rules" over `risk_rule`.

In SaaS, category names are only ever seen by the AI agent and by support staff diagnosing issues. The user never reads them. Name for precision and clarity to the model:

```python
# Standalone-friendly naming (user-visible)
categories=["Your Trading Rules", "Account Info", "Preferences"]

# SaaS-appropriate naming (AI-visible, never user-visible)
categories=["risk_rule", "account_profile", "preference"]
```

Technical, lowercase, underscore-separated names are the right choice for SaaS packs. They are unambiguous to the AI when it decides where to file a memory.

---

### 2. The system prompt matters more

In standalone, a user can ask "what do you remember about me?" and the AI can give a transparent answer referencing memory categories and stored facts.

In SaaS, the AI should never reference the memory system, AmnesiaIQ, or memory categories. If a user asks "how do you know that about me?", the correct answer is "you mentioned it in an earlier conversation" — not any reference to a memory system or stored data.

Pack authors should include product-specific system prompt guidance alongside the pack file. At minimum, this guidance should cover:

- What the AI should say when asked how it knows something about the user
- What the AI should never say (AmnesiaIQ, memory categories, "I stored that", etc.)
- How to surface recalled context naturally, as knowledge rather than retrieval

The SaaS deployment removes the `unless asked` qualifier from memory mechanics guidance in the base system prompt. In SaaS, memory operations are always invisible, full stop.

---

### 3. Global namespace is the product's knowledge layer

For SaaS packs, the global namespace is as important as the customer namespace. Both use categories defined by the pack — but what goes into global is the operator's domain expertise, not individual customer data.

The global namespace is the operator's competitive moat. It encodes their domain knowledge as AI-accessible memory that every customer benefits from without the AI needing to rediscover it.

Examples of what belongs in global:

- **Trading:** Options strategy definitions, risk framework descriptions, Greek explanations, common pattern annotations
- **Tax:** IRS publication summaries, deduction requirement checklists, filing deadline frameworks, entity structure comparisons

Pack authors should include a recommended global knowledge JSONL structure alongside the pack file — a template showing what the operator should seed on deployment.

```json
{"content": "Iron condor: sell OTM call spread + OTM put spread simultaneously. Max profit when underlying stays between short strikes at expiration. Best in high IVR environments (IVR > 50).", "category": "strategy", "domain": "trading", "confidence": 0.95}
{"content": "Delta-neutral: position constructed so that small moves in the underlying do not change total position value. Common in volatility trading.", "category": "strategy", "domain": "trading", "confidence": 0.95}
```

---

### 4. Decay windows have different stakes

In standalone, a decayed memory is mildly inconvenient. The user notices the AI forgot something, re-states it, and moves on.

In SaaS, a decayed memory causes the AI to re-ask a question the user already answered. That is a product quality failure — it signals that the product doesn't know its own customers. Users do not blame the memory system; they blame the product.

Err toward longer decay windows for SaaS packs, especially for any fact gathered through an onboarding or setup flow. If there is any doubt between a 180-day and a 365-day window for a stable customer fact, choose 365.

---

### 5. The onboarding window

In SaaS, the first few conversations are when the most important facts about a customer get stored. The AI is asking clarifying questions, learning preferences, understanding goals. This is the onboarding window, and it is the highest-value memory accumulation period in the customer lifecycle.

Design your pack with this mental model: what are the 5–10 things the AI should know about a customer within their first week? Those are your onboarding-critical categories. They need:

- The longest decay windows in the pack
- Priority in the AI's recall — these facts shape every subsequent interaction
- Explicit documentation in the pack file so the operator knows which categories to monitor

For a trading pack, onboarding-critical categories might be: `account_profile`, `risk_rule`, `strategy`, `instrument`. For a tax pack: `entity_structure`, `obligation`, `fact`.

---

### Recommended additions to a SaaS pack file

Beyond `register_domain`, a SaaS pack should include:

**`GLOBAL_KNOWLEDGE_SCHEMA` comment block** — describes what the operator should seed into the global namespace. What categories, what kind of content, and at what confidence level. This makes onboarding a new operator deployment straightforward.

**Suggested system prompt additions** — what the AI should say when asked how it knows something, what it should never say, and how to surface recalled context naturally as product knowledge rather than retrieved data.

**Onboarding-critical annotation** — a comment on each category flagging whether it is onboarding-critical and what happens to the product experience if it decays prematurely.

---

### Example: trading pack SaaS annotations

```python
# packs/trading.py

# GLOBAL_KNOWLEDGE_SCHEMA
# Seed the global namespace with the following before going live:
#   - category: strategy     → definitions for all primary options strategies
#   - category: risk_rule    → standard risk frameworks (Kelly criterion, max drawdown thresholds)
#   - category: instrument   → asset class descriptions and common characteristics
# See: knowledge_base_trading.jsonl (included with this pack)
#
# SYSTEM PROMPT ADDITIONS
# Add to the product system prompt:
#   "You have detailed knowledge of each customer's trading style, risk rules, and
#    current positions from prior conversations. Surface this knowledge naturally —
#    never reference a memory system or explain how you know something. If asked,
#    say it came up in an earlier conversation."
#   "Never mention AmnesiaIQ, memory categories, or memory storage."
#
# ONBOARDING-CRITICAL CATEGORIES (long decay, capture early)
#   risk_rule       — ONBOARDING CRITICAL. Decay 730 days minimum.
#   account_profile — ONBOARDING CRITICAL. Decay 1825 days minimum.
#   strategy        — ONBOARDING CRITICAL. Decay 365 days minimum.

register_domain(
    domain="trading",
    description="Options and equity trading context: strategies, risk rules, positions, instruments",
    categories=[
        "strategy",       # Approach to the market (defined strategies, style)
        "risk_rule",      # Hard rules: max loss per trade, no overnight holds, etc.
        "account_profile",# Account type, size, broker, experience level
        "position",       # Open or recently closed positions (short decay)
        "instrument",     # Specific instruments the customer trades or watches
        "market_note",    # Time-sensitive observations about market conditions
        "trade_note",     # Notes tied to specific past trades
    ],
    decay_windows={
        "strategy":        365,
        "risk_rule":       730,
        "account_profile": 1825,
        "position":          14,
        "instrument":       365,
        "market_note":        3,
        "trade_note":        90,
    },
)
```

---

## Coming in Phase 3: Advanced Pack Hooks

The following hooks will be added in Phase 3. Document them here for awareness — do not implement yet.

### `validate(content, category, domain) -> str | None`

Called before a memory is stored. Return an error string to reject the memory, `None` to accept.

```python
def validate(content: str, category: str, domain: str) -> str | None:
    if category == "risk_rule" and len(content) < 20:
        return "Risk rules must be descriptive (min 20 characters)"
    return None
```

### `on_recall(memories, context) -> list`

Called after recall returns results. Allows domain-specific reranking. The returned list must be a non-empty subset of the input — the core engine validates this.

```python
def on_recall(memories: list, context) -> list:
    # Example: push risk_rule memories to the top for trading queries
    risk_rules = [m for m in memories if m["category"] == "risk_rule"]
    rest = [m for m in memories if m["category"] != "risk_rule"]
    return risk_rules + rest
```

These hooks are loaded automatically if present in the pack file. No registration needed.

---

## Complete Reference: All Fields

When a memory is stored, it contains these fields. Your pack influences `category`, `domain`, and `decay_at`.

| Field | Set by | Description |
|-------|--------|-------------|
| `id` | System | UUID |
| `content` | AI | The memory text |
| `category` | AI (from pack) | Category name |
| `domain` | AI | Domain name (your pack's domain) |
| `confidence` | AI | 0.0–1.0 |
| `source` | AI | explicit_statement / inferred / observed_behavior / third_party |
| `layer` | System | short_term / long_term / archive |
| `decay_at` | System (from pack) | Expiry timestamp, based on pack's decay_window |
| `supersedes` | System | ID of memory this replaces |
| `superseded_by` | System | ID of memory that replaced this |
| `supersede_reason` | System | correction / changed / evolved / clarification / extends / derives |
| `consolidated_from` | System | Source memory IDs if this is a consolidated memory |
| `created_at` | System | Timestamp |
| `last_accessed` | System | Updated on every recall |
| `access_count` | System | Number of times recalled |

---

## Checklist Before Shipping a Pack

- [ ] Domain name is unique and descriptive
- [ ] Every category has a one-sentence definition in comments
- [ ] Decay windows are set for all time-sensitive categories
- [ ] Permanent or near-permanent data uses long decay (730+ days)
- [ ] Ephemeral data uses short decay (3–14 days)
- [ ] `validate_pack.py` passes with no errors
- [ ] Pack has been tested with a live Amnesia server (`amnesia-serve`)
- [ ] If SaaS: global namespace seed content has been prepared as a JSONL file
- [ ] Description field is filled in (shows in `/health` and `show_memory`)
