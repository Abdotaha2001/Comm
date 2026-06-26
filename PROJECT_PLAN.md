# 🏓 TT-OS — PROJECT EXECUTION PLAN

> Companion to `MASTER_SPEC/` (the "what"). This is the **"how & in what order"**.
> Strategy in one line: **reliability-first vertical slices, models shipped in waves, deliver value before all ~47 models are trained.**

---

## 1. Where we are → where we're going
- **Baseline:** one Colab notebook (single-match analyzer) ≈ **15%** of the vision; heuristic scoring (~30% hit FP by its own logs), no spin, rough speed, no DB, no UI, no tests.
- **Target:** an AI operating system for table tennis (18-part spec, ~165 components, **~47 dedicated trained models**, 2 cross-cutting layers).
- **We do NOT big-bang it.** We ship thin end-to-end slices, each usable, each honest about its own reliability.

## 2. Operating principles (non-negotiable)
1. **3 design laws:** Capture-Tier awareness · Reliability awareness · Everything-is-a-Model.
2. **Vertical slice > horizontal layer.** Every phase ends with something a coach can actually use.
3. **Data is the bottleneck.** Every phase carries its own data/labeling plan.
4. **Fallback + abstention.** Until a model hits its target metric, the system uses a confidence-labeled heuristic or says "I don't know" — never a silent guess.
5. **Measure before you trust.** Scoreboard OCR gives free ground truth from day one.

---

## 3. Phase roadmap

| Phase | Goal | Key deliverables | Model wave | Exit criteria (KPIs) | Rough duration* |
|-------|------|------------------|-----------|----------------------|----------------|
| **P0 — Foundation** | Notebook → product skeleton | Modular refactor, Postgres schema, API + GPU worker, reliability scaffolding, CI/tests | — | Upload video via API → worker runs → results in DB **with confidence tags** → retrievable; CI green | ~1 quarter |
| **P1 — Flagship MVP** | The "beat your opponent" loop, end-to-end | Player profiles + multi-video aggregation, opponent dossier, matchup + game-plan, coach UI, pre-match PDF | **Wave 1** | A coach creates a player → uploads videos → sends opponent → gets a **confidence-labeled game plan**; Wave-1 models beat heuristic baselines on a validation set | ~1–2 quarters |
| **P2 — Accuracy & Physics** | Make the numbers true | Custom TT-ball model, **spin engine**, 3D via multi-cam, benchmark + golden set | **Wave 2** | Metric speed/spin with calibrated confidence; published accuracy vs validation set; golden-set regression gate live | ~2 quarters |
| **P3 — Intelligence** | Data → development | Knowledge graph + expert system, periodization + talent framework, tactical/opponent AI, closed-loop drills | **Wave 3** | NL Q&A grounded + evidence-cited; opponent simulation; plan→outcome shows measurable improvement | ~2 quarters |
| **P4 — Officiating & Federation** | Institutional grade | ITTF rules in 3D, authority/governance, tournament + federation ops, live redundancy | **Wave 4** | Officiating accuracy >target on golden set with abstention; multi-tenant federation console; live-match failover | ~2+ quarters |

*Durations assume a **small dedicated team (3–6 people)**. See §11 for how this scales. Solo → multiply; funded team → parallelize workstreams.

---

## 4. Near-term detailed plan (P0 + P1)

### P0 — Foundation milestones
| ID | Milestone | Tasks | Depends on |
|----|-----------|-------|-----------|
| M0.1 | Repo & CI | Monorepo layout, package boundaries (engines), linting, test scaffold, CI pipeline | — |
| M0.2 | Modular extraction | Move notebook logic into installable packages (`perception`, `scoring`, `coaching`) — **no behavior change**, add tests around current behavior | M0.1 |
| M0.3 | Data model | Postgres schema + migrations: `players, player_videos, matches, rallies, shots, events, player_profiles, opponent_dossiers, matchups, game_plans, plan_outcomes` | M0.1 |
| M0.4 | API + worker | FastAPI skeleton, job queue, GPU worker that runs the existing pipeline on an uploaded video; object storage for video/artifacts | M0.2, M0.3 |
| M0.5 | Reliability v0 | Every engine output becomes `{value, confidence, provenance, tier}`; report renders confidence honestly | M0.2 |
| M0.6 | Auth & tenancy v0 | Basic auth + org scoping (multi-tenant ready) | M0.4 |

**P0 exit demo:** upload a match video through the API → it processes on a worker → results land in Postgres tagged with confidence → fetch them back. Tests + CI green.

