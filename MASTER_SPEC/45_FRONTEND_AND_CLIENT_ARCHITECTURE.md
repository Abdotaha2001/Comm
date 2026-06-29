# PART 45 — FRONTEND & CLIENT ARCHITECTURE (Authoritative Build Specification)

> Read `00_INDEX.md` first. This is the **authoritative experience law** of the platform — the **ninth build pillar** after the data model (37), ontology (38), event contract (39), reliability law (40), security law (41), operability law (42), intelligence law (43), and delivery law (44). Those eight are the **backend/platform** foundation; this part is the **human-facing client** that turns governed truth into something a coach, athlete, umpire, or federation actually uses.
>
> Its distinctive job: the client is the **last mile of honesty**. The reliability law (Part 40) is wasted if the UI renders a `preliminary`, abstained, or T1-capped value as a confident headline number. This part makes **"I don't know"** and **calibrated confidence** first-class UI states (§E) — the client never launders uncertainty into false certainty.
>
> **If implementation conflicts with this document, this document wins** — except where marked `SPECIFIED`. It **formalizes Part 32 (Product UX & User Journeys) + Part 14 (apps/engagement) for build**, and **consumes** Part 37 (API), 38 (i18n vocabulary), 40 (reliability envelope), 41 (client security), 42 (RUM), 44 (client delivery). RFC-2119 keywords are normative.
>
> **Status legend:** ✅ `IMPLEMENTED` · 🟡 `PARTIAL` · ⬜ `SPECIFIED`. Honesty rule (Part 41 §B.5): **no client exists in the repo today** — the frontend is **greenfield** (§T). What exists are the **contracts** a client must honor: the OpenAPI spec (✅ `api/openapi.yaml`), the i18n vocabulary (✅ `i18n/glossary.json`→`en/ar`), and the reliability-envelope schema (Part 40). This spec is the contract for when the client is built — so it is honest from line one.

---

## A. Scope & Objectives

### A.1 Purpose
Define a client architecture that is **honest, accessible, bilingual, fast, offline-capable, and secure** — a faithful, calibrated **view** of governed backend truth, never a second source of truth.

### A.2 Goals
- **G1.** The UI renders the **reliability envelope** faithfully (§E): no bare numbers, abstention shown, tier + confidence visible.
- **G2.** Every surface is **accessible** (WCAG, §G) and **bilingual EN↔AR with RTL** (§H) by default — not retrofitted.
- **G3.** The client is a **view**: the **server is the authority** (§B.2); the client never enforces security or invents data (§N/§O).
- **G4.** Performance is **budgeted + gated** (§I); the client is usable on modest devices + networks (§J offline).
- **G5.** A **design system** (§F) makes accessibility, i18n, and reliability-honesty the **default** of every component.
- **G6.** The client is **secure** (§O), **observable** (§P, RUM), **tested** (§Q), and **delivered** through Part 44 (§R).
- **G7.** Client invariants are **CI-enforced** (§S): no hardcoded strings, a11y gate, bundle budget, reliability-render, API-client-in-sync.

### A.3 Non-goals
- Not the UX research/journeys (Part 32) — it **builds** them.
- Not the API/event contracts (Part 37/39) — it **consumes** them via a generated client.
- Not backend security/reliability — it **honors** Part 40/41 at the edge; the server still enforces (§B.2).

### A.4 Relationship to Parts
Formalizes Part 32 (UX/journeys) + Part 14 (apps/media); consumes Part 37 (OpenAPI → generated client), Part 38 (`glossary.json` → all display strings), Part 40 (envelope → §E rendering), Part 39 (events → real-time §K), Part 35 (capture UX §M); complies with Part 41 (client security §O, a11y §AR.4, consent §H); emits Part 42 telemetry (RUM §P); ships via Part 44 (§R).

---

## B. Principles

