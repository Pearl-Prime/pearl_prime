#!/bin/bash
set -e
cd /Users/ahjan/phoenix_omega

echo "Running 100 Pearl Prime books..."
PASS=0; FAIL=0; TOTAL=0

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__boundaries__comparison__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_000 --out artifacts/pearl_prime_100_run/book_000.json --teacher master_wu 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  1/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  1/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__boundaries__shame__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_001 --out artifacts/pearl_prime_100_run/book_001.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  2/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  2/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__burnout__overwhelm__F003.yaml --location toronto_ca --structural-format F003 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_002 --out artifacts/pearl_prime_100_run/book_002.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  3/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  3/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__burnout__grief__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_003 --out artifacts/pearl_prime_100_run/book_003.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  4/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  4/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__anxiety__grief__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_004 --out artifacts/pearl_prime_100_run/book_004.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  5/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  5/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__overthinking__false_alarm__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_005 --out artifacts/pearl_prime_100_run/book_005.json --teacher ra 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  6/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  6/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__depression__watcher__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_006 --out artifacts/pearl_prime_100_run/book_006.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  7/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  7/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_anxiety --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__financial_anxiety__shame__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_007 --out artifacts/pearl_prime_100_run/book_007.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  8/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  8/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__boundaries__false_alarm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_008 --out artifacts/pearl_prime_100_run/book_008.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [  9/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [  9/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__anxiety__shame__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_009 --out artifacts/pearl_prime_100_run/book_009.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 10/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 10/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_stress --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__financial_stress__shame__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_010 --out artifacts/pearl_prime_100_run/book_010.json --teacher ra 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 11/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 11/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic social_anxiety --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__social_anxiety__false_alarm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_011 --out artifacts/pearl_prime_100_run/book_011.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 12/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 12/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__anxiety__shame__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_012 --out artifacts/pearl_prime_100_run/book_012.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 13/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 13/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic social_anxiety --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__social_anxiety__shame__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_013 --out artifacts/pearl_prime_100_run/book_013.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 14/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 14/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_stress --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__financial_stress__spiral__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_014 --out artifacts/pearl_prime_100_run/book_014.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 15/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 15/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__overthinking__false_alarm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_015 --out artifacts/pearl_prime_100_run/book_015.json --teacher joshin 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 16/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 16/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic compassion_fatigue --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__compassion_fatigue__overwhelm__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_016 --out artifacts/pearl_prime_100_run/book_016.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 17/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 17/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic compassion_fatigue --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__compassion_fatigue__grief__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_017 --out artifacts/pearl_prime_100_run/book_017.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 18/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 18/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona educators --arc config/source_of_truth/master_arcs/educators__anxiety__overwhelm__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_018 --out artifacts/pearl_prime_100_run/book_018.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 19/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 19/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic courage --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__courage__spiral__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_019 --out artifacts/pearl_prime_100_run/book_019.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 20/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 20/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_stress --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__financial_stress__shame__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_020 --out artifacts/pearl_prime_100_run/book_020.json --teacher maat 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 21/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 21/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic grief --persona gen_z_professionals --arc config/source_of_truth/master_arcs/gen_z_professionals__grief__grief__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_021 --out artifacts/pearl_prime_100_run/book_021.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 22/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 22/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__overthinking__spiral__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_022 --out artifacts/pearl_prime_100_run/book_022.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 23/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 23/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__burnout__overwhelm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_023 --out artifacts/pearl_prime_100_run/book_023.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 24/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 24/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__burnout__watcher__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_024 --out artifacts/pearl_prime_100_run/book_024.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 25/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 25/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__boundaries__false_alarm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_025 --out artifacts/pearl_prime_100_run/book_025.json --teacher junko 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 26/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 26/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona nyc_executives --arc config/source_of_truth/master_arcs/nyc_executives__boundaries__shame__F004.yaml --location nyc_grand_central --structural-format F004 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_026 --out artifacts/pearl_prime_100_run/book_026.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 27/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 27/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__burnout__watcher__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_027 --out artifacts/pearl_prime_100_run/book_027.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 28/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 28/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__sleep_anxiety__spiral__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_028 --out artifacts/pearl_prime_100_run/book_028.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 29/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 29/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__overthinking__false_alarm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_029 --out artifacts/pearl_prime_100_run/book_029.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 30/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 30/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic imposter_syndrome --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__imposter_syndrome__comparison__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_030 --out artifacts/pearl_prime_100_run/book_030.json --teacher ahjan 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 31/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 31/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__depression__grief__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_031 --out artifacts/pearl_prime_100_run/book_031.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 32/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 32/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__comparison__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_032 --out artifacts/pearl_prime_100_run/book_032.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 33/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 33/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_stress --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__financial_stress__shame__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_033 --out artifacts/pearl_prime_100_run/book_033.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 34/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 34/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__anxiety__shame__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_034 --out artifacts/pearl_prime_100_run/book_034.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 35/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 35/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__anxiety__comparison__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_035 --out artifacts/pearl_prime_100_run/book_035.json --teacher adi_da 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 36/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 36/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__anxiety__overwhelm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_036 --out artifacts/pearl_prime_100_run/book_036.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 37/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 37/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__depression__grief__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_037 --out artifacts/pearl_prime_100_run/book_037.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 38/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 38/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic somatic_healing --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__somatic_healing__overwhelm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_038 --out artifacts/pearl_prime_100_run/book_038.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 39/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 39/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__overthinking__spiral__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_039 --out artifacts/pearl_prime_100_run/book_039.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 40/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 40/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__sleep_anxiety__false_alarm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_040 --out artifacts/pearl_prime_100_run/book_040.json --teacher miki 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 41/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 41/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic grief --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__grief__watcher__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_041 --out artifacts/pearl_prime_100_run/book_041.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 42/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 42/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic self_worth --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__self_worth__comparison__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_042 --out artifacts/pearl_prime_100_run/book_042.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 43/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 43/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__burnout__grief__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_043 --out artifacts/pearl_prime_100_run/book_043.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 44/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 44/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic imposter_syndrome --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__imposter_syndrome__shame__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_044 --out artifacts/pearl_prime_100_run/book_044.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 45/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 45/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic courage --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__courage__shame__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_045 --out artifacts/pearl_prime_100_run/book_045.json --teacher junko 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 46/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 46/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__depression__watcher__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_046 --out artifacts/pearl_prime_100_run/book_046.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 47/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 47/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__overthinking__spiral__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_047 --out artifacts/pearl_prime_100_run/book_047.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 48/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 48/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic self_worth --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__self_worth__comparison__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_048 --out artifacts/pearl_prime_100_run/book_048.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 49/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 49/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_stress --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__financial_stress__shame__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_049 --out artifacts/pearl_prime_100_run/book_049.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 50/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 50/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__burnout__grief__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_050 --out artifacts/pearl_prime_100_run/book_050.json --teacher ahjan 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 51/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 51/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__anxiety__false_alarm__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_051 --out artifacts/pearl_prime_100_run/book_051.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 52/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 52/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic somatic_healing --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__somatic_healing__watcher__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_052 --out artifacts/pearl_prime_100_run/book_052.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 53/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 53/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__sleep_anxiety__false_alarm__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_053 --out artifacts/pearl_prime_100_run/book_053.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 54/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 54/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__overthinking__watcher__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_054 --out artifacts/pearl_prime_100_run/book_054.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 55/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 55/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic social_anxiety --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__social_anxiety__shame__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_055 --out artifacts/pearl_prime_100_run/book_055.json --teacher miki 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 56/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 56/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__depression__overwhelm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_056 --out artifacts/pearl_prime_100_run/book_056.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 57/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 57/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__anxiety__shame__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_057 --out artifacts/pearl_prime_100_run/book_057.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 58/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 58/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__spiral__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_058 --out artifacts/pearl_prime_100_run/book_058.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 59/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 59/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic somatic_healing --persona gen_z_professionals --arc config/source_of_truth/master_arcs/gen_z_professionals__somatic_healing__watcher__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_059 --out artifacts/pearl_prime_100_run/book_059.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 60/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 60/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic compassion_fatigue --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__compassion_fatigue__watcher__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_060 --out artifacts/pearl_prime_100_run/book_060.json --teacher sai_ma 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 61/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 61/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__boundaries__shame__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_061 --out artifacts/pearl_prime_100_run/book_061.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 62/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 62/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__sleep_anxiety__overwhelm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_062 --out artifacts/pearl_prime_100_run/book_062.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 63/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 63/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__boundaries__comparison__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_063 --out artifacts/pearl_prime_100_run/book_063.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 64/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 64/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__burnout__overwhelm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_064 --out artifacts/pearl_prime_100_run/book_064.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 65/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 65/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__anxiety__false_alarm__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_065 --out artifacts/pearl_prime_100_run/book_065.json --teacher joshin 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 66/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 66/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic social_anxiety --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__social_anxiety__false_alarm__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_066 --out artifacts/pearl_prime_100_run/book_066.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 67/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 67/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__anxiety__false_alarm__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_067 --out artifacts/pearl_prime_100_run/book_067.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 68/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 68/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__depression__overwhelm__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_068 --out artifacts/pearl_prime_100_run/book_068.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 69/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 69/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__anxiety__spiral__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_069 --out artifacts/pearl_prime_100_run/book_069.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 70/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 70/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic social_anxiety --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__social_anxiety__comparison__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_070 --out artifacts/pearl_prime_100_run/book_070.json --teacher ahjan 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 71/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 71/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__overthinking__spiral__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_071 --out artifacts/pearl_prime_100_run/book_071.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 72/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 72/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic depression --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__depression__watcher__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_072 --out artifacts/pearl_prime_100_run/book_072.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 73/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 73/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic courage --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__courage__spiral__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_073 --out artifacts/pearl_prime_100_run/book_073.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 74/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 74/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_anxiety --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__financial_anxiety__shame__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_074 --out artifacts/pearl_prime_100_run/book_074.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 75/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 75/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__boundaries__shame__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_075 --out artifacts/pearl_prime_100_run/book_075.json --teacher adi_da 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 76/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 76/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_stress --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__financial_stress__spiral__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_076 --out artifacts/pearl_prime_100_run/book_076.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 77/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 77/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_anxiety --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__financial_anxiety__spiral__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_077 --out artifacts/pearl_prime_100_run/book_077.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 78/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 78/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__anxiety__overwhelm__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_078 --out artifacts/pearl_prime_100_run/book_078.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 79/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 79/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__sleep_anxiety__spiral__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_079 --out artifacts/pearl_prime_100_run/book_079.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 80/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 80/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__anxiety__false_alarm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_080 --out artifacts/pearl_prime_100_run/book_080.json --teacher sai_ma 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 81/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 81/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_z_professionals --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F002.yaml --location coastal_california --structural-format F002 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_081 --out artifacts/pearl_prime_100_run/book_081.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 82/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 82/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__anxiety__spiral__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_082 --out artifacts/pearl_prime_100_run/book_082.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 83/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 83/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__anxiety__grief__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_083 --out artifacts/pearl_prime_100_run/book_083.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 84/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 84/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic self_worth --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__self_worth__comparison__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_084 --out artifacts/pearl_prime_100_run/book_084.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 85/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 85/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona gen_x_sandwich --arc config/source_of_truth/master_arcs/gen_x_sandwich__anxiety__spiral__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_085 --out artifacts/pearl_prime_100_run/book_085.json --teacher maat 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 86/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 86/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic social_anxiety --persona gen_alpha_students --arc config/source_of_truth/master_arcs/gen_alpha_students__social_anxiety__shame__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_086 --out artifacts/pearl_prime_100_run/book_086.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 87/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 87/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic compassion_fatigue --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__compassion_fatigue__overwhelm__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_087 --out artifacts/pearl_prime_100_run/book_087.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 88/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 88/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic financial_anxiety --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__financial_anxiety__shame__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_088 --out artifacts/pearl_prime_100_run/book_088.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 89/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 89/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic somatic_healing --persona first_responders --arc config/source_of_truth/master_arcs/first_responders__somatic_healing__overwhelm__F006.yaml --location coastal_california --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_089 --out artifacts/pearl_prime_100_run/book_089.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 90/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 90/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic courage --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__courage__false_alarm__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_090 --out artifacts/pearl_prime_100_run/book_090.json --teacher maat 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 91/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 91/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic grief --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__grief__watcher__F006.yaml --location generic_us_urban --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_091 --out artifacts/pearl_prime_100_run/book_091.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 92/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 92/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic burnout --persona millennial_women_professionals --arc config/source_of_truth/master_arcs/millennial_women_professionals__burnout__overwhelm__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_092 --out artifacts/pearl_prime_100_run/book_092.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 93/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 93/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic overthinking --persona corporate_managers --arc config/source_of_truth/master_arcs/corporate_managers__overthinking__watcher__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_093 --out artifacts/pearl_prime_100_run/book_093.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 94/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 94/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic self_worth --persona healthcare_rns --arc config/source_of_truth/master_arcs/healthcare_rns__self_worth__shame__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_094 --out artifacts/pearl_prime_100_run/book_094.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 95/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 95/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic boundaries --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__boundaries__comparison__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_095 --out artifacts/pearl_prime_100_run/book_095.json --teacher junko 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 96/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 96/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona entrepreneurs --arc config/source_of_truth/master_arcs/entrepreneurs__sleep_anxiety__spiral__F006.yaml --location nyc_metro --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_096 --out artifacts/pearl_prime_100_run/book_096.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 97/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 97/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic somatic_healing --persona gen_z_professionals --arc config/source_of_truth/master_arcs/gen_z_professionals__somatic_healing__overwhelm__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_097 --out artifacts/pearl_prime_100_run/book_097.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 98/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 98/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic sleep_anxiety --persona working_parents --arc config/source_of_truth/master_arcs/working_parents__sleep_anxiety__spiral__F006.yaml --location toronto_ca --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_098 --out artifacts/pearl_prime_100_run/book_098.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [ 99/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [ 99/100] FAIL"
fi

TOTAL=$((TOTAL+1))
if python3 scripts/run_pipeline.py --topic anxiety --persona tech_finance_burnout --arc config/source_of_truth/master_arcs/tech_finance_burnout__anxiety__spiral__F006.yaml --location nyc_grand_central --structural-format F006 --quality-profile draft --render-book --render-dir artifacts/pearl_prime_100_run/book_099 --out artifacts/pearl_prime_100_run/book_099.json 2>/dev/null; then
  PASS=$((PASS+1))
  echo "  [100/100] PASS"
else
  FAIL=$((FAIL+1))
  echo "  [100/100] FAIL"
fi

echo "
========== RESULTS =========="
echo "Total: $TOTAL  Pass: $PASS  Fail: $FAIL"