### P1 — Flagship MVP milestones
| ID | Milestone | Tasks | Depends on |
|----|-----------|-------|-----------|
| M1.1 | Player profiles | CRUD for players (pro/junior), multi-video upload, **aggregation across a player's videos** into one persistent profile | P0 |
| M1.2 | Reliability anchor | **Scoreboard OCR (M41)** + cross-check vs computed score → measures scoring accuracy + harvests ground truth | M0.4 |
| M1.3 | Wave-1 models | Train & integrate: TT-ball detector (M1), pose (M4), handedness/grip (M18/M19), stroke classifier (M22–M24). Heuristic fallback until target metric | M1.2, data |
| M1.4 | Opponent dossier | Build opponent profile from sent videos/name; **sparse-footage aware** + style classifier (M34) v0 | M1.1 |
| M1.5 | Matchup + plan | Matchup model (M35) + **game-plan generator (M36)** v0 — grounded, evidence-cited, confidence-labeled | M1.1, M1.4 |
| M1.6 | Coach UI | Profile dashboard + "Prepare for opponent" flow + pre-match report (PDF, coach + simplified player version) | M1.5 |
| M1.7 | Outcome loop | Plan-vs-outcome tracking (did the plan work?) feeding back | M1.5 |

**P1 exit demo:** a coach creates "Player Ahmed", uploads 3 of his matches, sends an opponent's video, and receives a **confidence-labeled game plan + PDF**. The scoreboard cross-check reports how accurate scoring is. Wave-1 models beat the heuristic baselines on a held-out set.

---

## 5. Parallel workstreams (tracks)
| Track | Owns | Active from |
|-------|------|-------------|
| **Platform/Backend** | API, DB, queue, storage, auth, multi-tenancy, ops | P0 |
| **CV / Models** | the ~47 models, training, eval, registry | P1 (Wave 1) |
| **Data / ML-Eng** | datasets, annotation, synthetic data, active learning, benchmarks | P0 (start collecting early) |
| **Product / Frontend** | coach UI, dashboards, reports, mobile later | P1 |
| **Reliability / QA** | confidence calibration, golden sets, abstention, tests | P0 |
| **Coaching/Domain** | rubrics, knowledge base, validating outputs with real coaches | P1 |

## 6. Team & roles (lean founding team)
ML/CV engineer (×1–2) · Backend engineer · Frontend engineer · Data/annotation lead · **Domain expert (high-performance coach + an umpire advisor)**. The domain expert is not optional — they define the rubrics and validate every coaching/officiating output.

## 7. Data strategy (the real core cost)
- **Now:** start harvesting from every processed video (scoreboard OCR = free score ground truth; uncertain frames → label queue via active learning).
- **Wave 1:** label ball/pose/handedness/grip/stroke sets; bootstrap with public sports datasets + self-supervised pretrain on unlabeled match footage.
- **Wave 2:** spin/3D via **synthetic (sim2real)** + a high-speed/IMU ground-truth rig for a small calibrated set.
- **Always:** inter-annotator agreement, bias audit, DVC versioning (Part 12).

## 8. Tech stack (from spec Part 16F)
PyTorch · Ultralytics/RT-DETR · RTMPose/MMPose · OpenCV · TensorRT/ONNX/Triton · FastAPI · Postgres (+pgvector) · S3 · Kafka · Redis · Neo4j (knowledge graph) · React/Next.js · DVC + MLflow/W&B · Kubernetes + GPU pools · grounded latest-Claude for reasoning/Q&A.

## 9. Risks & mitigations
| Risk | Mitigation |
|------|-----------|
| Data scarcity (esp. spin) | Self-supervision + synthetic + active learning; start collecting in P0 |
| Trying to train 47 models at once | Strict wave sequencing; shared backbones; fallback+abstention |
| Building features on untrusted data | Reliability layer from day one; scoreboard cross-check |
| Scope creep (it already happened in the spec) | Phase gates; nothing starts without an exit criterion |
| Officiating liability | Stay advisory until P4 golden-set accuracy + governance (Part 09) |
| Solo/under-resourcing | Cut to the P0→P1 vertical slice only; defer P2–P4 |

## 10. Definition of done (per phase) = the KPIs in §3 exit columns
No phase is "done" on code written — only on its **measurable exit criterion** met and demoable.

## 11. How the plan scales with resources
- **Solo / nights-and-weekends:** do **P0 + P1 only**, single camera (T1), Wave-1 models, ship the flagship MVP. Ignore P2–P4 until there's a team.
- **Small team (3–6):** the timeline in §3.
- **Funded team (10+):** run the workstreams (§5) in parallel; pull P2 accuracy forward alongside P1.

---

## 12. ▶️ Immediate next sprint (start now)
1. **M0.1** — scaffold the repo (packages, CI, tests, linting).
2. **M0.3** — write the Postgres schema + migrations for players/videos/profiles.
3. **M0.2** — extract the notebook's scoring + coaching into a tested module (no behavior change).
4. **M1.2 spike** — prototype **Scoreboard OCR** on a sample video (fastest reliability win).

> Recommended first commit: **M0.1 + M0.3** (skeleton + data model) — they unblock everything and are low-risk.

---

*This plan is a living document. Re-tune phase durations to your actual team size and budget (§11).*
