# PART 28 — ONTOLOGY & GLOSSARY (EN ↔ AR controlled vocabulary)

> Read `00_INDEX.md` first. **The single source of truth for terms.** Every enum (Part 27), label, training annotation (Part 12), knowledge-graph node (Part 11), and UI string maps to a **canonical_id** here. EN + AR are *display* labels; the `canonical_id` (snake_case) is the key used in code/data.

## How to use
- **Labeling/data:** annotators pick `canonical_id`s — never free text.
- **i18n:** the UI renders `en` or `ar` (RTL) from the same `canonical_id`.
- **Governance:** a new term is added **here first** (versioned), then used anywhere. This file is the controlled vocabulary. **Vocabulary version: v0.2** (adds reason codes, operational enums, basic/scoring terms, abbreviations, units, synonyms; reconciled with Part 27 enums).

---

## A. Ontology — entity (node) types
Grounds the Knowledge Graph (Part 11) and mirrors the data model (Part 27).
| canonical_id | EN | AR | Backing table (Part 27) |
|--------------|----|----|--------------------------|
| `organization` | Organization | جهة / مؤسسة | organizations |
| `user` | User | مستخدم | users |
| `player` | Player | لاعب | players |
| `coach` | Coach | مدرب | users(role=coach) |
| `umpire` | Umpire | حكم | users(role=umpire) |
| `video` | Video | فيديو | videos |
| `match` | Match | مباراة | matches |
| `rally` | Rally / Point | تبادُل / نقطة | rallies |
| `shot` | Shot / Stroke | ضربة | shots |
| `event` | Event | حدث | events |
| `player_profile` | Player profile | ملف اللاعب | player_profiles |
| `opponent_dossier` | Opponent dossier | ملف الخصم | opponent_dossiers |
| `matchup` | Matchup | مواجهة | matchups |
| `game_plan` | Game plan | خطة اللعب | game_plans |
| `drill` | Drill | تمرين | drills |
| `training_plan` | Training plan | خطة تدريب | training_plans |
| `equipment` | Equipment | عُدّة | player_equipment |
| `strength` | Strength | نقطة قوة | (in profile) |
| `weakness` | Weakness | نقطة ضعف | (in profile) |
| `injury` | Injury | إصابة | (sports science) |
| `impairment` | Impairment | إعاقة | players(impairment_type) |

### Relationship (edge) types
| canonical_id | EN | AR |
|--------------|----|----|
| `plays_for` | plays for | يلعب لـ |
| `competed_in` | competed in | شارك في |
| `executed` | executed (shot) | نفّذ (ضربة) |
| `has_strength` / `has_weakness` | has strength / weakness | لديه قوة / ضعف |
| `countered_by` | countered by | يُكسر بـ |
| `corrected_by` | corrected by (drill) | يُصحَّح بـ (تمرين) |
| `uses_equipment` | uses equipment | يستخدم عُدّة |
| `classified_as` | classified as (style) | مُصنّف كـ (أسلوب) |
| `has_impairment` | has impairment | لديه إعاقة |
| `prescribed` | prescribed (plan) | وُصِف له (خطة) |
| `beats` / `loses_to` | beats / loses to | يفوز على / يخسر أمام |

---

## B. Event taxonomy (`event.type` — Part 27)
| canonical_id | EN | AR |
|--------------|----|----|
| `bounce` | Bounce | ارتداد / نطّة |
| `net` | Net touch | لمس الشبكة |
| `hit` | Hit / contact | ضرب / تلامس |
| `serve` | Serve | إرسال |
| `point` | Point | نقطة |
| `let` | Let (replay) | إعادة (ليت) |
| `violation` | Violation | مخالفة |
| `timeout` | Timeout | وقت مستقطع |
| `set_change` | Set change | تغيير الشوط |
| `score_read` | Scoreboard read | قراءة النتيجة |

---

## C. Glossary by domain (EN ↔ AR)

### C1. Serves (`stroke_type` serve_*)
| canonical_id | EN | AR |
|--------------|----|----|
| `serve_pendulum` | Pendulum serve | إرسال البندول |
| `serve_reverse_pendulum` | Reverse pendulum | البندول العكسي |
| `serve_tomahawk` | Tomahawk serve | إرسال التوماهوك |
| `serve_reverse_tomahawk` | Reverse tomahawk | التوماهوك العكسي |
| `serve_shovel` | Shovel serve | إرسال الجاروف |
| `serve_backhand` | Backhand serve | إرسال خلفي |
| `serve_high_toss` | High-toss serve | إرسال الرمية العالية |
| `serve_ghost` | Ghost serve | الإرسال الشبح |
| `serve_hook` | Hook serve | الإرسال الخطّافي |
| `serve_windshield_wiper` | Windshield-wiper serve | إرسال المسّاحة |

