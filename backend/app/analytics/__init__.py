"""Rule-based intelligence layer (grounded in MASTER_SPEC Parts 07, 21, 22).

profile.aggregate_profile  → player style/strengths/weaknesses from analysis data
opponent.build_dossier     → opponent profile + style
matchup.build_matchup      → style-vs-style edge + predicted win probability
gameplan.generate_plan     → "how to beat them" plan + training block (Part 21 playbook)

Every output is confidence-tagged; thin data yields a 'preliminary' note rather
than a confident guess (Part 10). A grounded LLM (Part 11) can replace these
generators later behind the same interface.
"""
