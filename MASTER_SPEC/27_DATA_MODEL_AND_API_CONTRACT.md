# PART 27 — DATA MODEL & API CONTRACT (build artifact, realizes build #3)

> Read `00_INDEX.md` first. This is the **bridge from spec to code** — the concrete schema and API the platform is built on. Machine-readable companions live in `schema/schema.sql` (Postgres DDL) and `api/openapi.yaml` (OpenAPI 3.1). Enums are grounded in Parts 19 (skills), 20 (equipment), 24 (para), 19-B8 (styles).

## 0. Cross-cutting conventions
- **IDs:** UUID. **Times:** `timestamptz`. **Money/precision:** `numeric`. Flexible/nested data: `jsonb`.
- **Multi-tenancy:** every business row carries `org_id`; all queries are org-scoped (Part 13).
- **Reliability envelope** — any *measured* value is returned as:
```json
{ "value": 78.0, "confidence": 0.86, "ci": [72, 84], "tier": "t1", "source": "M14:speed@1.2", "status": "ok" }
```
`status:"abstain"` means "I don't know" (below threshold) → no value asserted (Part 10).

## 1. Entities (ER overview)
```
organizations ─┬─< users
               └─< players ─┬─< player_equipment
                            ├─< videos ─< analysis_runs ─< matches ─┬─< rallies ─< shots
                            │                                       │            └─< events
                            ├─< player_profiles (versioned)         └─ (player1_id, player2_id → players)
                            ├─< opponent_dossiers
                            └─< matchups ─< game_plans ─< plan_outcomes
```

### Key tables (fields abbreviated; full DDL in `schema/schema.sql`)
| Table | Purpose | Notable fields |
|-------|---------|----------------|
| `organizations` | tenant | `type` ∈ federation/club/academy/individual |
| `users` | accounts + RBAC | `role` ∈ admin/coach/player/umpire/medical/scout |
| `players` | pro & junior & para | `type`, `handedness`, `grip`, `para_class` (1–11), `impairment_type`, `mobility_mode`, `maturation_status` |
| `player_equipment` | versioned kit | `blade`, `fh_rubber_type`, `fh_sponge_mm`, `bh_rubber_type`, `bh_sponge_mm` |
| `videos` | source media | `status`, `capture_tier` (t1/t2/t3), `fps`, `storage_key` |
| `analysis_runs` | a processing job | `status`, `reliability_index`, `input_quality`, `model_versions` |
| `matches` | analyzed match | `player1_id`, `player2_id`, `score`, `format`, `is_doubles` |
| `rallies` | points | `server_player_id`, `winner_player_id`, `reason`, `quality`, `confidence` |
| `shots` | strokes | `stroke_type`, `spin_type`, `wing`, `speed_kmh`, `confidence`, `provenance` |
| `events` | bounce/net/hit/serve/point/let/violation | `type`, `frame`, `position`, `confidence` |
| `player_profiles` | aggregated, versioned | `style_class`, `aggregated_stats`, `strengths`, `weaknesses`, `confidence` |
| `opponent_dossiers` | scouting target | `opponent_player_id?`, `opponent_ref`, `footage_count`, `confidence` |
| `matchups` | my_player × opponent | `predicted_winprob`, `h2h`, `confidence` |
| `game_plans` | "how to beat them" | `plan`, `training_block`, `report_key`, `status`, `confidence` |
| `plan_outcomes` | did it work? | `actual_result`, `adherence`, `effectiveness` |

## 2. Controlled enums (grounded in the domain)
- **stroke_type:** `serve_pendulum, serve_reverse_pendulum, serve_tomahawk, serve_reverse_tomahawk, serve_shovel, serve_backhand, serve_high_toss, serve_ghost, push_short, push_long, flick, banana_flick, strawberry_flick, drop_shot, drive, loop, hook_loop, fade_loop, counterloop, smash, block, punch_block, chop_block, chop, fish, lob, dig` (Part 19).
- **spin_type:** `topspin, backspin, sidespin_left, sidespin_right, corkspin, mixed, no_spin`.
- **wing:** `fh, bh`.
- **style_class:** `fh_looper, two_winged_attacker, counter_driver, all_rounder, chopper, penhold_looper, penhold_rpb, short_pips_hitter, combination_chopper` (Part 19-B8).
- **rubber_type:** `inverted, short_pips, medium_pips, long_pips, anti` (Part 20).
- **grip:** `shakehand, penhold_chinese, penhold_japanese, seemiller, other, unknown`.
- **handedness:** `left, right, unknown`.
- **para impairment_type:** `impaired_muscle_power, impaired_passive_rom, limb_deficiency, leg_length_difference, short_stature, hypertonia, ataxia, athetosis, intellectual` (Part 24).
- **mobility_mode:** `standing, wheelchair, na`. · **capture_tier:** `t1, t2, t3`.
- **event.type:** `bounce, net, hit, serve, point, let, violation`.