### C2. Strokes — receive / attack / defense
| canonical_id | EN | AR |
|--------------|----|----|
| `push_short` / `push_long` | Short / long push | الدفع القصير / الطويل |
| `flick` | Flick / flip | الفليك |
| `banana_flick` | Banana flick / chiquita | فليك الموزة / الشيكيتا |
| `strawberry_flick` | Strawberry flick | فليك الفراولة |
| `drop_shot` | Drop shot | الكرة القصيرة الخادعة |
| `drive` | Drive | الدرايف / الضربة المستقيمة |
| `loop` | Loop (topspin) | اللوب |
| `hook_loop` / `fade_loop` | Hook / fade loop | اللوب الخطّافي / المنحرف |
| `counterloop` | Counterloop | اللوب المضاد |
| `smash` | Smash / kill | السماش / الضربة الساحقة |
| `block` | Block | الصد / البلوك |
| `punch_block` | Punch / active block | الصد الهجومي |
| `chop_block` | Chop block | صد القطع |
| `chop` | Chop | القطع |
| `fish` | Fish | الكرة المرتفعة القريبة |
| `lob` | Lob | الكرة المرتفعة الدفاعية |
| `dig` | Dig | رد السماش الدفاعي |
| `counter_drive` | Counter-drive | الضربة المضادة |
| `twiddle` | Twiddle (racket flip) | لفّ المضرب |

### C3. Spin (`spin_type`)
| canonical_id | EN | AR |
|--------------|----|----|
| `topspin` | Topspin | دوران أمامي (توب سبين) |
| `backspin` | Backspin | دوران خلفي (قطع) |
| `sidespin_left` / `sidespin_right` | Side spin L / R | دوران جانبي يسار / يمين |
| `corkspin` | Corkspin | دوران محوري |
| `mixed` | Mixed spin | دوران مختلط |
| `no_spin` | No spin | بدون دوران |

### C4. Footwork
| canonical_id | EN | AR |
|--------------|----|----|
| `one_step` | One-step | الخطوة الواحدة |
| `chasse_step` | Chassé / side-step | خطوة الشاسيه / الجانبية |
| `slide_step` | Slide / shuffle | الانزلاق |
| `cross_step` | Cross-step / crossover | الخطوة المتقاطعة |
| `pivot` | Pivot / turn | الدوران / البيفوت |

### C5. Equipment (Part 20) — incl. Egyptian terms
| canonical_id | EN | AR (incl. common) |
|--------------|----|--------------------|
| `blade` | Blade | الخشبة / البليد |
| `rubber` | Rubber | المطاط / الجلد |
| `sponge` | Sponge | الإسفنج / السفنجة |
| `inverted` | Inverted / smooth | الأملس / الجلد |
| `short_pips` | Short pips | الحبوب القصيرة / السريعة |
| `medium_pips` | Medium pips | الحبوب المتوسطة |
| `long_pips` | Long pips | الحبوب الطويلة |
| `anti` | Anti-spin | الأنتي / الصد |
| `ox` | OX (no sponge) | بدون سفنجة |
| `tacky` / `grippy` | Tacky / grippy | لزِج / ماسك |
| `hybrid` | Hybrid rubber | المطاط الهجين |
| `boosting` | Boosting (illegal) | التحسين الممنوع |

### C6. Playing styles (`style_class`)
| canonical_id | EN | AR |
|--------------|----|----|
| `fh_looper` | Forehand looper | مهاجم بالأمامية |
| `two_winged_attacker` | Two-winged attacker | مهاجم بالجهتين |
| `counter_driver` | Counter-driver / blocker | صدّاد قريب من الطاولة |
| `all_rounder` | All-rounder | شامل |
| `chopper` | Chopper / defender | قطّاع / مدافع |
| `penhold_looper` | Penhold looper | مهاجم قبضة القلم |
| `penhold_rpb` | Penhold RPB | قبضة القلم بالظهر العكسي |
| `short_pips_hitter` | Short-pips hitter | ضارب الحبوب القصيرة |
| `combination_chopper` | Combination-bat chopper | قطّاع بمضرب مركّب |

### C7. Grips (`grip`)
| canonical_id | EN | AR |
|--------------|----|----|
| `shakehand` | Shakehand | قبضة المصافحة |
| `penhold_chinese` | Chinese penhold | قبضة القلم الصينية |
| `penhold_japanese` | Japanese/Korean penhold | قبضة القلم اليابانية |
| `seemiller` | Seemiller grip | قبضة سيميلر |

