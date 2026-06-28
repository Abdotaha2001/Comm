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

## H. Onboarding & first-run
Org/team setup → add first player → **capture consent** (minor → guardian flow, Part 31) → **capture-setup guide** (Part 35) → upload first video → guided tour of the flagship loop. Every empty section nudges the next action ("add a video", "prepare for an opponent").

## I. Role-aware UI (RBAC reflected)
Each role sees a tailored home and only what it may touch (server-enforced, Part 31): **medical/injury data is hidden from coaches**; players are read-only on rosters; umpires get the officiating console. Sensitive items are **hidden, not just disabled**.

## J. Reliability design system (the visual language)
- Confidence rendered as a **band** (green = high · amber = moderate · grey = low/preliminary) **+ the interval** ("78 ± 6 km/h"); **never a bare number**.
- `abstain` → an explicit **"not sure — needs review"** state, not a fake value.
- Every claim has a consistent **evidence drill-down** affordance (tap → the frames/stats behind it).

## K. Loading / empty / error states
- **Skeleton loaders**; analysis **streams partial results** as it processes (Part 13.6).
- **Input-quality warning** before processing poor footage ("low light / heavy occlusion — results limited").
- Failed run → friendly message + **retry**; never a blank screen.

## L. Accessibility & localization UX
- **WCAG 2.1 AA:** keyboard nav, contrast ratios, alt text, **video captions**, focus order.
- **Localization:** true **RTL mirroring** for Arabic; localized units/date formats and **name order**; in-app **language switcher** (strings from the glossary, Part 28).

## M. Reports, export & collaboration
- **PDF reports** (coach version + simplified player version); shareable expiring links.
- **Share the game plan with the player**; comments/notes on clips; multiple coaches per team.

## N. Courtside, progress & juniors
- **Between-games tablet view** courtside (live coaching window, Part 14).
- **Longitudinal progress** + LTAD stage & trainability windows (Part 23).
- **Junior gamification:** badges, streaks, milestones (Part 14).

## O. Para & explainability UX
- **Wheelchair-aware views** (no able-bodied footwork; class context, Part 24); the product is usable **by** disabled coaches/players too (accessibility).
- **"Why this plan?"** — expandable rationale + evidence + a link to the model card (trust, Part 10/11).

## P. Offline & responsive
- **Low-connectivity capture + later sync** for academies; **mobile-first** for players, **desktop** for coaches; courtside **tablet**.

## Q. Flagship wireframes (text sketch)
```
[ANALYSIS VIEWER]                         [GAME PLAN — vs Opponent]
 ┌── video ───────────┬─ rally list ─┐    Win prob: 58% (amber, low conf) ⓘ
 │  ▶ telestration    │ #1 ✔ 0:12    │    ▸ Exploit: FH over-reliance (82%) ⓘ
 │  �= timeline ▮▮|▮   │ #2 ✗ 0:09    │    ▸ Serve: long backspin to pips ⓘ
 └────────────────────┴──────────────┘    ▸ Receive / Rally / Placement …
  Confidence band per metric + evidence   [Assign training block] [Export PDF]
```

## R. Design system, branding & white-label
A shared component library + **design tokens** (color/spacing/type) for consistency across web/mobile/tablet; **per-federation white-label** theming (logo/colors); dark mode.

## S. Navigation & findability
**Global search** (players/matches/opponents), filters & saved views, **command palette** for power users, breadcrumbs, recent items, quick actions.

## T. Notifications system
Channels: in-app · email · push (· SMS opt-in). Per-user **preferences** + **do-not-disturb** + digests. Triggers: analysis done, game plan ready, plan-vs-outcome due, security events. Templated + localized.

## U. Settings & preferences
Units, **language**, theme, notification prefs, account/security (sessions, MFA), org settings (admins). Player: consent & privacy controls (see Z).

## V. Data visualization
Chart catalog: shot distribution, **placement heatmaps** (6/9-zone), momentum/timeline, **radar** comparison, serve→receive matrix, win-probability. **Colour-blind-safe palettes**, interactive tooltips, every chart shows its **confidence/sample size**.

## W. Video tooling & comparison
Playback speed, **frame-step**, loop, zoom, **clip-and-share**, multi-angle switch (T3), keyboard shortcuts. **Side-by-side compare** (vs model · vs past self · vs opponent) with synced playback.

## X. Coach efficiency
**Reusable templates** (game-plan & training-block templates), bulk actions, keyboard-driven workflows, duplicate-from-last.

## Y. Calendar, roster & competition UX
Training **calendar** + session reminders (Part 15 logistics); **roster/team** management (assign players, coaches, medical); **tournament** brackets/schedules/results (Part 15).

## Z. Player self-service & privacy controls
The player can: view their profile/progress, **manage consent**, **download their data** and request deletion (DSAR UX, Part 31), edit basic profile — age-appropriate for juniors.

## AA. Help, feedback, microcopy & tone
In-app help/tutorials, **what's-new** changelog, feedback capture. **Tone:** weaknesses framed **constructively** (improvement-oriented), junior-friendly language, never shaming.

## AB. Safety & confirmation
Destructive actions (archive/delete) require **confirmation + undo**; clear **session-timeout / re-auth** flow without losing work.

## AC. Product success metrics (is the UX working?)
Track **activation** (first analysis + first game plan), **retention**, feature adoption, **time-to-first-insight**, and game-plan→outcome usage — to validate the product loop (ties Part 16 efficacy).

---

➡️ **NEXT FILE: `33_COMPETITIVE_LANDSCAPE.md`**
