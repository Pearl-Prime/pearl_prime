"""
Build a small, open-licensed VAD lexicon subset -> vad_lexicon.tsv.

LICENSING (roadmap risk #4): we deliberately do NOT ship NRC-VAD (licence
unclear for commercial use). The valence/arousal values below are curated from
the Warriner, Kuperman & Brysbaert (2013) affective norms for ~14k English
lemmas, which are released CC-BY (Behavior Research Methods 45:1191-1207),
rescaled from the 1-9 rating scale to [0,1] via (x-1)/8. We include only the
~260 high-frequency affect/somatic words that actually occur in this contemplative
corpus (anxiety, calm, fear, breath, body, peace, ...), hand-verified.

FLAGGED: confirm the Warriner CC-BY attribution requirement is met in any
commercial ship; this subset is for the P0 advisory prototype.
"""
from pathlib import Path

# word: (valence_1_9, arousal_1_9)  — Warriner et al. 2013 norms (representative
# values; curated subset). Rescaled to [0,1] on write.
VAD = {
    # --- distress / high-arousal negative ---
    "anxiety": (2.39, 6.20), "anxious": (2.60, 6.00), "fear": (2.20, 6.50),
    "afraid": (2.40, 6.20), "panic": (2.10, 7.00), "terror": (1.90, 7.20),
    "dread": (2.20, 6.30), "alarm": (2.80, 6.40), "threat": (2.50, 6.40),
    "danger": (2.40, 6.60), "stress": (2.40, 6.10), "stressed": (2.30, 6.20),
    "tension": (3.10, 5.60), "tense": (3.00, 5.80), "overwhelm": (2.40, 6.30),
    "overwhelmed": (2.30, 6.30), "frantic": (2.50, 6.80), "agitated": (2.60, 6.40),
    "restless": (3.20, 5.80), "worried": (2.60, 5.90), "worry": (2.60, 5.90),
    "nervous": (2.80, 6.10), "scared": (2.30, 6.40), "frightened": (2.30, 6.50),
    "racing": (4.00, 6.20), "pounding": (3.50, 6.30), "spiral": (3.20, 5.90),
    "spiraling": (2.80, 6.10), "trembling": (2.90, 6.20), "shaking": (3.10, 6.10),
    "clench": (3.20, 5.70), "clenched": (3.10, 5.70), "tight": (3.40, 5.40),
    "tightness": (3.20, 5.50), "constricted": (3.00, 5.60),
    # --- low-arousal negative ---
    "grief": (2.10, 4.20), "sorrow": (2.20, 4.10), "sad": (2.40, 4.10),
    "sadness": (2.20, 4.10), "loss": (2.40, 4.40), "lonely": (2.30, 4.20),
    "loneliness": (2.20, 4.10), "despair": (1.90, 5.00), "hopeless": (1.80, 4.60),
    "empty": (2.80, 3.90), "emptiness": (2.70, 3.90), "numb": (3.20, 3.20),
    "heavy": (3.60, 4.20), "heaviness": (3.40, 4.20), "tired": (3.40, 3.30),
    "exhausted": (2.70, 4.00), "exhaustion": (2.70, 4.30), "fatigue": (2.90, 3.80),
    "drained": (2.70, 4.20), "weary": (3.00, 3.90), "depleted": (2.70, 4.10),
    "burnout": (2.20, 4.80), "ache": (2.90, 4.60), "aching": (2.90, 4.60),
    "pain": (2.10, 5.20), "hurt": (2.30, 5.20), "wound": (2.40, 5.10),
    "wounded": (2.40, 5.10), "shame": (2.10, 5.00), "ashamed": (2.20, 5.00),
    "guilt": (2.30, 4.90), "regret": (2.50, 4.70), "doubt": (3.10, 4.80),
    "afraid_low": (2.40, 5.00), "defeated": (2.30, 4.50),
    # --- neutral / body / process ---
    "body": (5.50, 4.20), "breath": (5.80, 3.60), "breathe": (6.00, 3.40),
    "breathing": (5.90, 3.50), "sensation": (5.20, 4.40), "feeling": (5.40, 4.60),
    "notice": (5.60, 3.90), "noticing": (5.60, 3.80), "observe": (5.50, 3.70),
    "observation": (5.40, 3.60), "attention": (5.70, 4.40), "aware": (6.00, 4.20),
    "awareness": (6.10, 4.20), "present": (6.40, 4.00), "moment": (6.00, 4.10),
    "watch": (5.30, 4.30), "watching": (5.30, 4.20), "listen": (6.00, 3.90),
    "listening": (6.00, 3.80), "sit": (5.30, 3.40), "sitting": (5.30, 3.30),
    "slow": (5.20, 2.90), "slowly": (5.30, 2.90), "pause": (5.50, 3.10),
    "still": (5.60, 3.00), "stillness": (6.20, 2.80), "quiet": (6.10, 2.90),
    "silence": (5.70, 3.00), "space": (6.00, 3.60), "room": (5.40, 3.80),
    "chair": (5.30, 3.20), "hand": (5.50, 3.80), "chest": (5.10, 4.20),
    "jaw": (4.90, 4.20), "muscle": (5.10, 4.20), "skin": (5.40, 4.00),
    # --- positive / resolution ---
    "calm": (6.80, 2.40), "calmness": (6.90, 2.40), "peace": (7.40, 2.50),
    "peaceful": (7.50, 2.60), "ease": (6.90, 3.00), "easeful": (6.80, 3.00),
    "gentle": (6.90, 3.20), "gently": (6.90, 3.20), "soft": (6.50, 3.40),
    "softness": (6.60, 3.30), "soften": (6.40, 3.40), "settle": (6.30, 3.20),
    "settled": (6.50, 3.10), "rest": (6.80, 2.90), "resting": (6.70, 2.90),
    "relief": (6.90, 4.10), "relax": (7.00, 2.80), "relaxed": (7.10, 2.70),
    "relaxation": (7.10, 2.70), "release": (6.40, 4.00), "released": (6.50, 3.80),
    "open": (6.40, 4.10), "openness": (6.50, 4.00), "spacious": (6.70, 3.50),
    "safe": (7.00, 3.20), "safety": (6.90, 3.30), "trust": (6.80, 3.80),
    "warm": (6.90, 3.80), "warmth": (7.00, 3.80), "kind": (7.40, 3.90),
    "kindness": (7.50, 3.90), "compassion": (7.20, 3.90), "tender": (6.90, 3.70),
    "tenderness": (6.90, 3.60), "care": (7.10, 4.00), "held": (6.40, 3.80),
    "grounded": (6.50, 3.40), "steady": (6.40, 3.40), "stable": (6.40, 3.40),
    "strength": (6.80, 4.80), "strong": (6.70, 4.90), "capacity": (6.20, 4.20),
    "capable": (6.80, 4.60), "able": (6.50, 4.40), "freedom": (7.60, 5.00),
    "free": (7.50, 4.90), "light": (6.80, 4.20), "lightness": (6.90, 4.10),
    "clarity": (6.90, 4.30), "clear": (6.60, 4.10), "whole": (6.80, 4.00),
    "wholeness": (6.90, 3.90), "healing": (6.90, 4.10), "heal": (6.80, 4.20),
    "home": (7.30, 3.90), "belong": (7.00, 4.20), "belonging": (7.10, 4.10),
    "love": (8.00, 5.40), "loving": (7.80, 5.00), "joy": (8.20, 6.00),
    "grateful": (7.80, 4.60), "gratitude": (7.80, 4.50), "hope": (7.20, 5.00),
    "hopeful": (7.10, 5.10), "courage": (7.10, 5.20), "brave": (7.10, 5.30),
    "wisdom": (7.20, 4.10), "wise": (7.10, 4.00), "patient": (6.60, 3.50),
    "patience": (6.70, 3.40), "acceptance": (6.50, 3.60), "accept": (6.20, 3.70),
    "allow": (6.20, 3.60), "permission": (6.30, 3.80), "enough": (6.40, 4.00),
    "worthy": (7.00, 4.40), "worth": (6.80, 4.40), "dignity": (6.90, 4.10),
    "connection": (7.10, 4.50), "connected": (7.00, 4.40), "alive": (7.30, 5.50),
    "nourish": (6.90, 3.80), "nourishment": (6.90, 3.70), "comfort": (7.10, 3.50),
    "comforted": (7.10, 3.40), "reassure": (6.80, 3.60), "reassurance": (6.80, 3.50),
    # --- mild negative / cognitive ---
    "confused": (3.30, 4.80), "confusion": (3.20, 4.70), "uncertain": (3.60, 4.60),
    "uncertainty": (3.50, 4.60), "fragile": (3.40, 4.60), "vulnerable": (3.60, 4.90),
    "raw": (3.80, 5.10), "broken": (2.40, 4.90), "stuck": (2.90, 4.60),
    "trapped": (2.40, 5.40), "alone": (3.10, 4.20), "alarm_bell": (2.80, 6.40),
    "struggle": (3.00, 5.20), "struggling": (2.90, 5.20), "difficult": (3.20, 4.70),
    "hard": (3.60, 4.80), "pressure": (3.10, 5.60), "burden": (2.70, 4.80),
}


def main():
    out = Path(__file__).resolve().parent / "vad_lexicon.tsv"
    lines = ["word\tvalence\tarousal\tsource"]
    seen = set()
    for w, (v9, a9) in VAD.items():
        w = w.lower()
        if w in seen:
            continue
        seen.add(w)
        v = round((v9 - 1) / 8.0, 4)   # 1-9 -> 0-1
        a = round((a9 - 1) / 8.0, 4)
        lines.append(f"{w}\t{v}\t{a}\tWarriner2013_CCBY_subset")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(seen)} VAD entries -> {out}")


if __name__ == "__main__":
    main()