## 3. Core API flows (REST `/v1`, Bearer auth, org-scoped)
| Flow | Endpoint |
|------|----------|
| Create player (pro/junior/para) | `POST /v1/players` |
| Get / update player (assign disability/equipment) | `GET` / `PATCH /v1/players/{id}` |
| Register a player's video | `POST /v1/players/{id}/videos` |
| Run analysis | `POST /v1/videos/{id}/analyze` → `analysis_run` |
| Poll run status + reliability | `GET /v1/analysis-runs/{id}` |
| Get full match results | `GET /v1/matches/{id}` |
| Get / rebuild aggregated profile | `GET` / `POST /v1/players/{id}/profile[:rebuild]` |
| Create opponent dossier (ref or videos) | `POST /v1/opponents` |
| Create matchup | `POST /v1/matchups` |
| **Generate game plan** | `POST /v1/matchups/{id}/game-plan` |
| Get game plan | `GET /v1/game-plans/{id}` |
| Record plan outcome | `POST /v1/game-plans/{id}/outcome` |
| Webhook | `analysis.completed`, `gameplan.ready` |

### Example — generate game plan (response, abbreviated)
```json
{
  "id": "…", "matchup_id": "…", "status": "draft",
  "predicted_winprob": { "value": 0.58, "confidence": 0.41, "tier": "t1", "source": "M35", "status": "ok" },
  "plan": {
    "exploit": [{ "text": "Opponent loses long rallies vs no-spin to the middle",
                  "evidence": "7/9 across 2 matches", "confidence": 0.62 }],
    "serve": ["Long backspin to the long-pips BH, then 3rd-ball loop to FH"],
    "receive": ["Banana-flick the short FH serve"],
    "placement": ["Target the crossover/elbow"]
  },
  "training_block": [{ "drill": "BH push→loop, random spin (multiball)", "targets": "vs backspin BH" }],
  "confidence": 0.45,
  "data_note": "Preliminary — only 2 opponent videos. Add footage to raise confidence."
}
```
> Every plan item is **evidence-cited + confidence-tagged**; thin data → `status:"abstain"`/`"preliminary"` instead of a confident guess (Parts 10, 17).

## 4. Notes for implementation
- Results (`rallies/shots/events`) are written by the **GPU worker** after an `analysis_run`; the API is read-mostly for them.
- `analysis_runs.model_versions` records exactly which models produced the run → reproducibility (Part 13.4) + provenance (Part 10).
- Profiles are **append-only versioned** (never overwrite) → longitudinal history (Part 04/17).
- Para players: `mobility_mode='wheelchair'` switches movement scoring & service-legality rules (Parts 24, 09).

## 5. Hardening added in v0.1 (after review)
- **Auth:** `users.password_hash/status/last_login_at` + `api_keys` table; `POST /v1/auth/login`, `GET /v1/auth/me`.
- **Consent & privacy (minors/para/GDPR):** `consents` table + `POST /v1/players/{id}/consents` (guardian consent flag).
- **Doubles:** `matches.player3_id/player4_id` + `Match.player3_id/player4_id`.
- **Generated outputs:** `artifacts` table (video/chart/clip/report/results_json) surfaced on `Match.artifacts`.
- **Coaching storage:** `drills` catalog + `training_plans` (periodized; Parts 08, 22).
- **Audit & lifecycle:** `players.status/archived_at/created_by` + auto `updated_at` trigger.
- **API hygiene:** `GET /v1/healthz`, `Idempotency-Key` on plan generation, `401/422/429` responses, `WebhookEvent` schema.
- **Deferred (post-P1):** Postgres RLS policies, tournaments/teams, refresh-token rotation.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