- **B.1 The client is a view, not the truth.** State of record lives in the backend (Part 37); the client **renders + caches** it, and reconciles on conflict (§D) — it never becomes a divergent source.
- **B.2 The server is the authority.** The client **MUST NOT** be the security or business-rule boundary: RBAC, validation, and pricing are **re-enforced server-side** (Part 41 §B.1); a role-aware UI (§N) is convenience, never enforcement.
- **B.3 Honesty at the edge.** The UI **MUST** show confidence, abstention, and tier (§E); rendering a low-reliability value as a confident fact is a **defect**, not a design choice (Part 40 §B.1).
- **B.4 Accessible + bilingual by default.** a11y (§G) + EN/AR RTL (§H) are built into the design system (§F), not bolted on per screen.
- **B.5 Offline-tolerant.** The client degrades gracefully on poor/no network (§J) — courtside venues are not data centers (Part 02).
- **B.6 Performance is a feature.** A budgeted, fast UI (§I) is a usability + accessibility + reach requirement, not a nicety.
- **B.7 Trust nothing client-side.** No secrets, keys, or unvalidated trust in the client (§O); treat the client as a hostile, inspectable environment.
- **B.8 One design system.** Consistency + quality come from a shared, documented component library (§F) — not per-team reinvention.

---

## C. Client Surfaces & Topology

- **C.1 Surfaces.** Web app (coach/federation dashboard), mobile (athlete/coach on-court), desktop, **courtside/edge** capture client (Part 02), and **broadcast/overlay** + public **API/SDK** consumers (Part 14). Each persona (Part 32) maps to a primary surface.
- **C.2 Shared core, thin surfaces.** Business/view logic + the design system (§F) + the generated API client (§D) are **shared** (e.g. a shared TS core); per-surface code is the thin presentation shell — avoid divergent reimplementations.
- **C.3 Progressive capability.** A surface declares what it supports (offline §J, real-time §K, capture §M); it **degrades** features it can't support rather than breaking (§B.5).
- **C.4 Public SDK.** External API consumers get a **versioned, generated SDK** (from OpenAPI §D, Part 37) — not hand-rolled HTTP.

## D. Architecture & State Management

- **D.1 Generated API client.** The HTTP client is **generated from `api/openapi.yaml`** (✅ contract exists) so the client + server never drift (§S `api-client-in-sync`); hand-written endpoint calls are forbidden.
- **D.2 Server-state vs client-state.** Separate **server cache state** (fetched, cacheable, invalidated — e.g. TanStack-Query-style) from **local UI state** (form/toggle); don't dump server data into a global store.
- **D.3 First-class async states.** Every data view handles **loading / empty / error / and `abstain`** (§E) explicitly — a blank or fabricated value on missing/abstained data is a defect.
- **D.4 Optimistic + reconciled.** Optimistic updates **MUST** reconcile against the server response (§B.1); on conflict, server wins + the user is informed (§J.4).
- **D.5 Typed end-to-end.** Types flow from the schema/OpenAPI (Part 37) into the client (generated types) — the reliability envelope is a **typed shape**, not an ad-hoc object.

## E. The Reliability-Honest UI (the distinctive pillar)

The client is where Part 40 either lives or dies. Every measured value arrives as an **envelope** `{value, confidence, ci, tier, status, source}` and **MUST** be rendered as such.

