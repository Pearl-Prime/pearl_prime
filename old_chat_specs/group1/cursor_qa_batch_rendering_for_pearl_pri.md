# QA batch rendering for Pearl Prime pipeline
_Exported on 4/16/2026 at 19:18:36 GMT+8 from Cursor (3.1.15)_

---

**User**

You are Pearl_Dev running a comprehensive QA batch of the Pearl Prime pipeline.
Your job: render one book for EVERY output format, across a spread of different
topics, personas, engines, and teachers — then concatenate all rendered text
into a single QA review file.
─── STARTUP_RECEIPT ───────────────────────────────────────────────────────
AGENT:              Pearl_Dev
TASK:               Batch-render all 10 V4 output formats across varied
                    topics/personas/engines/teachers into one QA text file
PROJECT_ID:         proj_state_convergence_20260328
SUBSYSTEM:          core_pipeline
AUTHORITY_DOCS:     docs/DOCS_INDEX.md; docs/SESSION_UNITY_PROTOCOL.md
READ_PATH_COMPLETE: yes
WRITE_SCOPE:        artifacts/qa_batch_20260416/
OUT_OF_SCOPE:       brand-wizard-app/; config/ (no edits)
BLOCKERS:           none
READY_STATUS:       ready
───────────────────────────────────────────────────────────────────────────
Read before doing anything:
  1. pearl_prime/config/v4_freeze_modular_formats.yaml (confirm 10 output formats)
  2. scripts/run_pipeline.py (confirm CLI flags still match below)
══════════════════════════════════════════════════════════════════════════
LOAD CREDENTIALS FIRST
══════════════════════════════════════════════════════════════════════════
Before any pipeline run:
```bash
eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"

══════════════════════════════════════════════════════════════════════════
THE BATCH — 30 RUNS
══════════════════════════════════════════════════════════════════════════
Create output directory:
```bash
mkdir -p artifacts/qa_batch_20260416

Run each of the following commands. Each uses:
  --pipeline-mode spine --no-job-check --render-book --no-generate-freebies
  --no-update-freebie-index --quality-profile draft
The 10 V4 output formats are:
  1. five_min_practice       (micro 15min — 350-650 words/ch)
  2. pocket_guide            (short 30min — 200-450 words/ch)  [DEFAULT]
  3. ten_things_to_do        (short 30min — 120-260 words/ch)
  4. symptom_to_action_atlas (micro 20min — 90-220 words/ch)
  5. daily_text_audio_companion (micro 20min — 140-320 words/ch)
  6. crisis_cards            (micro 15min — 90-200 words/ch)
  7. weekly_challenge_pack   (short 30min — 180-480 words/ch)
  8. faq_audiobook           (short 30min — 320-700 words/ch)
  9. myth_vs_mechanism       (short 30min — 450-900 words/ch)
  10. protocol_library       (micro 20min — 120-280 words/ch)
