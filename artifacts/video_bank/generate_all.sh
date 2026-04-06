#!/bin/bash
# Video bank background image generator via RunComfy API
# Submits all 20 backgrounds, polls for completion, downloads results

set -euo pipefail

API_KEY="8ba0446d-2fdf-4757-87cc-017c8d7dfd84"
DEPLOYMENT="677edba8-ace0-4b2b-bad2-8e94b9959065"
BASE_URL="https://api.runcomfy.net/prod/v1/deployments/${DEPLOYMENT}"
OUT_DIR="/Users/ahjan/phoenix_omega/.claude/worktrees/magical-beaver/artifacts/video_bank"

mkdir -p "$OUT_DIR"

# ── Define all 20 images ──
declare -a NAMES PROMPTS

NAMES[0]="vb_anxiety_calm"
PROMPTS[0]="Soft morning light through sheer curtains, empty meditation cushion, warm golden tones, peaceful room, 16:9 cinematic, professional photography, high quality"

NAMES[1]="vb_burnout_recovery"
PROMPTS[1]="Person's hands resting on wooden desk, cup of tea steaming, morning sunlight, warm earth tones, 16:9, professional photography, high quality"

NAMES[2]="vb_sleep_night"
PROMPTS[2]="Moonlit bedroom window, soft blue tones, stars visible, peaceful night scene, 16:9 cinematic, professional photography, high quality"

NAMES[3]="vb_grief_still"
PROMPTS[3]="Empty park bench under autumn tree, fallen leaves, soft golden hour light, contemplative mood, 16:9, professional photography, high quality"

NAMES[4]="vb_imposter_mirror"
PROMPTS[4]="Bathroom mirror with condensation, blurred reflection, morning light, intimate personal moment, 16:9, professional photography, high quality"

NAMES[5]="vb_boundaries_door"
PROMPTS[5]="Wooden door slightly ajar, warm light spilling through gap, symbolic threshold, 16:9, professional photography, high quality"

NAMES[6]="vb_overthinking_loop"
PROMPTS[6]="Spiral staircase from above, geometric pattern, soft blue tones, abstract contemplative, 16:9, professional photography, high quality"

NAMES[7]="vb_somatic_body"
PROMPTS[7]="Close-up of hands on chest, soft warm lighting, body awareness, gentle self-touch, 16:9, professional photography, high quality"

NAMES[8]="vb_courage_cliff"
PROMPTS[8]="Person silhouette at cliff edge overlooking ocean at sunrise, expansive view, golden light, 16:9, professional photography, high quality"

NAMES[9]="vb_mindfulness_present"
PROMPTS[9]="Zen garden with raked sand patterns, single stone, morning dew, minimal peaceful, 16:9, professional photography, high quality"

NAMES[10]="vb_nature_forest"
PROMPTS[10]="Sunlight filtering through forest canopy, moss-covered path, green tones, peaceful, 16:9, professional photography, high quality"

NAMES[11]="vb_nature_ocean"
PROMPTS[11]="Gentle ocean waves on sandy beach, soft blue golden hour, calming seascape, 16:9, professional photography, high quality"

NAMES[12]="vb_nature_rain"
PROMPTS[12]="Rain drops on window glass, blurred city lights behind, contemplative mood, 16:9, professional photography, high quality"

NAMES[13]="vb_nature_mountain"
PROMPTS[13]="Misty mountain peak at dawn, layers of mountains fading, purple blue gradient, 16:9, professional photography, high quality"

NAMES[14]="vb_nature_stream"
PROMPTS[14]="Clear stream over smooth stones, dappled sunlight, forest setting, flowing water, 16:9, professional photography, high quality"

NAMES[15]="vb_abstract_warmth"
PROMPTS[15]="Abstract warm gradient, golden amber to soft cream, subtle organic texture, calm soothing, 16:9, professional photography, high quality"

NAMES[16]="vb_abstract_cool"
PROMPTS[16]="Abstract cool gradient, deep navy to soft lavender, water-like flowing texture, peaceful, 16:9, professional photography, high quality"

NAMES[17]="vb_abstract_breath"
PROMPTS[17]="Abstract expanding circles like breath ripples, soft white on pale blue, rhythmic pattern, 16:9, professional photography, high quality"

NAMES[18]="vb_abstract_ground"
PROMPTS[18]="Abstract earth tones, grounding texture, horizontal layers, stable foundation feel, 16:9, professional photography, high quality"

NAMES[19]="vb_abstract_light"
PROMPTS[19]="Abstract warm light rays through soft fog, golden particles floating, ethereal gentle, 16:9, professional photography, high quality"

