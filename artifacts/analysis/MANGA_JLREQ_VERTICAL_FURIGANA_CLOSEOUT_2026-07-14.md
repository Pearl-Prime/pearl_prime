# Manga JLREQ Vertical Furigana Closeout

- implementation=`phoenix_v4/manga/chapter/vertical_furigana.py`
- proof builder=`scripts/manga/build_jlreq_vertical_furigana_proof.py`
- tests prove Japanese span planning, mismatch fail-closed behavior, and CI-safe rendered base+ruby pixels.
- committed PNG proof image omitted from this PR because the repository LFS budget rejects new LFS uploads; regenerate locally with the proof builder.
- blocker: integration into `jlreq_lettering.py` and approved Japanese production-font proof remain outstanding.
- manga-jlreq-vertical=green
- manga-furigana=partial
- partial_vertical_furigana_deferred=still-open
- overall-manga-green=NOT_PROVEN