For each format, run 3 books (= 30 total), each with a DIFFERENT persona,
topic, engine, and (where applicable) teacher. This ensures maximum variety.
Here is the exact run matrix. Pick arcs that EXIST in
config/source_of_truth/master_arcs/ — verify each arc file exists before
running. If an arc doesn't exist, substitute the closest match from the
same persona+topic.
──────────────────────────────────────────────────────────────────────────
FORMAT 1: five_min_practice (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 01:
python3 scripts/run_pipeline.py \
  --topic anxiety --persona nyc_executives \
  --arc config/source_of_truth/master_arcs/nyc_executives__anxiety__watcher__F006.yaml \
  --output-format five_min_practice --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/01_five_min_practice_anxiety_nyc
RUN 02:
python3 scripts/run_pipeline.py \
  --topic burnout --persona healthcare_rns \
  --arc config/source_of_truth/master_arcs/healthcare_rns__burnout__overwhelm__F006.yaml \
  --output-format five_min_practice --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher adi_da \
  --render-dir artifacts/qa_batch_20260416/02_five_min_practice_burnout_healthcare
RUN 03:
python3 scripts/run_pipeline.py \
  --topic self_worth --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__self_worth__shame__F006.yaml \
  --output-format five_min_practice --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --frame spiritual_first \
  --render-dir artifacts/qa_batch_20260416/03_five_min_practice_selfworth_genz
──────────────────────────────────────────────────────────────────────────
FORMAT 2: pocket_guide (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 04:
python3 scripts/run_pipeline.py \
  --topic depression --persona working_parents \
  --arc config/source_of_truth/master_arcs/working_parents__depression__grief__F006.yaml \
  --output-format pocket_guide --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/04_pocket_guide_depression_parents
RUN 05:
python3 scripts/run_pipeline.py \
  --topic boundaries --persona corporate_managers \
  --arc config/source_of_truth/master_arcs/corporate_managers__boundaries__comparison__F006.yaml \
  --output-format pocket_guide --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher ahjan \
  --render-dir artifacts/qa_batch_20260416/05_pocket_guide_boundaries_corporate
RUN 06:
python3 scripts/run_pipeline.py \
  --topic grief --persona millennial_women_professionals \
  --arc config/source_of_truth/master_arcs/millennial_women_professionals__grief__grief__F006.yaml \
  --output-format pocket_guide --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/06_pocket_guide_grief_millennial
──────────────────────────────────────────────────────────────────────────
FORMAT 3: ten_things_to_do (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 07:
python3 scripts/run_pipeline.py \
  --topic overthinking --persona educators \
  --arc config/source_of_truth/master_arcs/educators__overthinking__spiral__F006.yaml \
  --output-format ten_things_to_do --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/07_ten_things_overthinking_educators
RUN 08:
python3 scripts/run_pipeline.py \
  --topic imposter_syndrome --persona tech_finance_burnout \
  --arc config/source_of_truth/master_arcs/tech_finance_burnout__imposter_syndrome__shame__F006.yaml \
  --output-format ten_things_to_do --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher sai_ma \
  --render-dir artifacts/qa_batch_20260416/08_ten_things_imposter_techfin
RUN 09:
python3 scripts/run_pipeline.py \
  --topic social_anxiety --persona gen_z_student \
  --arc config/source_of_truth/master_arcs/gen_z_student__social_anxiety__false_alarm__F006.yaml \
  --output-format ten_things_to_do --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/09_ten_things_socialanx_genzstudent
──────────────────────────────────────────────────────────────────────────
FORMAT 4: symptom_to_action_atlas (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 10:
python3 scripts/run_pipeline.py \
  --topic compassion_fatigue --persona first_responders \
  --arc config/source_of_truth/master_arcs/first_responders__compassion_fatigue__watcher__F006.yaml \
  --output-format symptom_to_action_atlas --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/10_symptom_atlas_compfatigue_firstresponders
RUN 11:
python3 scripts/run_pipeline.py \
  --topic financial_anxiety --persona entrepreneurs \
  --arc config/source_of_truth/master_arcs/entrepreneurs__financial_anxiety__spiral__F006.yaml \
  --output-format symptom_to_action_atlas --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher master_wu \
  --render-dir artifacts/qa_batch_20260416/11_symptom_atlas_finanx_entrepreneurs
RUN 12:
python3 scripts/run_pipeline.py \
  --topic sleep_anxiety --persona midlife_women \
  --arc config/source_of_truth/master_arcs/midlife_women__sleep_anxiety__false_alarm__F006.yaml \
  --output-format symptom_to_action_atlas --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/12_symptom_atlas_sleepanx_midlife
──────────────────────────────────────────────────────────────────────────
FORMAT 5: daily_text_audio_companion (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 13:
python3 scripts/run_pipeline.py \
  --topic courage --persona gen_x_sandwich \
  --arc config/source_of_truth/master_arcs/gen_x_sandwich__courage__false_alarm__F006.yaml \
  --output-format daily_text_audio_companion --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/13_daily_companion_courage_genx
RUN 14:
python3 scripts/run_pipeline.py \
  --topic financial_stress --persona corporate_managers \
  --arc config/source_of_truth/master_arcs/corporate_managers__financial_stress__overwhelm__F006.yaml \
  --output-format daily_text_audio_companion --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher ra \
  --render-dir artifacts/qa_batch_20260416/14_daily_companion_finstress_corporate
RUN 15:
python3 scripts/run_pipeline.py \
  --topic somatic_healing --persona healthcare_rns \
  --arc config/source_of_truth/master_arcs/healthcare_rns__somatic_healing__watcher__F006.yaml \
  --output-format daily_text_audio_companion --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/15_daily_companion_somatic_healthcare
──────────────────────────────────────────────────────────────────────────
FORMAT 6: crisis_cards (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 16:
python3 scripts/run_pipeline.py \
  --topic anxiety --persona working_parents \
  --arc config/source_of_truth/master_arcs/working_parents__anxiety__false_alarm__F006.yaml \
  --output-format crisis_cards --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/16_crisis_cards_anxiety_parents
RUN 17:
python3 scripts/run_pipeline.py \
  --topic burnout --persona educators \
  --arc config/source_of_truth/master_arcs/educators__burnout__overwhelm__F006.yaml \
  --output-format crisis_cards --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher joshin \
  --render-dir artifacts/qa_batch_20260416/17_crisis_cards_burnout_educators
RUN 18:
python3 scripts/run_pipeline.py \
  --topic depression --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__depression__watcher__F006.yaml \
  --output-format crisis_cards --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/18_crisis_cards_depression_genz
──────────────────────────────────────────────────────────────────────────
FORMAT 7: weekly_challenge_pack (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 19:
python3 scripts/run_pipeline.py \
  --topic self_worth --persona millennial_women_professionals \
  --arc config/source_of_truth/master_arcs/millennial_women_professionals__self_worth__comparison__F006.yaml \
  --output-format weekly_challenge_pack --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/19_weekly_challenge_selfworth_millennial
RUN 20:
python3 scripts/run_pipeline.py \
  --topic boundaries --persona first_responders \
  --arc config/source_of_truth/master_arcs/first_responders__boundaries__shame__F006.yaml \
  --output-format weekly_challenge_pack --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher master_feung \
  --render-dir artifacts/qa_batch_20260416/20_weekly_challenge_boundaries_firstresponders
RUN 21:
python3 scripts/run_pipeline.py \
  --topic overthinking --persona tech_finance_burnout \
  --arc config/source_of_truth/master_arcs/tech_finance_burnout__overthinking__spiral__F006.yaml \
  --output-format weekly_challenge_pack --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --frame spiritual_first \
  --render-dir artifacts/qa_batch_20260416/21_weekly_challenge_overthinking_techfin
──────────────────────────────────────────────────────────────────────────
FORMAT 8: faq_audiobook (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 22:
python3 scripts/run_pipeline.py \
  --topic imposter_syndrome --persona entrepreneurs \
  --arc config/source_of_truth/master_arcs/entrepreneurs__imposter_syndrome__comparison__F006.yaml \
  --output-format faq_audiobook --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/22_faq_audiobook_imposter_entrepreneurs
RUN 23:
python3 scripts/run_pipeline.py \
  --topic grief --persona gen_x_sandwich \
  --arc config/source_of_truth/master_arcs/gen_x_sandwich__grief__grief__F006.yaml \
  --output-format faq_audiobook --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher miki \
  --render-dir artifacts/qa_batch_20260416/23_faq_audiobook_grief_genx
RUN 24:
python3 scripts/run_pipeline.py \
  --topic anxiety --persona gen_alpha_students \
  --arc config/source_of_truth/master_arcs/gen_alpha_students__anxiety__false_alarm__F006.yaml \
  --output-format faq_audiobook --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/24_faq_audiobook_anxiety_genalpha
──────────────────────────────────────────────────────────────────────────
FORMAT 9: myth_vs_mechanism (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 25:
python3 scripts/run_pipeline.py \
  --topic social_anxiety --persona nyc_executives \
  --arc config/source_of_truth/master_arcs/nyc_executives__social_anxiety__false_alarm__F006.yaml \
  --output-format myth_vs_mechanism --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/25_myth_mechanism_socialanx_nyc
RUN 26:
python3 scripts/run_pipeline.py \
  --topic compassion_fatigue --persona healthcare_rns \
  --arc config/source_of_truth/master_arcs/healthcare_rns__compassion_fatigue__overwhelm__F006.yaml \
  --output-format myth_vs_mechanism --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher master_sha \
  --render-dir artifacts/qa_batch_20260416/26_myth_mechanism_compfatigue_healthcare
RUN 27:
python3 scripts/run_pipeline.py \
  --topic courage --persona educators \
  --arc config/source_of_truth/master_arcs/educators__courage__shame__F006.yaml \
  --output-format myth_vs_mechanism --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/27_myth_mechanism_courage_educators
──────────────────────────────────────────────────────────────────────────
FORMAT 10: protocol_library (3 runs)
──────────────────────────────────────────────────────────────────────────
RUN 28:
python3 scripts/run_pipeline.py \
  --topic burnout --persona millennial_women_professionals \
  --arc config/source_of_truth/master_arcs/millennial_women_professionals__burnout__watcher__F006.yaml \
  --output-format protocol_library --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/28_protocol_library_burnout_millennial
RUN 29:
python3 scripts/run_pipeline.py \
  --topic financial_anxiety --persona working_parents \
  --arc config/source_of_truth/master_arcs/working_parents__financial_anxiety__overwhelm__F006.yaml \
  --output-format protocol_library --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft --teacher junko \
  --render-dir artifacts/qa_batch_20260416/29_protocol_library_finanx_parents
RUN 30:
python3 scripts/run_pipeline.py \
  --topic sleep_anxiety --persona gen_z_student \
  --arc config/source_of_truth/master_arcs/gen_z_student__sleep_anxiety__watcher__F006.yaml \
  --output-format protocol_library --pipeline-mode spine --no-job-check \
  --render-book --no-generate-freebies --no-update-freebie-index \
  --quality-profile draft \
  --render-dir artifacts/qa_batch_20260416/30_protocol_library_sleepanx_genzstudent
══════════════════════════════════════════════════════════════════════════
ARC EXISTENCE CHECK — DO THIS FIRST
══════════════════════════════════════════════════════════════════════════
Before running ANY of the above, verify every arc file exists:
```bash
for arc in
nyc_executives__anxiety__watcher__F006
healthcare_rns__burnout__overwhelm__F006
gen_z_professionals__self_worth__shame__F006
working_parents__depression__grief__F006
corporate_managers__boundaries__comparison__F006
millennial_women_professionals__grief__grief__F006
educators__overthinking__spiral__F006
tech_finance_burnout__imposter_syndrome__shame__F006
gen_z_student__social_anxiety__false_alarm__F006
first_responders__compassion_fatigue__watcher__F006
entrepreneurs__financial_anxiety__spiral__F006
midlife_women__sleep_anxiety__false_alarm__F006
gen_x_sandwich__courage__false_alarm__F006
corporate_managers__financial_stress__overwhelm__F006
healthcare_rns__somatic_healing__watcher__F006
working_parents__anxiety__false_alarm__F006
educators__burnout__overwhelm__F006
gen_z_professionals__depression__watcher__F006
millennial_women_professionals__self_worth__comparison__F006
first_responders__boundaries__shame__F006
tech_finance_burnout__overthinking__spiral__F006
entrepreneurs__imposter_syndrome__comparison__F006
gen_x_sandwich__grief__grief__F006
gen_alpha_students__anxiety__false_alarm__F006
nyc_executives__social_anxiety__false_alarm__F006
healthcare_rns__compassion_fatigue__overwhelm__F006
educators__courage__shame__F006
millennial_women_professionals__burnout__watcher__F006
working_parents__financial_anxiety__overwhelm__F006
gen_z_student__sleep_anxiety__watcher__F006; do
f="config/source_of_truth/master_arcs/${arc}.yaml"
if [ ! -f "$f" ]; then
echo "MISSING: $f"
fi
done

For any MISSING arc, find the closest substitute from the same persona+topic:
```bash
ls config/source_of_truth/master_arcs/<persona><topic>*.yaml

Update the run command to use the substitute. Document every substitution.
══════════════════════════════════════════════════════════════════════════
ERROR HANDLING
══════════════════════════════════════════════════════════════════════════
- If a run fails, log the error to artifacts/qa_batch_20260416/ERRORS.txt
  with the run number, command, and error message. Continue to the next run.
- If more than 10 runs fail, STOP and report the pattern. Something
  systemic is wrong.
- Use --quality-profile draft so quality gate failures become warnings,
  not blockers.
- If a run hangs for more than 5 minutes, kill it and log as timeout.
══════════════════════════════════════════════════════════════════════════
CONCATENATION — THE FINAL QA FILE
══════════════════════════════════════════════════════════════════════════
After all 30 runs complete (or as many as succeeded), concatenate all
rendered text into ONE file:
```bash
echo "" > artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt

for dir in artifacts/qa_batch_20260416/*/; do
run_name=$(basename "$dir")
echo "" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
echo "═══════════════════════════════════════════════════════════════" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
echo "RUN: $run_name" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
echo "═══════════════════════════════════════════════════════════════" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
echo "" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt

Find all .txt files in the render dir and concat them
find "$dir" -name "*.txt" -type f | sort | while read f; do
echo "--- $(basename "$f") ---" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
cat "$f" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
echo "" >> artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
done
done

Also create a summary header at the top of the file:
PEARL PRIME QA BATCH — 2026-04-16
══════════════════════════════════
30 books across 10 output formats
13 personas × 15 topics × 7 engines × 6 teachers
Quality profile: draft (warnings, not blocks)

FORMAT COVERAGE:
✓ five_min_practice (runs 01-03)
✓ pocket_guide (runs 04-06)
✓ ten_things_to_do (runs 07-09)
✓ symptom_to_action_atlas (runs 10-12)
✓ daily_text_audio_companion (runs 13-15)
✓ crisis_cards (runs 16-18)
✓ weekly_challenge_pack (runs 19-21)
✓ faq_audiobook (runs 22-24)
✓ myth_vs_mechanism (runs 25-27)
✓ protocol_library (runs 28-30)

PERSONA COVERAGE: [list which personas were used]
TOPIC COVERAGE: [list which topics were used]
ENGINE COVERAGE: [list which engines were used]
TEACHER COVERAGE: [list which teachers were used, including "none" for non-teacher runs]
FRAME COVERAGE: somatic_first (default) + spiritual_first (runs 03, 21)

ERRORS: [count] runs failed — see ERRORS.txt
ARC SUBSTITUTIONS: [list any arcs that were substituted]

══════════════════════════════════════════════════════════════════════════
DELIVER
══════════════════════════════════════════════════════════════════════════
The final deliverable is:
  artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
Report its word count and line count when done:
```bash
wc -w -l artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt

No commit needed — this is a QA artifact, not a code change.
Print the full path to the file as your final output.
══════════════════════════════════════════════════════════════════════════
CLOSEOUT_RECEIPT REQUIREMENTS
══════════════════════════════════════════════════════════════════════════
CLOSEOUT_RECEIPT must include:
- RUNS_ATTEMPTED: 30
- RUNS_SUCCEEDED: N/30
- RUNS_FAILED: N/30 (with run numbers)
- ARC_SUBSTITUTIONS: list any
- OUTPUT_FILE: artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt
- WORD_COUNT: total words
- LINE_COUNT: total lines
- FORMATS_COVERED: 10/10 (or N/10 if some failed entirely)
- PERSONAS_USED: list
- TOPICS_USED: list
- ENGINES_USED: list
- TEACHERS_USED: list
- ERRORS_SUMMARY: brief description of failure patterns, if any



---

**Cursor**

Starting the QA batch now. I’ll first verify the required config/CLI surfaces and arc availability, then run all 30 renders with timeout/error logging and produce the consolidated QA file plus counts.

I’ve confirmed the 10 output formats and CLI flags. Next I’m running an arc existence check and then launching an automated 30-run driver with per-run timeout/error logging and final concatenation.

I found 7 missing arcs; only one has an exact same persona+topic replacement. I’m proceeding with closest substitutions (prioritizing same persona where possible), documenting each in the final header and `ERRORS.txt` if any run still fails. Launching the full 30-run batch now with 5-minute per-run timeout.

The batch driver is running in the background with 5-minute timeouts per run; I’m monitoring live progress and will report success/failure totals plus counts as soon as it finishes.

The batch hit a systemic failure pattern immediately (first 11/11 failed), so the safeguard stopped execution as requested. I’m now extracting the exact error cause and then I’ll report the receipt details and artifact path/counts.

CLOSEOUT_RECEIPT

- RUNS_ATTEMPTED: 30 (requested matrix)
- RUNS_SUCCEEDED: 0/30
- RUNS_FAILED: 11/30 executed then halted (run numbers: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11)
- ARC_SUBSTITUTIONS:
  - Run 01: `config/source_of_truth/master_arcs/nyc_executives__anxiety__watcher__F006.yaml` -> `config/source_of_truth/master_arcs/nyc_executives__anxiety__spiral__F015.yaml`
  - Run 07: `config/source_of_truth/master_arcs/educators__overthinking__spiral__F006.yaml` -> `config/source_of_truth/master_arcs/educators__anxiety__overwhelm__F006.yaml`
  - Run 09: `config/source_of_truth/master_arcs/gen_z_student__social_anxiety__false_alarm__F006.yaml` -> `config/source_of_truth/master_arcs/gen_alpha_students__social_anxiety__false_alarm__F006.yaml`
- OUTPUT_FILE: `artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt`
- WORD_COUNT: 106
- LINE_COUNT: 271
- FORMATS_COVERED: 0/10
- PERSONAS_USED: `corporate_managers`, `educators`, `entrepreneurs`, `first_responders`, `gen_z_professionals`, `gen_z_student`, `healthcare_rns`, `millennial_women_professionals`, `nyc_executives`, `tech_finance_burnout`, `working_parents`
- TOPICS_USED: `anxiety`, `boundaries`, `burnout`, `compassion_fatigue`, `depression`, `financial_anxiety`, `grief`, `imposter_syndrome`, `overthinking`, `self_worth`, `social_anxiety`
- ENGINES_USED: `comparison`, `false_alarm`, `grief`, `overwhelm`, `shame`, `spiral`, `watcher`
- TEACHERS_USED: `adi_da`, `ahjan`, `master_wu`, `sai_ma`, `none`
- ERRORS_SUMMARY:
  - Systemic `Book planning layer: FAIL — No deterministic BookStructurePlan ... runtime='standard_book'` on most early runs.
  - Additional blockers: topic source readiness missing canonical atom banks, arc/format role incompatibility (missing `REFLECTION` slot), and invalid teacher-engine pairing (`master_wu` with `spiral`).
  - Per your rule, execution stopped after failures exceeded 10.

`/Users/ahjan/phoenix_omega/artifacts/qa_batch_20260416/ALL_BOOKS_QA_REVIEW.txt`