- **E.1 No bare numbers.** A value **MUST** be shown with its **status + confidence** (and `ci`/unit for continuous values); "78 km/h" alone is forbidden — show "78 ± 6 km/h · preliminary · T1" (Part 40 §R, §BA precision-matches-uncertainty).
- **E.2 Abstention is first-class.** `status = abstain` renders an explicit **"Not enough signal to tell"** state (with the reason — occlusion / thin data / tier / OOD, Part 40 §F/§AR), **never** a 0, a blank, or a guessed value.
- **E.3 Calibrated language.** Copy matches the status band (Part 40 §E): `verified` → assertive; `preliminary`/`moderate` → hedged ("looks like", "preliminary"); `unreliable` → flagged. The i18n strings (§H) carry the calibrated phrasing in both languages.
- **E.4 Tier + provenance visible.** A **capture-tier badge** (T1/T2/T3) and a path to **provenance/evidence** (the drill-down, Part 32.D / Part 40 §J) are available on any measured value — the user can always ask "how do you know?".
- **E.5 Uncertainty in viz.** Charts (§L) show **confidence bands / error bars**, not just point lines; a trend within overlapping CIs is **not** drawn as a definitive change (Part 43 §S.1).
- **E.6 Officiating restraint.** A decisive/officiating value (Part 09/41 §L) shows as **advisory** until validated, with its evidence + the human-override path (Part 41 §AC) — the UI never presents an unvalidated call as final.
- **E.7 Honesty over polish.** When forced to choose, the UI prefers an honest "preliminary/abstain" over a confident-looking but unwarranted number (§B.3, Part 40 §B.1).

## F. Design System & Component Library

- **F.1 Tokens + theming.** Design tokens (color/space/type/motion) drive theming, dark mode, and contrast (§G); no hardcoded styles.
- **F.2 Accessible + i18n + reliability-aware components.** Every shared component bakes in a11y (§G), RTL/i18n (§H), and the reliability-render contract (§E) — e.g. a `<Metric envelope=… />` component that **cannot** render a bare number.
- **F.3 Documented.** The library is documented + visually catalogued (Storybook-style) with usage + a11y notes; teams compose, not reinvent (§B.8).
- **F.4 Consistency = quality + trust.** A consistent system reduces error, speeds delivery, and makes the product feel as reliable as its data.

## G. Accessibility (a11y)

- **G.1 WCAG.** Target **WCAG 2.2 AA** (AAA where feasible) across surfaces; a11y is a **release gate** (§S), not a backlog item.
- **G.2 Mechanics.** Full keyboard operability, correct semantics/ARIA, visible focus, screen-reader labels, **contrast** from tokens (§F.1), **reduced-motion** honored, target sizes.
- **G.3 Para-athletes + inclusion.** Usable with assistive tech for **para-athletes** (Part 24) and diverse users (Part 41 §AR.4) — the platform serves them, so its UI must not exclude them.
- **G.4 Media a11y.** Video has captions/transcripts; data viz (§L) has non-color encodings + text/table alternatives.

## H. Internationalization & Localization

- **H.1 No hardcoded display strings.** All UI text comes from the **controlled vocabulary** (✅ `i18n/glossary.json` → `en.json`/`ar.json`, Part 38); a literal string in a component is a defect (§S `no-hardcoded-strings`).
- **H.2 EN ↔ AR + RTL.** Both languages are **first-class**; the layout **mirrors for RTL** (logical properties, not left/right), and bidi text is handled correctly — Arabic is not an afterthought (the project is bilingual at its core).
- **H.3 Locale formatting.** Numbers, dates, **units** (km/h, RPM), and pluralization are locale-formatted; precision matches the value's uncertainty (§E.1, Part 40 §BA).
- **H.4 Canonical terms.** Domain terms render from their `canonical_id` (Part 38) so "loop"/"topspin"/"banana flick" are consistent + translatable everywhere.

## I. Performance

- **I.1 Web Vitals budgets.** Target **Core Web Vitals** (LCP, **INP**, CLS) with explicit budgets; a regression **fails the gate** (§S, ties Part 42 §L perf-regression).
- **I.2 Bundle discipline.** Code-splitting, lazy-loading, tree-shaking, and a **bundle-size budget** per route; ship less JS (§B.6).
- **I.3 Media optimization.** Video/image are adaptively sized + lazy + streamed (§K); the heavy CV artifacts are server-side — the client renders results, not raw compute.
- **I.4 Perceived performance.** Skeletons + optimistic UI (§D.4) + instant feedback; the UI feels fast even when the analysis is slow (async, Part 42 §E latency SLOs).

