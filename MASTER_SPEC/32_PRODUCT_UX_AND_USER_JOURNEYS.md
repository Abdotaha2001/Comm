# PART 32 — PRODUCT, UX & USER JOURNEYS

> Read `00_INDEX.md` first. Turns the engines into something a coach actually uses. Defines personas, the journeys they walk, the screen map, and the UX principles (honest reliability + bilingual RTL). Powers the frontend (Part 13D/14); driven by the API (Part 27).

## A. Personas
| Persona | Goal | Key tasks |
|---------|------|-----------|
| **Coach** | win matches, develop players | upload video, read analysis, prep vs opponent, assign training |
| **Player (pro/junior)** | improve | see my profile/progress, watch my clips, do drills |
| **Umpire** | correct calls | officiating assist, review evidence package |
| **Sports scientist / medical** | health & load | injury risk, asymmetry, fatigue, return-to-play |
| **Scout** | find/prepare for opponents | opponent dossiers, multi-match trends |
| **Federation / academy admin** | run teams & events | manage roster/coaches, tournaments, rankings |

## B. Core journeys

### J1 — Coach: "prepare my player to beat an opponent" (the flagship)
1. Create player (pro/junior; or para — set class) → **upload videos**.
2. Open **Analysis** → review rallies/shots/events with **confidence on every number**.
3. **Rebuild profile** → see style, strengths, weaknesses.
4. **Prepare for opponent** → pick opponent (in-system or upload footage) → dossier.
5. **Generate game plan** → serve/receive/placement/exploit + win-probability + **"preliminary" badge if data is thin**.
6. **Assign training block** → lands in the player's calendar.
7. After the match → **record outcome** → did the plan work? (efficacy loop).

### J2 — Player (mobile): self-record → see progress → do drills → track streaks.
### J3 — Umpire (live): assist flags suspect calls → open **evidence package** (frames + 3D + confidence) → confirm/override (logged).
### J4 — Admin: manage roster/coaches/teams → schedule camps → run tournament brackets → rankings.

## C. Screen map (information architecture)
```
Dashboard
├─ Players ── Player profile (style/strengths/weaknesses, longitudinal)
│             └─ Videos ── Analysis viewer (timeline + clips + confidence)
├─ Prepare for opponent ── Dossier → Matchup → Game plan (+ PDF)
├─ Training ── Plan / calendar / drill library
├─ Reports ── match / player / scouting (export PDF)
└─ Admin ── org, users/roles, teams, tournaments, consent, billing
```

## D. UX principles
- **Honest reliability, always:** every metric shows a **confidence chip**; low → muted + "preliminary"; **abstain → "not sure, needs review"** (never a fake number).
- **Evidence on tap:** click any claim → the frames/stats behind it (Part 10 provenance).
- **Bilingual + RTL:** EN/AR from the glossary (Part 28); Arabic is true right-to-left.
- **Accessible:** colour-blind-safe charts, keyboard nav, screen-reader labels.
- **Right device:** coach = desktop dashboard; player = mobile; umpire = courtside tablet.

## E. Signature components
- **Interactive video timeline** — jump to any point/shot/bounce; per-event markers.
- **Confidence chip** + **evidence drill-down**.
- **Game-plan card** — exploit / serve / receive / placement, each evidence-cited.
- **Telestration** (draw on video) + **side-by-side compare** (vs model / vs past self).
- **Reliability banner** per analysis run (input quality + match reliability index).

## F. States & notifications
- **Empty/low-data:** clear "add more footage to raise confidence" prompts.
- **Async:** "analysis processing…" → push/notify on done; "game plan ready" (webhooks, Part 27).
- **Errors:** friendly failure with retry; never a blank screen.

## G. Screen → API map (Part 27)
| Screen | Endpoints |
|--------|-----------|
| Player profile | `GET /players/{id}`, `GET/POST /players/{id}/profile[/rebuild]` |
| Analysis viewer | `GET /matches/{id}`, `GET /analysis-runs/{id}` |
| Upload | `POST /players/{id}/videos`, `POST /videos/{id}/analyze` |
| Opponent prep | `POST /opponents`, `POST /matchups`, `POST /matchups/{id}/game-plan` |
| Training | `GET/POST /players/{id}/training-plans`, `GET /drills` |
| Auth/admin | `/auth/*`, players CRUD, webhooks |

---

➡️ **NEXT FILE: `33_COMPETITIVE_LANDSCAPE.md`**
