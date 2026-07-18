"""Smoke test: verify article structure restructure 2026-05-17.

Operator directive:
  1) Start with news summary (~200 words).
  2) Section header "This is how it affects Gen Z and Gen Alpha" (localized).
  3) Two felt-experience atoms (hook_personal + youth_somatic).
  4) Then teacher_intro / witness / evidence / etc.
"""
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from pearl_news.pipeline.assemble_v52 import assemble_v52

NEWS_PEG = (
    "On May 14 2026, UNICEF released the Global Coalition for Youth Mental"
    " Health report covering 5,600 respondents aged 14-25 across seven"
    " countries. The findings show 6 in 10 say they are overwhelmed more"
    " days than not."
    "\n\n"
    "The driver: WHO/Europe adopted the Child and Adolescent Health Strategy"
    " 2026-2030 in October 2025, which set a binding 2030 reporting deadline"
    " on adolescent mental load. The May report is the first to land under it."
    "\n\n"
    "Across 2024 and 2025, country-level surveys reported similar pressure,"
    " but this is the first multilateral report to consolidate the cohort."
)

TEACHER_INTRO = "Teacher Ahjan has watched this rise for two years."
HOOK_PERSONAL = "You wake before the alarm. The screen lights up the dark."
YOUTH_SOMATIC = (
    "Loop sequence: jaw tightens, breath shortens, shoulders rise, eyes pin."
    " It is not in your head."
)

slots = {
    "headline_layer_1": "Youth Mental Overload Keeps Rising",
    "headline_layer_2": "What 5,600 voices tell us about the load",
    "hook_personal": HOOK_PERSONAL,
    "hook_big_picture": "",
    "news_peg": NEWS_PEG,
    "teacher_intro": TEACHER_INTRO,
    "youth_somatic": YOUTH_SOMATIC,
    "teacher_witness": "Teacher Ahjan sees this pattern in young clients.",
    "body_data": "WHO/Europe data points to a 6-in-10 ratio.",
    "turnaround": "First paragraph of turnaround.\n\nSecond paragraph.",
    "bridge": "Bridge connector paragraph.",
    "teacher_perspective": "Teaching paragraph one.\n\nTeaching paragraph two.",
    "practice_announce": "Practice announcement.\n\nShift sentence here.",
    "forward_look": "Forward paragraph one.\n\nTake action paragraph two.",
    "sdg_un_tie": "SDG 3 — Good Health and Well-Being.",
}

ARTICLE = {
    "slots": slots,
    "teacher": "ahjan",
    "topic": "mental_health",
    "sdg": "3",
    "template": "hard_news_spiritual_response",
}

EXPECTED = {
    "en": {
        "news_label": "News Summary",
        "felt_label": "This is how it affects Gen Z and Gen Alpha",
    },
    "ja": {
        "news_label": "ニュース要約",
        "felt_label": "Z世代とα世代にはこう響く",
    },
    "zh-cn": {
        "news_label": "新闻摘要",
        "felt_label": "这对Z世代和α世代意味着什么",
    },
}
COMMON = {
    "intro_marker": "Teacher Ahjan has watched this",
    "youth_marker": "jaw tightens",
    "hook_marker": "wake before the alarm",
    "news_para": "UNICEF released the Global Coalition",
}

print("=" * 78)
print("Article Structure Smoke Test (operator restructure 2026-05-17)")
print("=" * 78)

all_pass = True
for lang, markers in EXPECTED.items():
    meta = {"language": lang}
    html = assemble_v52(ARTICLE, meta, standalone=False)

    p_news = html.find(markers["news_label"])
    p_felt = html.find(markers["felt_label"])
    p_intro = html.find(COMMON["intro_marker"])
    p_youth = html.find(COMMON["youth_marker"])
    p_hook = html.find(COMMON["hook_marker"])
    p_news_para = html.find(COMMON["news_para"])

    issues = []
    if p_news < 0: issues.append(f"news label '{markers['news_label']}' missing")
    if p_felt < 0: issues.append(f"felt label '{markers['felt_label']}' missing")
    if p_intro < 0: issues.append("teacher_intro missing")
    if p_youth < 0: issues.append("youth_somatic missing")
    if p_hook < 0: issues.append("hook_personal missing")
    if p_news_para < 0: issues.append("news para 1 (UNICEF) missing")

    if not issues:
        if not (p_news < p_news_para):
            issues.append(f"news label NOT before news para ({p_news} >= {p_news_para})")
        if not (p_news_para < p_felt):
            issues.append(f"news para NOT before felt label ({p_news_para} >= {p_felt})")
        if not (p_felt < p_hook):
            issues.append(f"felt label NOT before hook ({p_felt} >= {p_hook})")
        if not (p_hook < p_youth):
            issues.append(f"hook NOT before youth ({p_hook} >= {p_youth})")
        if not (p_youth < p_intro):
            issues.append(f"youth NOT before intro ({p_youth} >= {p_intro})")

    print(f"\n[{lang}]")
    if not issues:
        print(f"  PASS  news({p_news}) < news_para({p_news_para}) < felt({p_felt}) "
              f"< hook({p_hook}) < youth({p_youth}) < intro({p_intro})")
    else:
        for s in issues:
            print(f"  FAIL  {s}")
        all_pass = False
        if p_felt >= 0:
            print(f"\n  --- HTML around felt header (pos {p_felt}) ---")
            print(html[max(0, p_felt - 200):p_felt + 500])
            print("  ---")

print("\n" + "=" * 78)
if all_pass:
    print("ALL 3 LANGUAGES PASS — structure restructure verified.")
    sys.exit(0)
else:
    print("STRUCTURE TEST FAILED — see above.")
    sys.exit(1)