## J. Offline, Sync & Edge

- **J.1 Offline-tolerant.** Critical read flows work offline (cached, PWA/service-worker or native store); the client shows **stale-but-labeled** data, never a hard failure (§B.5).
- **J.2 Store-and-forward.** Captures/edits made offline are **queued + synced on reconnect** (Part 42 §X store-and-forward); courtside venues with poor links still work (Part 02).
- **J.3 Edge-private aware.** In edge-private mode (Part 41 §H.7 / Part 42 §X), the client respects that **video stays local** — it shows results without assuming cloud round-trips.
- **J.4 Conflict resolution.** On sync conflict, the **server is authoritative** (§B.1); the user sees what changed + can resolve — no silent overwrite or lost work.

## K. Real-Time & Streaming

- **K.1 Live events.** Live match/analysis views subscribe to backend events (Part 39) over **WebSocket/SSE**; reconnection + backfill on drop are handled (no missed events).
- **K.2 Video sync.** Playback is **frame-accurate** and synced to events (bounce/shot/score markers, Part 03/09); scrubbing maps to frames/timestamps (Part 40 §D).
- **K.3 Live reliability.** Real-time values carry their evolving **confidence/abstention** (§E) — a live number that hasn't stabilized shows as preliminary, not final.
- **K.4 Graceful realtime degradation.** On a slow link, fall back to polling/lower update rate (§B.5) rather than freezing.

## L. Data Visualization (honest viz)

- **L.1 Show uncertainty.** Trajectories, heatmaps, shot charts, and trends render **confidence bands / error bars** (§E.5); a metric is never plotted as more precise than its `ci` (Part 40 §BA).
- **L.2 No misleading charts.** Truthful axes (no truncated-baseline distortion), honest aggregation (no averaging-away, Part 40 §H), and clear sample size — a chart is a claim + **MUST** be defensible.
- **L.3 Evidence-linked.** A data point links to its **evidence package** (clip/frame/track, Part 09/32) — the viz is a doorway to "how do you know?" (§E.4).
- **L.4 Accessible viz.** Non-color encodings + table/text alternatives (§G.4); viz is bilingual (§H).

## M. Forms, Input & Capture UX

- **M.1 Guided capture.** The capture client **coaches good filming** per tier (angle, lighting, framing, fps — Part 35 SOP) **before** recording, raising capture quality at the source.
- **M.2 Live capture feedback.** Surface the **Capture Quality Score** + gate failures (Part 35) to the operator in real time — "move the camera / add light / lock exposure" — so a bad capture is fixed on-site, not discovered later.
- **M.3 Upload UX.** Resumable, progress-shown, validated uploads (size/type, Part 41 §AF.5) with clear errors; large videos upload in background (§J.2).
- **M.4 Input validation mirrors the contract.** Client validation mirrors the server's (Part 37 schema) for fast feedback — but the **server re-validates** (§B.2); client validation is UX, not security.

## N. Navigation, IA & Role-Aware UI

- **N.1 Information architecture.** The screen map + navigation follow Part 32; routing is deep-linkable + shareable (respecting access, §O).
- **N.2 Role-aware UI.** The UI shows only the actions a role may take (Part 41 §E) — a coach doesn't see admin controls — **for clarity**, while the **server enforces** (§B.2); hiding a button is never the access control.
- **N.3 Progressive disclosure.** Surface the essential first; depth (evidence §E.4, advanced stats) is a drill-down — manage cognitive load for non-technical coaches (Part 32).
- **N.4 Consistent patterns.** Navigation, empty states, and errors use the design-system patterns (§F) so the product is learnable.

## O. Client Security

