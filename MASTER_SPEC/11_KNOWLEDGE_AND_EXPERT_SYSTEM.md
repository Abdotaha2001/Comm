# PART 11 — KNOWLEDGE GRAPH & EXPERT SYSTEM

> Read `00_INDEX.md` first. This is the "brain" that turns numbers into decisions.

## 11A. Sports Knowledge Graph
Connect: Player ↔ Match ↔ Stroke ↔ Spin ↔ Biomechanics ↔ Training ↔ Weakness ↔ Injury ↔ Correction ↔ Performance.

| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 11.1 | Graph schema + ontology (standard TT event taxonomy) | 🔴 | L |
| 11.2 | Graph database + ingestion from all engines | 🔴 | L |
| 11.3 | Entity resolution (link to Player Passport — Part 04) | 🟠 | M |
| 11.4 | Temporal graph (evolution over a career) | 🟠 | L |

## 11B. Sports Knowledge Engine (expert / causal)
Answer: Why did the player fail? What caused the mistake? How to correct it? Which drill fixes it? How long will improvement take? How should training change?

| # | Component | Priority | Complexity |
|---|-----------|----------|-----------|
| 11.5 | **Causal reasoning engine** (root-cause of errors) | 🔴 | XL |
| 11.6 | Drill-recommendation reasoner (weakness → drill) | 🟠 | L |
| 11.7 | Improvement-time estimator | 🟡 | L |
| 11.8 | **Curated expert knowledge base** (world-class coaches) | 🔴 | L |
| 11.9 | Evidence base — every recommendation cites sports-science source | 🟠 | M |
| 11.10 | Methodology variants (national schools) as selectable models | 🟡 | M |
| 11.11 | Knowledge CMS + versioning (coach-authored content) | 🟡 | M |
| 11.12 | **Natural-language Q&A** over the graph (coach/athlete level) | 🟠 | L |
| 11.13 | Coach-correction feedback loop → knowledge/model update | 🔴 | L |

## Design note
The expert system reads from the Knowledge Graph and the Reliability layer (Part 10), so its answers are themselves confidence-tagged and cite evidence. LLM-based reasoning must be grounded in the graph (no ungrounded claims) — see Part 16 for validity requirements.

---

➡️ **NEXT FILE: `12_DATA_AND_ML_INFRA.md`**