# ── Submit function ──
submit_image() {
    local prompt="$1"
    local resp
    resp=$(curl -s -X POST "${BASE_URL}/inference" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json" \
        -d "{\"overrides\": {\"6\": {\"inputs\": {\"text\": \"${prompt}\"}}}}")
    echo "$resp"
}

# ── Poll function ──
poll_status() {
    local request_id="$1"
    local status_url="${BASE_URL}/requests/${request_id}/status"
    local max_wait=300
    local interval=5
    local elapsed=0

    while [ $elapsed -lt $max_wait ]; do
        local resp
        resp=$(curl -s "${status_url}" \
            -H "Authorization: Bearer ${API_KEY}" \
            -H "Content-Type: application/json")
        local status
        status=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null || echo "unknown")

        if [ "$status" = "succeeded" ] || [ "$status" = "completed" ]; then
            echo "completed"
            return 0
        elif [ "$status" = "failed" ] || [ "$status" = "error" ]; then
            echo "failed"
            return 1
        fi

        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo "timeout"
    return 1
}

# ── Download result ──
download_result() {
    local request_id="$1"
    local output_file="$2"
    local result_url="${BASE_URL}/requests/${request_id}/result"

    local resp
    resp=$(curl -s "${result_url}" \
        -H "Authorization: Bearer ${API_KEY}" \
        -H "Content-Type: application/json")

    # Extract first image URL from outputs
    local image_url
    image_url=$(echo "$resp" | python3 -c "
import sys, json
data = json.load(sys.stdin)
outputs = data.get('outputs', {})
for node_id, node_out in outputs.items():
    if isinstance(node_out, dict):
        images = node_out.get('images', [])
        if images:
            if isinstance(images[0], dict):
                print(images[0].get('url', ''))
            elif isinstance(images[0], str):
                print(images[0])
            break
" 2>/dev/null)

    if [ -n "$image_url" ]; then
        curl -s -o "$output_file" "$image_url"
        echo "downloaded"
        return 0
    else
        echo "no_url"
        return 1
    fi
}

# ── Main batch loop ──
echo "=== Video Bank Generation: 20 images ==="
echo "Output: $OUT_DIR"
echo ""

BATCH_SIZE=5
TOTAL=${#NAMES[@]}
COMPLETED=0
FAILED=0

# Track request IDs for parallel polling
declare -a REQUEST_IDS

for batch_start in $(seq 0 $BATCH_SIZE $((TOTAL-1))); do
    batch_end=$((batch_start + BATCH_SIZE - 1))
    if [ $batch_end -ge $TOTAL ]; then
        batch_end=$((TOTAL - 1))
    fi

    echo "--- Batch: images $((batch_start+1))-$((batch_end+1)) ---"

    # Submit all in batch
    REQUEST_IDS=()
    for i in $(seq $batch_start $batch_end); do
        echo "  Submitting [${NAMES[$i]}]..."
        resp=$(submit_image "${PROMPTS[$i]}")
        rid=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('request_id',''))" 2>/dev/null || echo "")
        if [ -n "$rid" ]; then
            REQUEST_IDS+=("$rid")
            echo "    -> request_id: $rid"
        else
            REQUEST_IDS+=("FAILED")
            echo "    -> SUBMIT FAILED: $resp"
        fi
        sleep 1  # small gap between submits
    done

    # Poll and download each
    for j in $(seq 0 $((${#REQUEST_IDS[@]}-1))); do
        idx=$((batch_start + j))
        rid="${REQUEST_IDS[$j]}"
        name="${NAMES[$idx]}"
        output_file="${OUT_DIR}/${name}.png"

        if [ "$rid" = "FAILED" ]; then
            echo "  [${name}] SKIP (submit failed)"
            FAILED=$((FAILED + 1))
            continue
        fi

        echo "  Polling [${name}] (${rid})..."
        poll_result=$(poll_status "$rid")

        if [ "$poll_result" = "completed" ]; then
            echo "  Downloading [${name}]..."
            dl_result=$(download_result "$rid" "$output_file")
            if [ "$dl_result" = "downloaded" ]; then
                size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file" 2>/dev/null || echo "?")
                echo "  OK [${name}] -> ${output_file} (${size} bytes)"
                COMPLETED=$((COMPLETED + 1))
            else
                echo "  FAIL [${name}] download: $dl_result"
                FAILED=$((FAILED + 1))
            fi
        else
            echo "  FAIL [${name}] poll: $poll_result"
            FAILED=$((FAILED + 1))
        fi
    done

    echo ""
    # Brief pause between batches
    if [ $batch_end -lt $((TOTAL-1)) ]; then
        echo "  (pause 3s between batches)"
        sleep 3
    fi
done

echo "========================================="
echo "DONE: ${COMPLETED} completed, ${FAILED} failed out of ${TOTAL}"
echo "Output directory: ${OUT_DIR}"
ls -la "${OUT_DIR}"/*.png 2>/dev/null | wc -l | xargs -I{} echo "PNG files: {}"