- **O.1 No secrets in the client.** API keys/secrets **never** ship to the client (Part 41 §B.7/§Y); the client holds only short-lived user tokens.
- **O.2 Token handling.** Tokens are stored + sent securely (httpOnly cookies for web where possible, secure storage on native); **short TTL + refresh rotation** (Part 41 §D); logout clears + revokes.
- **O.3 Web hardening.** **CSP**, Subresource Integrity, output encoding (anti-**XSS**), **CSRF** protection for cookie flows, and the security headers (Part 41 §X) are enforced.
- **O.4 Auth flows.** Login/SSO (OIDC/SAML, Part 41 §AD), MFA prompts (Part 41 §D.6), and hardened account recovery (Part 41 §D.8) are first-class flows.
- **O.5 No PII in client telemetry.** Client logs/analytics scrub PII/tokens (Part 41 §K.3 / Part 42 §R); consent gates analytics (Part 41 §H).
- **O.6 Supply chain.** Client dependencies are scanned + pinned (Part 41 §S); a compromised npm package is a client-side breach.

## P. Client Observability

- **P.1 RUM.** Real-user monitoring captures actual client latency/Web-Vitals/errors (Part 42 §Q.3) — server metrics can't see the client.
- **P.2 Crash/ANR.** Native/desktop crash + ANR reporting (Part 42 §Q.4); web error tracking with source maps.
- **P.3 Feature flags client-side.** Flags (Part 44 §J.2) gate UI features for progressive rollout + kill-switch; flag state is telemetry.
- **P.4 Product analytics.** Funnel/journey analytics (Part 42 §Y) are **consent-gated** (Part 41 §H), privacy-respecting, and never log sensitive content.

## Q. Client Testing

- **Q.1 Unit + component.** Components are unit + interaction tested; the reliability-render contract (§E) is tested (a `<Metric>` with `abstain` shows the abstain state).
- **Q.2 E2E journeys = synthetic monitors.** Critical journeys (Part 32: login, upload→analyze→profile, game-plan) are end-to-end tested **and reused as production synthetic monitors** (Part 42 §Q.1).
- **Q.3 Visual regression + a11y.** Visual-regression snapshots + **automated a11y tests** (axe-style) gate the design system (§F/§G).
- **Q.4 Contract tests.** The client is tested against the **OpenAPI contract** (Part 37) so a backend change that breaks the client is caught in CI (§S).
- **Q.5 Cross-surface.** Cross-browser + device + RTL + offline (§J) are part of the matrix.

## R. Client Build & Delivery

- **R.1 Through Part 44.** Client CI/CD uses the delivery pipeline (Part 44): build → test (§Q) → a11y/perf/i18n gates (§S) → sign → deploy.
- **R.2 Web deploy.** Static assets to a CDN with cache-busting + long-cache hashing; **progressive rollout** + instant rollback (Part 44 §J/§L).
- **R.3 App stores.** Mobile/desktop ship through store review with **forced-update** support for security fixes (Part 41) and staged rollout.
- **R.4 Versioning + compatibility.** The client declares the **API version** it needs (Part 37 §K coordinated versions); a client **MUST** handle a deprecated-but-not-removed API gracefully (no hard break, Part 37/39).
- **R.5 Generated-client sync.** Regenerating the API client (§D.1) is part of the build; drift from `openapi.yaml` fails CI (§S).

## S. Governance & CI Enforcement (client invariants)

CI **MUST** keep the client honest + accessible by construction (the client analogue of the backend governance gates).

| Check | Invariant | Status |
|-------|-----------|--------|
| `no-hardcoded-strings` | all display text from `i18n` (Part 38), no literals (§H.1) | ⬜ |
| `a11y-gate` | automated a11y tests pass; WCAG AA (§G) | ⬜ |
| `bundle-budget` | per-route JS/asset budget not exceeded (§I.2) | ⬜ |
| `web-vitals` | LCP/INP/CLS within budget (§I.1) | ⬜ |
| `reliability-render` | measured values render the envelope; lint bans bare-number `<Metric>` (§E.1) | ⬜ |
| `api-client-in-sync` | generated client matches `api/openapi.yaml` (§D.1) | ⬜ |
| `contract-tests` | client passes OpenAPI contract tests (§Q.4) | ⬜ |
| `csp-present` | security headers/CSP configured (§O.3) | ⬜ |

