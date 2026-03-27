# Amnesia Pack SDK

Everything a developer (or AI assistant) needs to build a custom domain pack for Amnesia.

---

## What's in this SDK

```
pack-sdk/
  README.md                  ← you are here
  PACK_DEVELOPER_GUIDE.md    ← full specification and design guide
  pack_template.py           ← annotated starter template
  validate_pack.py           ← validator script — run before deploying
  examples/
    trading.py               ← NeoSwarm trading pack (options/equities)
    tax.py                   ← SwarmIQ tax advisory pack
    gaming.py                ← ZofiaTrail gaming companion pack
```

---

## 60-Second Start

**1. Copy the template:**
```bash
cp pack_template.py my_domain.py
```

**2. Fill it in** — open `my_domain.py` and replace the TODOs with your domain, categories, and decay windows. See `examples/` for complete reference implementations.

**3. Validate:**
```bash
python validate_pack.py my_domain.py
```

**4a. Deploy (standalone / personal use):**
```bash
cp my_domain.py ~/.amnesia/packs/
# Restart amnesia-serve
```

**4b. Deploy (SaaS — NeoSwarm, SwarmIQ, etc.):**
```bash
# Copy to server's packs directory and restart amnesia-saas
# Then seed global knowledge (optional but recommended):
amnesia-saas-admin global seed-file \
  --product YOUR_PRODUCT \
  --file my_global_knowledge.jsonl
```

---

## Core Concept

A pack defines:
- **Categories** — the vocabulary the AI uses to file memories
- **Decay windows** — how long each type of memory stays active

The memory engine (embedding search, contradiction detection, consolidation, scoring) is unchanged — your pack just tells it what words to use and how long things matter.

The AI does the rest. It decides what to remember, how confident to be, and when to update existing memories. Your pack shapes the vocabulary, not the behavior.

---

## The API (one function)

```python
from amnesia.registry import register_domain

register_domain(
    domain="my_domain",          # unique identifier
    description="...",           # shown in /health output
    categories=["cat1", "cat2"], # custom category names
    decay_windows={              # per-category expiry in days
        "cat1": 30,
        "cat2": 365,
    },
)
```

That's the entire public API for pack authors. Read `PACK_DEVELOPER_GUIDE.md` for full details on category design, decay window guidelines, global namespace seeding, and upcoming Phase 3 hooks.

---

## For AI Assistants Building a Pack

If you are an AI assistant being asked to build a pack for a specific product, here is the process:

**1. Understand the domain.** Ask what the product does and what context the AI agent needs to remember across sessions. The goal is to avoid repeating questions and to personalize responses.

**2. Design categories.** Each category is a bucket for one type of information. Aim for 4–8 categories. Use the base categories (`preference`, `fact`, `goal`, etc.) for generic information — only add domain-specific categories for things the base set can't express.

**3. Set decay windows.** Ask: how quickly does this information become stale or misleading? Real-time data (market conditions, open positions) needs short decay. Rules and preferences need long decay. See the decay guidelines in `PACK_DEVELOPER_GUIDE.md`.

**4. Consider the global namespace.** For SaaS products, there is a global knowledge base accessible to all customers. This is where product-level expertise lives (tax code references, trading strategy definitions, game lore). Design what should go there alongside what goes in customer-scoped memory.

**5. Write the pack, validate it, propose a global knowledge JSONL.** The global JSONL is separate from the pack file — it's the content the operator seeds into the global namespace.

**6. Review with the operator.** The decay windows especially are judgment calls that the domain expert (the product owner) should sign off on.

---

## Requirements

- Python 3.11+
- `amnesia-core` installed (for `amnesia.registry`) OR use `validate_pack.py` standalone (it shims the import)

To install amnesia-core for local development:
```bash
pip install amnesia-core
# or from source:
pip install /path/to/Amnesia/packages/core/
```
