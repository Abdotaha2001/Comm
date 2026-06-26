# PART 04 — PLAYER RE-IDENTIFICATION & IDENTITY

> Read `00_INDEX.md` first. Today identity is "Player 1 / Player 2" per video — no persistent named players.

## Purpose
Maintain a player's identity **across an entire tournament and across years**, beyond clothing. Build a real player database and a portable identity.

## Required signals
Face recognition · Body embeddings · **Skeleton embeddings** · Jersey/number recognition · **Playing-style signature** · **Movement signature** · Multi-view ReID.

## Missing components

| # | Component | Priority | Complexity | Tier | Notes |
|---|-----------|----------|-----------|------|-------|
| 4.1 | **Player database** (real named athletes, not P1/P2) | 🔴 | M | all | Foundation for everything longitudinal |
| 4.2 | Face recognition + profile auto-link | 🟠 | L | T1 | 30-player squads |
| 4.3 | Body/appearance embeddings (beyond histogram) | 🟠 | L | T1 | Today OSNet + histogram fallback |
| 4.4 | **Skeleton/gait embeddings** | 🟠 | L | T1 | Robust to clothing |
| 4.5 | Jersey/number recognition | 🟡 | M | T1 | Team events |
| 4.6 | **Playing-style signature** as a biometric (shot mix, tempo) | 🟠 | L | T2 | Style ≈ fingerprint |
| 4.7 | **Movement signature** (footwork rhythm) | 🟡 | L | T2 | Complements style |
| 4.8 | Multi-view ReID consistency | 🟠 | L | T3 | Links Part 02 |
| 4.9 | **Handedness detection (left/right)** | 🔴 | M | T1 | Baseline FH/BH logic silently assumes a hand → flips for lefties |
| 4.10 | **Grip detection** (shakehand / penhold / Chinese penhold) | 🔴 | L | T1 | Changes interpretation of every stroke |
| 4.11 | Reverse-penhold-backhand (RPB) detection | 🟠 | L | T1 | Modern world-class technique |
| 4.12 | Cold-start handling (new player, no history) | 🟠 | M | all | Few-shot profile bootstrap |
| 4.13 | **Global Player Passport** (cross-federation portable ID) | 🟠 | L | all | Player moves club/country; one career record |
| 4.14 | Career timeline / auto-built athlete biography | 🟡 | M | all | Longitudinal narrative |
| 4.15 | Identity reliability score + human-confirm workflow | 🟠 | M | all | Feeds Part 10 |

## Datasets / models
- Labeled multi-match ReID set (same player across venues/outfits).
- Face set with consent governance (Part 15).
- Handedness/grip labeled clips.

---

➡️ **NEXT FILE: `05_STROKE_SPIN_FOOTWORK.md`**
