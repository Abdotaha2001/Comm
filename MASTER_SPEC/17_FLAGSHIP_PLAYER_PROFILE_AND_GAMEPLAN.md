# PART 17 — ⭐ FLAGSHIP FEATURE: PLAYER PROFILES & "HOW TO BEAT YOUR OPPONENT" GAME PLAN

> Read `00_INDEX.md` first. This is the platform's flagship, user-facing product loop. It composes the engines in Parts 04, 07, 08, 10, 11 into one workflow a coach actually uses.

## One-line definition
For **every player you own** (professional or junior): keep a persistent profile, feed it that player's videos to build/refresh it over time, then **send an opponent** (name or videos) and the platform produces a personalized, opponent-specific **game plan for how this player beats that specific opponent** — plus a short training block to rehearse it.

```
  My Player Profile  ──┐
   (built from his      │
    own videos, kept    ├──►  MATCHUP ENGINE  ──►  "HOW TO BEAT THEM" GAME PLAN
    & updated)          │      (style × style,        + opponent-specific training block
  Opponent Dossier  ───┘       H2H, weaknesses)        + pre-match report + live adjustments
   (sent by coach:
    name or videos)
```

## User journey
1. Coach creates a **player profile** (pro or junior) → uploads one or more of that player's match videos.
2. Platform analyzes each video and **aggregates** into a persistent, longitudinal profile (style, strengths, weaknesses, serve/receive tendencies, patterns, footwork, physical trends).
3. Before a match, coach **sends the opponent**: either an existing player in the system, a name to look up, or raw opponent videos.
4. Platform builds an **opponent dossier** (even from sparse footage) and runs the **matchup engine**.
5. Output: **a game plan to beat that opponent**, a **training block** to prepare, a **pre-match report** (coach + simplified player version), and **between-games live adjustments** during the match.

## Game-plan contents (the deliverable)
- **Exploit map:** opponent's weaknesses × my player's strengths that attack them.
- **Serve strategy vs this opponent** (which serves to which weak returns).
- **Receive strategy vs their serves** (how to neutralize their best serves).
- **Rally tactics:** which wing to target, preferred rally length to impose, patterns to use / avoid.
- **Score-situation tactics:** what to do at pressure points (deuce, game points).
- **Predicted matchup + win probability** with an explicit confidence (Part 10).
- **Rehearsal training block:** drills that practice exactly this plan (Part 08).
- **Sparring recommendation:** which squad member plays most like the opponent, to spar against.

## Missing components (specific to this feature)

| # | Component | Priority | Complexity | Depends on |
|---|-----------|----------|-----------|-----------|
| 17.1 | **Player profile entity** (pro/junior) + lifecycle (create/edit/archive) | 🔴 | M | Part 04, 13 |
| 17.2 | **Multi-video ingestion per player** (upload, dedup, queue) | 🔴 | M | Part 13 |
| 17.3 | **Profile aggregation** across a player's videos (persistent, longitudinal) | 🔴 | L | Part 04, 07 |
| 17.4 | **Opponent dossier builder** (from name lookup OR sent videos) | 🔴 | L | Part 07 |
| 17.5 | **Sparse-footage handling** (few-shot opponent, 1 video or less) + confidence | 🔴 | L | Part 10, 12 |
| 17.6 | **Head-to-head history** (if they played before) | 🟠 | M | Part 04 |
| 17.7 | **Style-vs-style matchup model** (e.g. chopper vs looper priors) | 🔴 | L | Part 07 |
| 17.8 | **Game-plan generator** (grounded in knowledge graph + expert system) | 🔴 | L | Part 11 |
| 17.9 | **Opponent-specific training block** (rehearse the plan) | 🟠 | M | Part 08 |
| 17.10 | **Pre-match report** (coach version + simplified player version, PDF) | 🟠 | M | Part 13 |
| 17.11 | **Win-probability for the specific matchup** + confidence interval | 🟠 | M | Part 07, 10 |
| 17.12 | **"What-if" plan simulator** (test the plan vs opponent model) | 🟡 | XL | Part 07 |
| 17.13 | **Sparring-partner recommender** (squad member who mimics opponent) | 🟡 | M | Part 04, 07 |
| 17.14 | **Between-games live adjustments** (in-match, coaching allowed between games) | 🟠 | L | Part 07, 14 |
| 17.15 | **Plan-vs-outcome tracking** (did the plan work? feed back) | 🟠 | M | Part 16 |
| 17.16 | Coach UI: profile dashboard + "Prepare for opponent" flow | 🔴 | L | Part 13 |

## New database tables (extends Part 13)
- `players` (id, name, type=pro|junior, handedness, grip, org_id, …)
- `player_videos` (id, player_id, source, status, processed_at)
- `player_profiles` (player_id, aggregated_stats, style_signature, updated_at) — versioned
- `opponent_dossiers` (id, subject_player_id, opponent_ref, footage_count, confidence)
- `matchups` (id, my_player_id, opponent_id, h2h, predicted_winprob, confidence)
- `game_plans` (id, matchup_id, plan_json, training_block_id, report_path, created_at)
- `plan_outcomes` (game_plan_id, actual_result, adherence, effectiveness)

## Reliability requirements (Part 10 applies hard here)
- The game plan **must** carry a confidence driven by how much opponent footage exists. One clip → label the plan **LOW confidence / preliminary**.
- Every recommendation cites its **evidence** ("opponent lost 7/9 long rallies across 2 matches").
- If data is too thin, the system **says so** and asks for more opponent footage instead of bluffing a plan.

## Datasets / models
- Style-taxonomy labels (chopper / looper / blocker / all-round / penhold-attacker …).
- Matchup-outcome corpus (style A vs style B → who tends to win, and why).
- The opponent-simulation model from Part 07 powers the what-if simulator.

---

➡️ **NEXT FILE: `18_MODEL_CATALOG_EVERYTHING_IS_AI.md`**