### C8. Rules / officiating
| canonical_id | EN | AR |
|--------------|----|----|
| `service` | Service | الإرسال |
| `good_return` | Good return | إرجاع صحيح |
| `let` | Let | إعادة / ليت |
| `edge_ball` | Edge ball | كرة الحافة |
| `deuce` | Deuce | تعادل (10-10) |
| `expedite` | Expedite system | نظام التعجيل |
| `illegal_serve` | Illegal serve | إرسال مخالف |
| `obstruction` | Obstruction | إعاقة الكرة |
| `double_hit` | Double hit | ضرب مزدوج |
| `free_hand` | Free hand | اليد الحرة |

### C9. Tactics / training (Parts 21, 22)
| canonical_id | EN | AR |
|--------------|----|----|
| `third_ball` | Third-ball attack | هجوم الكرة الثالثة |
| `serve_receive` | Serve & receive | الإرسال والاستقبال |
| `crossover` | Crossover / elbow | نقطة التقاطع / الكوع |
| `placement` | Placement | التوجيه |
| `multiball` | Multiball | الكرات المتعددة |
| `falkenberg` | Falkenberg drill | تمرين فالكنبرج |
| `block_practice` | Block (repetitive) practice | تمرين متكرر |
| `random_practice` | Random practice | تمرين عشوائي |
| `periodization` | Periodization | التدوير التدريبي |

### C10. Anatomy / biomechanics (Part 25)
| canonical_id | EN | AR |
|--------------|----|----|
| `kinetic_chain` | Kinetic chain | السلسلة الحركية |
| `trunk_rotation` | Trunk rotation | دوران الجذع |
| `weight_transfer` | Weight transfer | نقل الوزن |
| `center_of_mass` | Center of mass | مركز الكتلة |
| `range_of_motion` | Range of motion | مدى الحركة |
| `rotator_cuff` | Rotator cuff | الكفّة المُدوّرة |

### C11. Para / disability (Part 24)
| canonical_id | EN | AR |
|--------------|----|----|
| `para_class` | Sport class (1–11) | الفئة (١–١١) |
| `wheelchair` | Wheelchair | كرسي متحرك |
| `standing` | Standing | وقوف |
| `impaired_muscle_power` | Impaired muscle power | ضعف قوة العضلات |
| `limb_deficiency` | Limb deficiency | نقص طرف |
| `short_stature` | Short stature | قِصر القامة |
| `hypertonia` | Hypertonia | فرط التوتر العضلي |
| `ataxia` | Ataxia | الترنّح |
| `athetosis` | Athetosis | الكنع |
| `intellectual` | Intellectual impairment | إعاقة ذهنية |

### C12. Platform / AI terms
| canonical_id | EN | AR |
|--------------|----|----|
| `confidence` | Confidence | درجة الثقة |
| `reliability` | Reliability | الموثوقية |
| `abstain` | Abstain ("I don't know") | امتناع ("مش متأكد") |
| `capture_tier` | Capture tier | مستوى التصوير |
| `model` | Model | نموذج |
| `dataset` | Dataset | مجموعة بيانات |
| `provenance` | Provenance | مصدر القرار |
| `game_plan` | Game plan | خطة اللعب |
| `matchup` | Matchup | المواجهة |

---

### C13. Point-outcome reasons (`rallies.reason`)
| canonical_id | EN | AR |
|--------------|----|----|
| `winner` | Clean winner | ضربة حاسمة |
| `unforced_error` | Unforced error | خطأ غير قسري |
| `missed_return` | Missed return | فشل الإرجاع |
| `ball_out` | Ball out | الكرة خارج |
| `net_fail` | Failed to clear net | لم تعبر الشبكة |
| `double_bounce` | Double bounce | ارتداد مزدوج |
| `service_fault` | Service fault | خطأ إرسال |
| `edge_winner` | Edge-ball winner | كرة حافة كاسبة |
| `timeout_call` | Timeout-based | بسبب الوقت المستقطع |

### C14. Basic & scoring terms
| canonical_id | EN | AR |
|--------------|----|----|
| `forehand` / `fh` | Forehand | الأمامية / فورهاند |
| `backhand` / `bh` | Backhand | الخلفية / باكهاند |
| `table` | Table | الطاولة |
| `net` | Net | الشبكة |
| `ball` | Ball | الكرة |
| `racket` | Racket / bat | المضرب |
| `serve_order` | Serve order | ترتيب الإرسال |
| `server` / `receiver` | Server / receiver | المُرسِل / المُستقبِل |
| `point` / `game` / `set` / `match` | Point / game / set / match | نقطة / لعبة / شوط / مباراة |
| `win` / `loss` | Win / loss | فوز / خسارة |