- **S.1** Each invariant has a test; ⬜→✅ when the client + its CI assertion exist.
- **S.2** The i18n build (✅ `i18n/build.py`, already a CI job, Part 44 §C.2) is the seed `no-hardcoded-strings` extends.

## T. Build-Artifacts Status (honest, grounded in repo)

| Capability | Artifact | Status |
|------------|----------|--------|
| OpenAPI contract (→ generated client) | `api/openapi.yaml` (Part 37) | ✅ (seed) |
| i18n vocabulary (EN/AR) + build | `i18n/glossary.json`→`en/ar` + `build.py` (Part 38) | ✅ (seed) |
| Reliability-envelope schema to render | Part 40 §C (`reliability.py`) | ✅ (seed) |
| Capture-quality signals to surface | `capture_quality.py` (Part 35) | ✅ (seed) |
| **Any frontend/client code** | — | ⬜ (greenfield) |
| Design system / component library | — | ⬜ |
| Web / mobile / desktop / courtside apps | — | ⬜ |
| Reliability-honest components (§E) | — | ⬜ |
| a11y + i18n/RTL + perf gates | i18n build job exists | 🟡 |
| Offline/real-time/viz/capture UX | — | ⬜ |
| Client security (CSP/auth flows) + RUM | — | ⬜ |

The honest truth: **the client is greenfield** — no frontend exists yet. What exists are the **contracts it must honor** (✅ seeds: OpenAPI, i18n, reliability envelope, capture signals). This spec ensures that when the client *is* built, it is **reliability-honest, accessible, and bilingual from line one** — not retrofitted (§B.4). Stating the greenfield reality is the point (Part 41 §B.5).

## U. Open Problems & Roadmap (honest)

- **Rendering uncertainty without overwhelming** (§E/§L) — showing confidence/CIs to non-technical coaches **clearly** is a real design challenge; roadmap: progressive disclosure (§N.3) + user testing (Part 32).
- **Offline conflict at scale** (§J.4) — robust offline editing + sync for courtside is hard; roadmap: CRDT/last-writer-wins with server authority.
- **Broadcast-grade real-time** (§K) — low-latency overlays for live TV (Part 14) push beyond web-app latency; roadmap, surface-specific.
- **Bilingual data-viz** (§H/§L) — RTL + Arabic typography in charts is under-tooled; roadmap: design-system viz primitives.

## V. Glossary & Notation

Canonical via Part 38 where applicable: **client / surface** (web/mobile/desktop/courtside/overlay) · **server-state vs client-state** · **generated API client** (from OpenAPI, Part 37) · **reliability-honest UI** (§E) · **abstain state** ("I don't know", Part 40) · **tier badge** (T1/T2/T3) · **evidence drill-down** (Part 32) · **design system / tokens / component library** · **WCAG / ARIA / a11y** · **i18n / l10n / RTL / bidi** (Part 38) · **Core Web Vitals (LCP/INP/CLS)** · **bundle budget** · **PWA / service worker / store-and-forward** (offline, Part 42 §X) · **WebSocket / SSE** (real-time, Part 39) · **optimistic UI / reconciliation** · **CSP / SRI / XSS / CSRF** (Part 41) · **RUM** (Part 42) · **feature flag** (Part 44) · **contract test** (vs Part 37). These notations are used across Parts 14/32/37/38/40/41/42/44/45.

This document is the authoritative experience (frontend/client) law for TT-OS; with the data model (37), ontology (38), event contract (39), reliability law (40), security law (41), operability law (42), intelligence law (43), and delivery law (44), it completes the platform's build foundation — **structure, meaning, communication, honesty, trust, operability, intelligence, delivery, and experience.**

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
