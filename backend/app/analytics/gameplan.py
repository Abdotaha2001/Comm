"""Generate the 'how to beat them' game plan + training block.

Grounded in the Part 21 playbook keyed by the opponent's style, plus the
opponent's detected weaknesses. Confidence/data_note follow the opponent data
volume (Part 10) — thin data yields a 'preliminary' plan, never a confident guess.
"""
from .playbook import for_style


def generate_plan(my_profile: dict, dossier: dict, matchup: dict) -> dict:
    opp_style = dossier.get("style_class")
    pb = for_style(opp_style)

    exploit = []
    for w in (dossier.get("summary", {}) or {}).get("weaknesses", []) or []:
        exploit.append({
            "text": f"Exploit: {w.get('text')}",
            "evidence": w.get("evidence"),
            "confidence": w.get("confidence", "LOW"),
        })

    plan = {
        "opponent_style": opp_style or "unknown",
        "exploit": exploit,
        "serve": pb["serve"],
        "receive": pb["receive"],
        "rally": pb["rally"],
        "placement": pb["placement"],
        "pressure_points": [
            "At deuce / game points, use your highest-percentage serve + pattern."
        ],
    }
    training_block = [
        {"drill": "Multiball to the opponent's weak wing (random spin)",
         "targets": "matchup weakness", "structure": "random"},
        {"drill": "Serve + 3rd-ball attack to the crossover (elbow)",
         "targets": "serve+attack", "structure": "semi_random"},
    ]

    conf = round(matchup.get("confidence", 0.0), 3)
    note = (
        "Preliminary — limited opponent data; add footage to raise confidence."
        if conf < 0.3
        else "Plan grounded in observed tendencies."
    )
    return {"plan": plan, "training_block": training_block, "confidence": conf, "data_note": note}