### C15. Operational enums (Part 27 value sets, bilingual)
| field · value | EN | AR |
|---------------|----|----|
| `capture_tier`: `t1`/`t2`/`t3` | single-cam 2D / single-cam 3D-lift / multi-cam 3D | كاميرا واحدة 2D / مرفوعة 3D / متعددة 3D |
| `mobility_mode`: `standing`/`wheelchair`/`na` | standing / wheelchair / n-a | وقوف / كرسي متحرك / غير منطبق |
| `format`: `bo3`/`bo5`/`bo7` | best of 3 / 5 / 7 | أفضل من 3 / 5 / 7 |
| `status`: `queued`/`processing`/`done`/`failed` | queued / processing / done / failed | في الطابور / قيد المعالجة / تم / فشل |
| `role`: `admin`/`coach`/`player`/`umpire`/`medical`/`scout` | admin / coach / player / umpire / medical / scout | أدمن / مدرب / لاعب / حكم / طبي / كشّاف |
| confidence level: `high`/`moderate`/`low` | high / moderate / low | عالية / متوسطة / منخفضة |
| reliability `status`: `ok`/`abstain` | ok / abstain | موثوق / امتناع |
| `drill.structure`: `regular`/`semi_random`/`random` | regular / semi-random / random | منتظم / شبه عشوائي / عشوائي |
| `drill.phase`: `off_season`/`pre_season`/`in_season` | off / pre / in-season | خارج / قبل / أثناء الموسم |
| `level`: `beginner`/`intermediate`/`advanced`/`elite` | beginner / intermediate / advanced / elite | مبتدئ / متوسط / متقدم / نخبة |
| `consent.type`: `data_processing`/`video_storage`/`image_rights`/`medical` | data / video / image-rights / medical | معالجة بيانات / تخزين فيديو / حقوق صورة / طبي |
| `artifact.type`: `video`/`chart`/`clip`/`report`/`results_json` | video / chart / clip / report / results.json | فيديو / رسم / مقطع / تقرير / نتائج |

### C16. Abbreviations
| Abbr | EN | AR |
|------|----|----|
| FH / BH | forehand / backhand | الأمامية / الخلفية |
| RPB | reverse penhold backhand | الظهر العكسي لقبضة القلم |
| OX | no-sponge rubber | مطاط بدون سفنجة |
| ITTF | Int'l Table Tennis Federation | الاتحاد الدولي |
| LARC | List of Approved Racket Coverings | قائمة المطاطات المعتمدة |
| LTAD | Long-Term Athlete Development | التطوير طويل المدى |
| PST | Psychological Skills Training | تدريب المهارات النفسية |
| GRF / COM | ground reaction force / center of mass | قوة رد الأرض / مركز الكتلة |
| SSC / ROM | stretch-shortening cycle / range of motion | دورة التمدد-التقصير / مدى الحركة |
| RPM | revolutions per minute (spin) | لفة/دقيقة (دوران) |
| ReID / OCR / KG | re-identification / OCR / knowledge graph | إعادة تعرّف / OCR / رسم معرفي |

### C17. Units & measures
| unit | EN | AR |
|------|----|----|
| `km_h` | km/h (speed) | كم/س |
| `rps` / `rpm` | revolutions per sec/min (spin) | لفة/ث / لفة/د |
| `mm` / `cm` / `m` | millimetre / cm / metre | مم / سم / م |
| `fps` | frames per second | إطار/ث |
| `ms` | millisecond | مللي ثانية |
| `px` | pixel | بكسل |
| `deg` | degree (angle) | درجة |
| `mN` | millinewton (friction) | مللي نيوتن |

### C18. Synonyms / aliases (map to the canonical_id)
| alias | canonical_id |
|-------|--------------|
| chiquita | `banana_flick` |
| underspin | `backspin` |
| smooth / pips-in | `inverted` |
| bat / paddle | `racket` |
| ping pong | table tennis |
| topspin attack | `loop` |
| defender | `chopper` |

## D. Naming conventions
- **canonical_id:** `snake_case`, ASCII, stable (never rename — deprecate instead).
- **Enums in Part 27/`schema.sql`** use these exact `canonical_id`s.
- **UI** maps `canonical_id → {en, ar}`; Arabic is **RTL** (Part 15.22).
- **Knowledge graph (Part 11)** node/edge labels = the `canonical_id`s in §A.

---

➡️ **NEXT FILE: `29_EVALUATION_METRICS_CATALOG.md`**
