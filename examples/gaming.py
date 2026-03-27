"""
Gaming Domain Pack — Reference Implementation
==============================================

Extends Amnesia with categories for game-specific memory context.
Designed for ZofiaTrail and similar AI-assisted gaming products.

The AI companion uses this domain to:
  - Remember how the player plays without re-asking
  - Pick up where the player left off in story/progression
  - Personalize difficulty, hints, and companion behavior
  - Remember squad members, in-game relationships, and social context

Customer namespace stores per-player context:
  - Play style, difficulty preferences, control preferences
  - Story position and completed content
  - Behavioral patterns (what they struggle with, what they excel at)
  - In-game relationships and social preferences

Global namespace (SaaS, seeded by operator) stores:
  - Game lore and world knowledge
  - Strategy guides and tips
  - Zone/dungeon walkthrough summaries
  - Achievement and unlock requirements

Install (standalone):
    cp gaming.py ~/.amnesia/packs/

Install (SaaS):
    Copy to configured packs directory and restart amnesia-saas.
"""

from amnesia.registry import register_domain

register_domain(
    domain="gaming",
    description="Game context, player preferences, and progression memory",
    categories=[
        "playstyle",
        # How the player approaches the game.
        # e.g. "Player prefers stealth over direct combat"
        # e.g. "Player likes to explore everything before advancing the story"
        # e.g. "Player sets difficulty to Hard but uses hints for puzzles"

        "progression",
        # Story position, completed quests, unlocked content.
        # Long decay — progression is permanent.
        # e.g. "Completed Act 2. Has not started the northern dungeon."
        # e.g. "Unlocked the blacksmith crafting system. Has not upgraded weapons yet."

        "session_context",
        # What the player was doing at the end of the last session.
        # Very short decay — stale session context is confusing.
        # e.g. "Logged off in the middle of the forest dungeon, floor 3"
        # e.g. "Was in the middle of a trading quest with NPC Aldric"

        "behavioral_pattern",
        # Observed patterns in how the player plays.
        # Used to personalize hints, difficulty, and companion commentary.
        # e.g. "Player consistently runs out of potions before boss fights"
        # e.g. "Player rarely uses the crafting system despite having materials"

        "social",
        # Multiplayer, guild, and in-game relationship context.
        # e.g. "Regular squad members: Kira, DevNull, Phantom_X"
        # e.g. "Player is guild leader of Ironclad. Guild focuses on PvE."

        "loadout",
        # Current character build, equipment, and ability choices.
        # Medium decay — loadouts change with patches and playthroughs.
        # e.g. "Using dual-wield rogue build with poison specialization"
        # e.g. "Main weapon: Shadowfang +3. Has not enchanted secondary."
    ],
    decay_windows={
        # Highly perishable session context
        "session_context":    3,    # next session starts fresh from where they left off

        # Behavioral patterns form over time
        "behavioral_pattern": 30,

        # Loadouts change with patches and progression
        "loadout":            90,

        # Social context shifts
        "social":            180,

        # Playstyle preferences are stable
        "playstyle":         365,

        # Progression is permanent — never expire
        "progression":      3650,
    },
)
