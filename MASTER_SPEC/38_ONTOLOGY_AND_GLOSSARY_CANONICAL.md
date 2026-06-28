# PART 38 — ONTOLOGY & GLOSSARY (Canonical Ontology & Controlled Vocabulary)

> Read `00_INDEX.md` first. This is the **authoritative ontology and controlled vocabulary** for the platform — the semantic Single Source of Truth (SSoT) for every concept used across documentation, AI models, CV, physics, database, knowledge graph, annotation, datasets, evaluation, analytics, backend, frontend, reports, LLM prompts, and APIs.
>
> **No component may introduce terminology not defined here.** If terminology conflicts with another document, **this document prevails**. It consolidates and supersedes Part 28 for semantics; the machine-readable projection lives in `i18n/glossary.json` (canonical_id ↔ EN ↔ AR), built by `i18n/build.py` and CI-validated.
>
> RFC-2119 keywords (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`) are normative. Status: the glossary holds **184 canonical terms** (`version 0.3`).

---

## A. Scope & Principles

### A.1 Purpose
Define one canonical, language-neutral identifier (`canonical_id`) per concept, with a human-readable EN + AR label, a precise definition, and its place in a semantic graph (parents, children, relations). Eliminate ambiguity, synonyms, and divergent spellings across the codebase and the spec.

### A.2 Scope
Every domain concept the platform reasons about: entities, events, strokes, serves, spin, pose/biomechanics, equipment, match structure, player styles, para classification, and AI/reliability concepts.

### A.3 Single Source of Truth policy
- Code, schema, prompts, labels, and UI strings **MUST** reference a `canonical_id` defined here; they **MUST NOT** hard-code display strings (EN/AR come from the glossary, Part 34.G).
- `i18n/glossary.json` is the **machine-readable SSoT** for `id ↔ en ↔ ar`. This document is authoritative for **meaning** (definitions, hierarchy, relations). The two **MUST NOT** diverge (§P/§Q).
- A term **MUST** exist here before it appears anywhere else.

### A.4 Naming philosophy
`canonical_id`s are **stable, language-neutral, lowercase `snake_case`**, descriptive of the concept (not of any one language or UI). Display text is a *projection*; the id is the *identity*. Ids are **immutable once published** — rename = deprecate + add (§B).

### A.5 Relationship to Parts 01–37
This ontology names the concepts those parts specify: CV/ball (01–03), ReID/pose (04/25), strokes/spin/footwork (05/19), biomechanics (06), tactics (07/21), coaching (08/22/23), rules (09), reliability (10), equipment (20), para (24), data model (27/37), evaluation (29), annotation (30). The traceability column (`Source Parts`) ties each term back.

---

## B. Ontology Design Principles

- **B.1 Canonical naming.** Exactly one `canonical_id` per concept; one concept per id. No two ids may share a meaning (§Q).
- **B.2 Stable identifiers.** Ids are immutable; they **MUST NOT** be reused for a different concept after deprecation.
- **B.3 Machine-readable terms.** Every term is addressable by `canonical_id` in `glossary.json` and the generated `en.json`/`ar.json`.
- **B.4 Human-readable labels.** Each term **MUST** have an EN and an AR label; AR **MUST** be professional and consistent (§N).
- **B.5 Extensibility.** New terms **MUST** be addable without changing existing ids; additive change only (the glossary `version` minor-bumps).
- **B.6 Backward compatibility.** Consumers **MUST** tolerate unknown ids (forward-compat); removing a term is a breaking change (major bump, §P).
- **B.7 Versioning.** The glossary carries a SemVer-style `version`; this document tracks it. Additions → minor; removals/renames → major (§P).
- **B.8 Deprecation policy.** A term is deprecated (not deleted) with `deprecated: true` + `replaced_by`; it remains resolvable for one major cycle, then **MAY** be removed.
- **B.9 Namespace strategy.** Terms are grouped by **domain** (`entity`, `event`, `stroke`, `serve`, `spin`, `pose`, `equipment`, `match`, `style`, `para`, `ai`). The `domain` field in `glossary.json` carries the namespace (currently `ontology`; domains in this document are authoritative and SHOULD be migrated into the field — §O).

---

## C. Naming Rules

| Artifact | Rule | Example |
|----------|------|---------|
| **canonical_id** | lowercase `snake_case`, language-neutral, immutable | `banana_flick` |
| **Entities** | singular noun id; plural only for the DB table | id `player` → table `players` |
| **Events** | noun or noun-phrase id | `double_bounce`, `rally_start` |
| **Actions/strokes** | the stroke's canonical name | `counterloop`, `serve_pendulum` |
| **Metrics** | `snake_case`, unit implied by §G/Part 34.AC | `spin_rpm`, `speed_kmh` |
| **Labels (dataset)** | the `canonical_id` verbatim — never free text | `chop`, not "chopping" |
| **Enums** | enum *values* are `canonical_id`s (Part 28/34.T) | `grip ∈ {shakehand, …}` |
| **Files** | `snake_case`; SSoT files keep Part prefix | `38_…_CANONICAL.md` |
| **IDs (records)** | UUID v4 (Part 37 §I) | — |
| **Database fields** | `snake_case`; enum columns store `canonical_id`s | `players.grip` |
| **JSON** | `snake_case` keys; values that are domain concepts are `canonical_id`s | `{"stroke_type":"loop"}` |
| **Python** | identifiers `snake_case`; constants `UPPER_SNAKE`; the value carried is the `canonical_id` string | `STROKE_LOOP = "loop"` |
| **UI labels** | **MUST** be resolved from the glossary by `canonical_id`; **MUST NOT** be literals | `t("loop")` → "Loop" / "اللوب" |

A term that cannot be expressed as a `canonical_id` under these rules **MUST NOT** enter the system.

---

## D. Canonical Entity Ontology

Full template per entity: `canonical_id · EN · AR · definition · synonyms · forbidden synonyms · parent · children · related · source Parts`.

| canonical_id | EN | AR | Definition | Synonyms | Forbidden | Parent | Children | Related | Parts |
|---|---|---|---|---|---|---|---|---|---|
| `organization` | Organization | جهة / مؤسسة | The tenant boundary owning all data | org, tenant | "company" (legal-only) | — | user, player | — | 13/31/37 |
| `user` | User | مستخدم | An authenticating principal | account | "login" | organization | — | role | 31/37 |
| `player` | Player | لاعب | An athlete tracked over time | athlete | "user" | organization | player_profile | match, equipment | 04/17/24 |
| `coach` | Coach | مدرب | A user who develops players | trainer | "manager" | user | — | training_plan | 08 |
| `umpire` | Umpire | حكم | An official adjudicating a match | referee, official | — | user | — | violation, let | 09 |
| `video` | Video | فيديو | An ingested media asset | clip, footage | "film" | player | — | analysis_run | 02/12/37 |
| `match` | Match | مباراة | A contest between players | game¹ | "game" (=`game`) | tournament | game, rally | score | 09/37 |
| `tournament` | Tournament | بطولة | An organized set of matches | event² | "event" (=`event`) | organization | match | — | 15 |
| `rally` | Rally / Point | تبادُل / نقطة | One ball-in-play exchange | point³, exchange | — | match | shot, event | winner | 01/37 |
| `shot` | Shot / Stroke | ضربة | One racket-ball contact | stroke | "hit" (=`hit`) | rally | event | spin, stroke types | 05/37 |
| `event` | Event | حدث | A discrete timestamped occurrence | — | — | — | (event types §E) | rally, shot | 01/37 |
| `player_profile` | Player profile | ملف اللاعب | Derived per-player capability snapshot | profile | "passport" | player | — | strength, weakness | 17/37 |
| `opponent_dossier` | Opponent dossier | ملف الخصم | Derived scouting profile of an opponent | scouting report | — | organization | — | matchup | 07/37 |
| `matchup` | Matchup | مواجهة | Modeled my-player vs opponent | head-to-head | — | organization | game_plan | opponent_dossier | 17/21/37 |
| `game_plan` | Game plan | خطة اللعب | Prescriptive "how to beat them" plan | strategy | — | matchup | — | training_plan | 17/21 |
| `drill` | Drill | تمرين | A training exercise | exercise | — | — | — | training_plan | 22 |
| `training_plan` | Training plan | خطة تدريب | Periodized program for a player | program | — | coach | drill | — | 08/23 |
| `equipment` | Equipment | عُدّة | A player's gear assembly | gear, kit | — | player | blade, rubber, ball | spin | 20 |
| `strength` | Strength | نقطة قوة | A validated player advantage | — | — | player_profile | — | weakness | 17 |
| `weakness` | Weakness | نقطة ضعف | A validated player vulnerability | — | "flaw" | player_profile | — | game_plan | 17/21 |
| `injury` | Injury | إصابة | A health event affecting load | — | — | player | — | impairment | 06 |
| `impairment` | Impairment | إعاقة | An eligible para impairment | disability | "handicap" | player | (para types §H) | wheelchair | 24 |

¹/²/³ The English word collides with another concept; the **forbidden** column prevents misuse. "game" MUST mean `game` (a set's sub-unit), "event" MUST mean `event` (a timestamped occurrence), "point" MUST mean `point` (the scoring event), not the rally.

---

## E. Event Ontology

Events are discrete, timestamped (frame-index + fps, Part 34.AC), and carry confidence (Part 10). `domain = event`.

| canonical_id | EN | AR | Definition |
|---|---|---|---|
| `serve` | Serve | إرسال | The stroke that starts a rally |
| `receive` | Receive | الاستقبال | The return of serve |
| `bounce` | Bounce | ارتداد / نطّة | Ball contacts the table |
| `net` | Net touch | لمس الشبكة | Ball contacts the net assembly |
| `edge_contact` | Edge contact | تلامس الحافة | Ball contacts the table edge |
| `hit` | Hit / contact | ضرب / تلامس | Racket-ball contact (generic) |
| `point` | Point | نقطة | A scoring event awarded to a player |
| `let` | Let (replay) | إعادة (ليت) | A non-scoring replayed rally |
| `violation` | Violation | مخالفة | A rules infraction |
| `timeout` | Timeout | وقت مستقطع | A requested pause |
| `set_change` | Set change | تغيير الشوط | End of a game/set |
| `score_read` | Scoreboard read | قراءة النتيجة | OCR of the on-screen score |
| `rally_start` | Rally start | بداية التبادل | Rally boundary (open) |
| `rally_end` | Rally end | نهاية التبادل | Rally boundary (close) |
| `equipment_change` | Equipment change | تغيير العُدّة | Racket/covering swap |
| `capture_failure` | Capture failure | فشل الالتقاط | Capture-side fault (Part 35) |
| `winner` | Clean winner | ضربة حاسمة | Point-ending winning shot |
| `unforced_error` | Unforced error | خطأ غير قسري | Self-inflicted point loss |
| `missed_return` | Missed return | فشل الإرجاع | Failure to return the ball |
| `ball_out` | Ball out | الكرة خارج | Ball lands off-table |
| `net_fail` | Failed to clear net | لم تعبر الشبكة | Ball fails to pass the net |
| `double_bounce` | Double bounce | ارتداد مزدوج | Two bounces on one side |
| `service_fault` | Service fault | خطأ إرسال | Illegal serve |
| `edge_winner` | Edge-ball winner | كرة حافة كاسبة | Winning legal edge ball |
| `abstain` | Abstain | امتناع (مش متأكد) | Reliability abstention — the system declines to assert (Part 10) |

Outcome events (`winner`, `unforced_error`, `missed_return`, `ball_out`, `net_fail`, `double_bounce`, `service_fault`, `edge_winner`) classify *why* a `rally` ended; exactly one **MUST** attach to a completed rally.

---

## F. Stroke Ontology

Per stroke: `definition · aliases · common mistakes (misclassification risks) · classification rule`. `domain = serve | stroke`. Wings: `forehand`, `backhand` (الأمامية/الخلفية) qualify any stroke.

### F.1 Serves (`domain = serve`)
| canonical_id | EN | AR | Definition · classification rule | Aliases | Common confusion |
|---|---|---|---|---|---|
| `serve_pendulum` | Pendulum serve | إرسال البندول | FH serve, blade swings like a pendulum; spin set by contact phase | — | vs `serve_reverse_pendulum` (opposite arc) |
| `serve_reverse_pendulum` | Reverse pendulum | البندول العكسي | Pendulum with reversed wrist → opposite sidespin | reverse | vs `serve_pendulum` |
| `serve_tomahawk` | Tomahawk serve | إرسال التوماهوك | FH serve with axe-like downward-out motion | — | vs `serve_hook` |
| `serve_reverse_tomahawk` | Reverse tomahawk | التوماهوك العكسي | Tomahawk with reversed sidespin | — | vs `serve_tomahawk` |
| `serve_shovel` | Shovel serve | إرسال الجاروف | Low scooping FH serve | — | — |
| `serve_backhand` | Backhand serve | إرسال خلفي | Serve executed on the backhand wing | BH serve | — |
| `serve_high_toss` | High-toss serve | إرسال الرمية العالية | Serve with a high ball toss for added spin/deception | — | — |
| `serve_ghost` | Ghost serve | الإرسال الشبح | Heavy backspin serve that returns toward the net | — | — |
| `serve_hook` | Hook serve | الإرسال الخطّافي | Hooking sidespin serve | — | vs `serve_tomahawk` |
| `serve_windshield_wiper` | Windshield-wiper serve | إرسال المسّاحة | Wiper-like wrist arc producing variable spin | — | — |

### F.2 Strokes (`domain = stroke`)
| canonical_id | EN | AR | Definition · classification rule | Aliases | Common confusion |
|---|---|---|---|---|---|
| `push_short` | Short push | الدفع القصير | Backspin control stroke kept short | — | vs `push_long` (length) |
| `push_long` | Long push | الدفع الطويل | Deep backspin push | — | vs `push_short` |
| `flick` | Flick / flip | الفليك | Aggressive over-the-table topspin off a short ball | flip | vs `banana_flick` |
| `banana_flick` | Banana flick / chiquita | فليك الموزة / الشيكيتا | BH sidespin flick with curved arc | chiquita | forbidden: "chikita" misspelling |
| `strawberry_flick` | Strawberry flick | فليك الفراولة | Reverse-sidespin counterpart to banana | — | vs `banana_flick` |
| `drop_shot` | Drop shot | الكرة القصيرة الخادعة | Deceptive short placement | stop | — |
| `drive` | Drive | الدرايف | Flat/low-spin drive | — | vs `counter_drive` |
| `loop` | Loop (topspin) | اللوب | Primary topspin attacking stroke | topspin attack | vs `drive` (spin level) |
| `hook_loop` | Hook loop | اللوب الخطّافي | Loop with hooking sidespin | — | vs `fade_loop` |
| `fade_loop` | Fade loop | اللوب المنحرف | Loop fading the opposite way | — | vs `hook_loop` |
| `counterloop` | Counterloop | اللوب المضاد | Topspin against incoming topspin | counter-topspin | forbidden: "counter loop" (space) |
| `smash` | Smash / kill | السماش | Maximal-speed put-away | kill | — |
| `block` | Block | الصد / البلوك | Passive return absorbing pace | — | vs `punch_block` |
| `punch_block` | Punch / active block | الصد الهجومي | Active block adding pace | active block | vs `block` |
| `chop_block` | Chop block | صد القطع | Block imparting backspin | — | — |
| `chop` | Chop | القطع | Defensive backspin stroke from distance | cut | — |
| `fish` | Fish | الكرة المرتفعة القريبة | Soft near-table defensive lift | — | vs `lob` |
| `lob` | Lob | الكرة المرتفعة الدفاعية | High defensive lift from distance | — | vs `fish` |
| `dig` | Dig | رد السماش الدفاعي | Reflex defense against a smash | — | — |
| `counter_drive` | Counter-drive | الضربة المضادة | Drive against a drive | — | vs `drive` |
| `twiddle` | Twiddle (racket flip) | لفّ المضرب | Rotating the racket to change rubber | — | not a stroke outcome |

---

## G. Spin Ontology

`domain = spin`. Spin is a vector: an **axis** + a **magnitude (rpm)**; named classes are quantized regions of that space.

| canonical_id | EN | AR | Definition · physics mapping |
|---|---|---|---|
| `topspin` | Topspin | دوران أمامي | Forward roll; Magnus dips the arc (Part 19) |
| `backspin` | Backspin | دوران خلفي (قطع) | Reverse roll; Magnus floats/lifts the arc |
| `sidespin_left` | Side spin left | دوران جانبي يسار | Lateral spin curving left |
| `sidespin_right` | Side spin right | دوران جانبي يمين | Lateral spin curving right |
| `corkspin` | Corkspin | دوران محوري | Spin about the velocity axis ("corkscrew") |
| `mixed` | Mixed spin | دوران مختلط | Combined topspin/sidespin axis |
| `no_spin` | No spin | بدون دوران | Negligible rotation ("float") |
| `spin_axis` | Spin axis | محور الدوران | Unit vector of rotation (frame: Part 35.BD) |
| `spin_strength` | Spin strength | شدة الدوران | Qualitative magnitude tier |
| `rpm` | RPM | لفّة/دقيقة | Spin magnitude in revolutions/minute |

**Rules:** every spin estimate **MUST** carry `spin_axis` + `rpm` (or a quantized class) **and** a `confidence`; an uncalibrated/markerless estimate **MUST** cap confidence and **MAY** `abstain` (Part 10). "corkscrew" is an alias of `corkspin`; the canonical id is `corkspin`.

---

## H. Human Pose, Footwork, Grip & Para Ontology

`domain = pose | style | para`.

### H.1 Pose / biomechanics
`pose_landmark` (معلَم تشريحي), `joint` (مفصل), `segment` (جزء جسمي), `kinetic_chain` (السلسلة الحركية), `court_frame` (إطار إحداثيات الملعب), `handedness` (اليد المفضّلة). Joints: `shoulder` الكتف · `elbow` المرفق · `wrist` المعصم · `hip` الورك · `knee` الركبة · `ankle` الكاحل · `trunk` الجذع.

### H.2 Movement phases (a stroke's temporal segmentation)
`ready_position` وضع الاستعداد → `backswing` التحضير → `forward_swing` الاندفاع الأمامي → `contact_phase` لحظة التلامس → `follow_through` المتابعة → `recovery` العودة للوضع. A stroke **MUST** be segmentable into these ordered phases.

### H.3 Footwork
`one_step` الخطوة الواحدة · `chasse_step` خطوة الشاسيه · `slide_step` الانزلاق · `cross_step` الخطوة المتقاطعة · `pivot` الدوران/البيفوت.

### H.4 Grip & stance
Grips: `shakehand` قبضة المصافحة · `penhold_chinese` قبضة القلم الصينية · `penhold_japanese` قبضة القلم اليابانية · `seemiller` قبضة سيميلر. `stance` الوقفة. Mobility/class: `standing` وقوف · `wheelchair` كرسي متحرك.

### H.5 Player styles (`domain = style`)
`fh_looper` مهاجم بالأمامية · `two_winged_attacker` مهاجم بالجهتين · `counter_driver` صدّاد قريب من الطاولة · `all_rounder` شامل · `chopper` قطّاع/مدافع · `penhold_looper` مهاجم قبضة القلم · `penhold_rpb` قبضة القلم بالظهر العكسي · `short_pips_hitter` ضارب الحبوب القصيرة · `combination_chopper` قطّاع بمضرب مركّب.

### H.6 Para impairment types (`domain = para`, Part 24)
`impaired_muscle_power` ضعف قوة العضلات · `impaired_passive_rom` محدودية مدى الحركة · `limb_deficiency` نقص طرف · `leg_length_difference` فرق طول الساقين · `short_stature` قِصر القامة · `hypertonia` فرط التوتر العضلي · `ataxia` الترنّح · `athetosis` الكنع · `intellectual` إعاقة ذهنية. Classes are expressed via `wheelchair`/`standing` + the numeric class 1–11 (Part 24).

---

## I. Equipment Ontology

`domain = equipment` (Part 20).

| canonical_id | EN | AR | Definition |
|---|---|---|---|
| `blade` | Blade | الخشبة / البليد | The wooden paddle body |
| `rubber` | Rubber (covering) | المطاط (الكسوة) | A blade covering (topsheet + sponge) |
| `sponge` | Sponge | الإسفنج / السفنجة | Foam layer under the topsheet |
| `inverted` | Inverted / smooth | الأملس / الجلد | Smooth topsheet (pips inward) |
| `short_pips` | Short pips | الحبوب القصيرة | Short outward pimples |
| `medium_pips` | Medium pips | الحبوب المتوسطة | Medium outward pimples |
| `long_pips` | Long pips | الحبوب الطويلة | Long outward pimples (spin-reversal) |
| `anti` | Anti-spin | الأنتي / الصد | Low-friction inverted rubber |
| `ox` | OX (no sponge) | بدون سفنجة | Topsheet without sponge |
| `tacky` | Tacky | لزِج | High-grip Chinese-style topsheet |
| `grippy` | Grippy | ماسك | Grippy (non-tacky) topsheet |
| `hybrid` | Hybrid rubber | المطاط الهجين | Tacky-ish hybrid topsheet |
| `racket` | Racket / bat | المضرب | Assembled blade + rubbers |
| `ball` | Ball | الكرة | 40 mm poly ball |
| `table` | Table | الطاولة | 2.74 × 1.525 m playing surface |
| `shoes` | Shoes | الحذاء | Footwear (footwork/biomech context) |
| `robot` | Ball robot | روبوت الكرات | Ball-feeding training machine |
| `sensor` | Sensor | حسّاس | Radar/IMU/force/environmental sensor |
| `camera` | Camera | كاميرا | Capture device (Part 35) |
| `lighting` | Lighting | الإضاءة | Venue illumination (Part 35) |
| `environment` | Environment | البيئة | Ambient conditions (temp/humidity, Part 19/35) |

The physical net is referenced by the `net` event (لمس الشبكة) and the `table` assembly. Equipment **MUST** be recorded with a capture session as a spin prior (Part 20/35.K).

---

## J. Match Ontology

`domain = match`. Structural hierarchy: `tournament` → `match` → `game` → rally/point → `shot`.

| canonical_id | EN | AR | Definition |
|---|---|---|---|
| `tournament` | Tournament | بطولة | Organized set of matches |
| `match` | Match | مباراة | Best-of-N games between two sides |
| `game` | Game | لعبة | A game to 11 (2 clear) |
| `set` | Set | شوط | Synonym tier for a game in some locales |
| `rally` | Rally / Point | تبادُل / نقطة | One ball-in-play exchange |
| `point` | Point | نقطة | The scoring event |
| `shot` | Shot / Stroke | ضربة | One racket-ball contact |
| `sequence` | Sequence / pattern | تسلسل / نمط | A recurring shot pattern (tactics, Part 21) |
| `timeline` | Timeline | الخط الزمني | Ordered event stream of a match |
| `score_read` | Scoreboard read | قراءة النتيجة | OCR-derived score state |
| `statistic` | Statistic | إحصائية | An aggregated measured quantity |
| `win` | Win | فوز | Match/game won |
| `loss` | Loss | خسارة | Match/game lost |

`game` and `set` denote the same structural unit; **`game` is canonical** for scoring logic (Part 09), `set` is retained for locale display.

---

## K. AI & Reliability Ontology

`domain = ai` (Parts 10/12/29/37).

| canonical_id | EN | AR | Definition |
|---|---|---|---|
| `model` | Model | نموذج | A trained AI artifact (Part 18) |
| `dataset` | Dataset | مجموعة بيانات | A versioned data collection (Part 12) |
| `annotation` | Annotation | وسم / تعليق توضيحي | A human/auto label (Part 30) |
| `prediction` | Prediction | تنبؤ | A model output |
| `ground_truth` | Ground truth | الحقيقة المرجعية | The reference label |
| `confidence` | Confidence | درجة الثقة | Calibrated certainty `[0,1]` (Part 10) |
| `reliability` | Reliability | الموثوقية | Trustworthiness of an output |
| `reliability_envelope` | Reliability envelope | غلاف الموثوقية | `{value, confidence, ci, tier, source, status}` (Part 10) |
| `calibration` | Calibration | المعايرة | Aligning confidence with accuracy / camera calibration |
| `inference` | Inference | الاستدلال | Running a model on input |
| `inference_job` | Inference job | مهمة استدلال | A queued inference unit (Part 37) |
| `training` | Training (model) | تدريب النموذج | Fitting a model |
| `validation` | Validation | التحقّق | Held-out evaluation |
| `benchmark` | Benchmark | معيار قياس | Golden-set accuracy gate (Part 29) |
| `abstain` | Abstain | امتناع (مش متأكد) | Declining to assert below threshold (Part 10) |
| `capture_tier` | Capture tier | مستوى التصوير | T1/T2/T3 capability tier (Part 02/35) |
| `capture_certification` | Capture certification | اعتماد الالتقاط | Bronze/Silver/Gold/Platinum (Part 35) |
| `provenance` | Provenance | مصدر القرار | Source/version trail of a value (Part 34.AK) |

---

## L. Knowledge Graph Relationships

Edges are typed `(subject) —predicate→ (object)`. Predicates are `snake_case`, stable, and part of the ontology.

| Subject | Predicate | Object | Cardinality |
|---------|-----------|--------|-------------|
| `organization` | owns | `player`, `user`, `video` | 1→N |
| `player` | participates_in | `match` | N↔M |
| `player` | has | `player_profile` | 1→N (versioned) |
| `player` | uses | `equipment` | 1→N |
| `equipment` | composed_of | `blade`, `rubber`, `sponge` | 1→N |
| `match` | has | `game` | 1→N |
| `match` | has | `rally` | 1→N |
| `rally` | has | `shot` | 1→N |
| `rally` | ended_by | (outcome `event`) | 1→1 |
| `shot` | is_a | (stroke/serve id) | 1→1 |
| `shot` | imparts | (spin id) + `rpm` + `spin_axis` | 1→1 |
| (spin id) | governed_by | physics (Magnus/drag, Part 19) | — |
| `shot` | executed_with | `forehand`/`backhand`, `grip` | 1→1 |
| `shot` | segmented_into | movement phases (§H.2) | 1→N (ordered) |
| `video` | produces | `analysis_run` | 1→N |
| `analysis_run` | yields | `match` | 1→0..1 |
| `analysis_run` | certified_by | `capture_certification` | 1→0..1 |
| `model` | produces | `prediction` | 1→N |
| `prediction` | carries | `confidence`, `provenance` | 1→1 |
| `prediction` | evaluated_against | `ground_truth` via `benchmark` | — |
| `opponent_dossier` | describes | `player` | N→1 |
| `matchup` | composes | `player` + `opponent_dossier` | 1→1 |
| `matchup` | produces | `game_plan` | 1→N |
| `game_plan` | exploits | `weakness` | N↔M |
| `game_plan` | prescribes | `drill`, `training_plan` | N↔M |
| `coach` | authors | `training_plan` | 1→N |
| `player` | assigned | `training_plan` | N↔M |
| `umpire` | adjudicates | `match` (`violation`, `let`) | N↔M |
| `player` | classified_by | `impairment`, `wheelchair`/`standing` | N→1 |

Every relationship instance that asserts a *measured* fact **MUST** carry a `reliability_envelope`.

---

## M. Controlled Vocabulary

- **M.1 Approved values only.** Any field whose type is a domain concept **MUST** take a `canonical_id` from this ontology; unknown values **MUST** be rejected at the boundary (`422`, Part 37 §Q).
- **M.2 Forbidden spellings (non-exhaustive, CI-checkable):** `chikita`→`banana_flick`; `counter loop`/`counter-loop`→`counterloop`; `corkscrew`→`corkspin`; `top spin`→`topspin`; `back spin`→`backspin`; `for hand`→`forehand`; `penholder`→use the specific `penhold_*`; "set" in scoring logic → `game`. Forbidden spellings **MUST NOT** appear in code, labels, datasets, or prompts.
- **M.3 Abbreviations.** Allowed: `FH`=`forehand`, `BH`=`backhand`, `RPB`=`penhold_rpb`, `ROM` (range of motion), `RPM`=`rpm`, `T1/T2/T3`=`capture_tier`. Abbreviations are display aliases only; the stored value **MUST** be the `canonical_id`.
- **M.4 Localization.** Display strings come **only** from `glossary.json` via `canonical_id`. AR is **RTL**; UI **MUST** mirror layout (Part 32.L). Numbers/units follow Part 34.AC.

---

## N. EN ↔ AR Glossary

The complete controlled vocabulary (184 terms) lives in `i18n/glossary.json` and is reproduced here by domain. Arabic is professional and **MUST** be used verbatim; no synonym may carry the same meaning (§Q). (Tables D–K above already list EN/AR/definition per term; this section is the authoritative cross-index.)

- **Entities:** `organization` جهة/مؤسسة · `user` مستخدم · `player` لاعب · `coach` مدرب · `umpire` حكم · `video` فيديو · `match` مباراة · `tournament` بطولة · `rally` تبادُل/نقطة · `shot` ضربة · `event` حدث · `player_profile` ملف اللاعب · `opponent_dossier` ملف الخصم · `matchup` مواجهة · `game_plan` خطة اللعب · `drill` تمرين · `training_plan` خطة تدريب · `equipment` عُدّة · `strength` نقطة قوة · `weakness` نقطة ضعف · `injury` إصابة · `impairment` إعاقة
- **Events:** `serve` إرسال · `receive` الاستقبال · `bounce` ارتداد/نطّة · `net` لمس الشبكة · `edge_contact` تلامس الحافة · `hit` ضرب/تلامس · `point` نقطة · `let` إعادة · `violation` مخالفة · `timeout` وقت مستقطع · `set_change` تغيير الشوط · `score_read` قراءة النتيجة · `rally_start` بداية التبادل · `rally_end` نهاية التبادل · `equipment_change` تغيير العُدّة · `capture_failure` فشل الالتقاط · `winner` ضربة حاسمة · `unforced_error` خطأ غير قسري · `missed_return` فشل الإرجاع · `ball_out` الكرة خارج · `net_fail` لم تعبر الشبكة · `double_bounce` ارتداد مزدوج · `service_fault` خطأ إرسال · `edge_winner` كرة حافة كاسبة · `abstain` امتناع
- **Serves:** `serve_pendulum` البندول · `serve_reverse_pendulum` البندول العكسي · `serve_tomahawk` التوماهوك · `serve_reverse_tomahawk` التوماهوك العكسي · `serve_shovel` الجاروف · `serve_backhand` إرسال خلفي · `serve_high_toss` الرمية العالية · `serve_ghost` الإرسال الشبح · `serve_hook` الخطّافي · `serve_windshield_wiper` المسّاحة
- **Strokes:** `push_short` الدفع القصير · `push_long` الدفع الطويل · `flick` الفليك · `banana_flick` فليك الموزة · `strawberry_flick` فليك الفراولة · `drop_shot` الكرة القصيرة الخادعة · `drive` الدرايف · `loop` اللوب · `hook_loop` اللوب الخطّافي · `fade_loop` اللوب المنحرف · `counterloop` اللوب المضاد · `smash` السماش · `block` الصد/البلوك · `punch_block` الصد الهجومي · `chop_block` صد القطع · `chop` القطع · `fish` الكرة المرتفعة القريبة · `lob` الكرة المرتفعة الدفاعية · `dig` رد السماش الدفاعي · `counter_drive` الضربة المضادة · `twiddle` لفّ المضرب · `forehand` الأمامية · `backhand` الخلفية
- **Spin:** `topspin` دوران أمامي · `backspin` دوران خلفي · `sidespin_left` جانبي يسار · `sidespin_right` جانبي يمين · `corkspin` دوران محوري · `mixed` مختلط · `no_spin` بدون دوران · `spin_axis` محور الدوران · `spin_strength` شدة الدوران · `rpm` لفّة/دقيقة
- **Footwork/Grip/Pose:** `one_step` الخطوة الواحدة · `chasse_step` الشاسيه · `slide_step` الانزلاق · `cross_step` المتقاطعة · `pivot` البيفوت · `shakehand` المصافحة · `penhold_chinese` القلم الصينية · `penhold_japanese` القلم اليابانية · `seemiller` سيميلر · `pose_landmark` معلَم تشريحي · `joint` مفصل · `segment` جزء جسمي · `kinetic_chain` السلسلة الحركية · `stance` الوقفة · `ready_position` وضع الاستعداد · `backswing` التحضير · `forward_swing` الاندفاع الأمامي · `contact_phase` لحظة التلامس · `follow_through` المتابعة · `recovery` العودة للوضع · `handedness` اليد المفضّلة · `court_frame` إطار إحداثيات الملعب · `shoulder` الكتف · `elbow` المرفق · `wrist` المعصم · `hip` الورك · `knee` الركبة · `ankle` الكاحل · `trunk` الجذع
- **Styles:** `fh_looper` مهاجم بالأمامية · `two_winged_attacker` مهاجم بالجهتين · `counter_driver` صدّاد قريب · `all_rounder` شامل · `chopper` قطّاع/مدافع · `penhold_looper` مهاجم قبضة القلم · `penhold_rpb` الظهر العكسي · `short_pips_hitter` ضارب الحبوب القصيرة · `combination_chopper` قطّاع بمضرب مركّب
- **Para:** `impaired_muscle_power` ضعف قوة العضلات · `impaired_passive_rom` محدودية مدى الحركة · `limb_deficiency` نقص طرف · `leg_length_difference` فرق طول الساقين · `short_stature` قِصر القامة · `hypertonia` فرط التوتر العضلي · `ataxia` الترنّح · `athetosis` الكنع · `intellectual` إعاقة ذهنية · `wheelchair` كرسي متحرك · `standing` وقوف
- **Equipment:** `blade` الخشبة · `rubber` المطاط · `sponge` الإسفنج · `inverted` الأملس · `short_pips` الحبوب القصيرة · `medium_pips` المتوسطة · `long_pips` الطويلة · `anti` الأنتي · `ox` بدون سفنجة · `tacky` لزِج · `grippy` ماسك · `hybrid` الهجين · `racket` المضرب · `ball` الكرة · `table` الطاولة · `shoes` الحذاء · `robot` روبوت الكرات · `sensor` حسّاس · `camera` كاميرا · `lighting` الإضاءة · `environment` البيئة
- **Match/AI:** `game` لعبة · `set` شوط · `sequence` تسلسل/نمط · `timeline` الخط الزمني · `statistic` إحصائية · `win` فوز · `loss` خسارة · `model` نموذج · `dataset` مجموعة بيانات · `annotation` وسم · `prediction` تنبؤ · `ground_truth` الحقيقة المرجعية · `confidence` درجة الثقة · `reliability` الموثوقية · `reliability_envelope` غلاف الموثوقية · `calibration` المعايرة · `inference` الاستدلال · `inference_job` مهمة استدلال · `training` تدريب النموذج · `validation` التحقّق · `benchmark` معيار قياس · `capture_tier` مستوى التصوير · `capture_certification` اعتماد الالتقاط · `provenance` مصدر القرار

---

## O. Machine-readable Artifacts

The ontology **MUST** be projected into machine-readable artifacts. `i18n/glossary.json` is the source; the rest are generated (specifications below).

| Artifact | Owner | Content | Status |
|----------|-------|---------|--------|
| `i18n/glossary.json` | this ontology | `{version, terms:[{id, domain, en, ar}]}` — the SSoT | ✅ (184 terms) |
| `i18n/en.json` · `i18n/ar.json` | `i18n/build.py` | flat `{canonical_id: label}` per locale | ✅ generated |
| `ontology.json` | spec | enriched terms `{id, domain, en, ar, definition, parent, children, synonyms, forbidden, related, source_parts, deprecated?, replaced_by?}` | ⬜ target (extends glossary.json) |
| `enums.json` | spec | `{enum_name: [canonical_id,…]}` for code generation (grips, strokes, spins, styles, para) | ⬜ target |
| `glossary.csv` | spec | flat export `id,domain,en,ar,definition` for review/import | ⬜ target |
| `terminology.yaml` | spec | human-review form of the controlled vocabulary + forbidden spellings | ⬜ target |
| `ontology.graphml` | spec | the §L relationship graph for visualization/KG load | ⬜ target |

Generation rules: every generated artifact **MUST** derive from `glossary.json` (+ this document for relations) and **MUST** be reproducible by a single command; committed copies **MUST** match a fresh generation (CI gate, §P). The enriched schema additions (`definition`, `parent`, …) are additive and **MUST NOT** break `build.py`.

---

## P. Governance

- **P.1 Versioning.** `glossary.json.version` is authoritative. **Additive** change (new term, new AR) → minor bump. **Breaking** change (remove/rename/redefine) → major bump + migration note.
- **P.2 Review process.** A new/changed term **MUST** be proposed in a PR that updates `glossary.json` **and** this document together; a `MASTER_SPEC/` + `i18n/` CODEOWNER **MUST** approve.
- **P.3 Change approval.** Renames are forbidden in place; instead deprecate the old id and add the new one with `replaced_by` (§B.8).
- **P.4 Deprecation.** Deprecated terms remain resolvable for one major cycle; consumers **SHOULD** migrate; tooling **MAY** warn.
- **P.5 Compatibility.** Consumers **MUST** tolerate unknown ids; producers **MUST NOT** emit non-canonical strings for typed fields.
- **P.6 CI expectations (future enforcement, ties Part 37 §Z).** CI **MUST**:
  1. run `i18n/build.py` and fail on **duplicate `canonical_id`s** (already enforced);
  2. fail if any term lacks a non-empty `en` **and** `ar`;
  3. fail if generated artifacts (`en.json`/`ar.json`/`ontology.json`/…) are **stale** vs `glossary.json`;
  4. fail if code/labels/datasets contain a **forbidden spelling** (§M.2);
  5. fail if a typed enum value is **not** a `canonical_id` (schema-driven, Part 37 §Z).

---

## Q. Acceptance Criteria

The ontology conforms **iff** all hold:

- **Q.1 Uniqueness.** Every `canonical_id` is unique (`build.py` passes). No two terms share a meaning (no duplicate EN **or** AR for distinct ids unless an explicit synonym).
- **Q.2 Completeness.** Every term has `id`, `domain`, `en`, `ar`; no empty labels; no placeholders.
- **Q.3 Traceability.** Every term maps to ≥1 Source Part (§D–K), and every domain concept used in Parts 01–37 has a `canonical_id` here.
- **Q.4 Single Source of Truth.** No component defines a competing term; all typed enums, labels, dataset labels, and prompts reference `canonical_id`s; `glossary.json` and this document agree.
- **Q.5 Reusability.** The vocabulary is consumable as `enums.json`/`ontology.json` without restating any term.
- **Q.6 Versioned + stable.** Ids are immutable; changes follow §P; the glossary `version` reflects the change class.
- **Q.7 Localized.** Every term has professional EN + AR; AR renders RTL; no forbidden spelling appears anywhere (§M.2).

This document is the semantic foundation of the platform and **MUST** remain stable for its lifetime; all other parts defer to it for meaning.

---

➡️ **NEXT FILE: `00_INDEX.md`** *(loop back — the spec is a living reference)*
