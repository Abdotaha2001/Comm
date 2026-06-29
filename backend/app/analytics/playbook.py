"""How-to-beat-each-style playbook — distilled from MASTER_SPEC Part 21.

Keyed by the opponent's style_class (Part 19 B8 / Part 28). Generic fallback
applies when the style is unknown.
"""

PLAYBOOK = {
    "chopper": {
        "serve": ["Vary heavy backspin with no-spin; avoid predictable depth"],
        "receive": ["Open with a low spinny loop, then change pace"],
        "rally": ["Alternate heavy loops with soft/no-spin; avoid medium pace",
                  "Bring them in with a drop shot, then attack with placement"],
        "placement": ["Attack wide angles and change pace"],
    },
    "short_pips_hitter": {
        "serve": ["Avoid short-into-short; serve deep with spin"],
        "receive": ["Take them away from the table early"],
        "rally": ["Use heavy spin and wide angles to push them back off the table"],
        "placement": ["Deep, wide, heavy-spin balls"],
    },
    "combination_chopper": {  # long pips / anti
        "serve": ["DO NOT serve sidespin to the pips; use topspin/backspin, vary placement"],
        "receive": ["Read the returned ball (spin reversal), not your own stroke"],
        "rally": ["Loop with less spin; sometimes give no spin/pace",
                  "Long backspin serve to the pips side, then attack the weak return"],
        "placement": ["Attack only after forcing a weak return"],
    },
    "fh_looper": {
        "serve": ["Serve to the wide backhand / crossover to limit the forehand"],
        "receive": ["Take time away with quick blocks"],
        "rally": ["Target the crossover (elbow); don't feed clean topspin to the FH"],
        "placement": ["Crossover (elbow) and wide backhand"],
    },
    "two_winged_attacker": {
        "serve": ["Mix short and sudden-long; deny the opening"],
        "receive": ["Banana-flick short serves; rush their setup"],
        "rally": ["Hit the crossover (elbow); change angle and rhythm"],
        "placement": ["Crossover (elbow)"],
    },
    "penhold_looper": {
        "serve": ["Pressure the backhand / transition point"],
        "receive": ["Attack the wide backhand"],
        "rally": ["Target the BH and the RPB switch point; rush transitions"],
        "placement": ["Wide backhand and the switch point"],
    },
    "penhold_rpb": {
        "serve": ["Pressure the RPB↔FH switch point"],
        "receive": ["Rush the transition"],
        "rally": ["Target the crossover and the switch point"],
        "placement": ["Crossover / switch point"],
    },
    "counter_driver": {
        "serve": ["Use spin variation to deny a clean block"],
        "receive": ["Open with spin to disrupt the block rhythm"],
        "rally": ["Change pace and spin; avoid feeding flat speed they can redirect"],
        "placement": ["Wide angles and the crossover"],
    },
    "all_rounder": {
        "serve": ["Vary serve spin and placement; avoid patterns"],
        "receive": ["Mix push, flick and control to deny rhythm"],
        "rally": ["Probe both wings and the crossover; impose your strength"],
        "placement": ["Crossover (elbow) and wide angles"],
    },
}

GENERIC = PLAYBOOK["all_rounder"]


def for_style(style_class: str) -> dict:
    return PLAYBOOK.get(style_class or "", GENERIC)
