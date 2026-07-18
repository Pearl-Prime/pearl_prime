# Branch commands

Run each lane from a clean worktree. Do not stage unrelated dirty files.

## Lane A

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_a -b agent/manga-layered-default-integration-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_a
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane B

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_b -b agent/manga-raw-layer-hardening-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_b
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane C

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_c -b agent/manga-story-doctrine-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_c
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane D

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_d -b agent/manga-mode-plumbing-proof-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_d
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane E

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_e -b agent/manga-structural-template-expansion-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_e
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane F

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_f -b agent/manga-jlreq-vertical-furigana-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_f
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane G

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_g -b agent/manga-proof-packet-goldens-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_g
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane H

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_h -b agent/manga-batch-episode-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_h
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane I

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_i -b agent/manga-blind-read-bar-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_i
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane J

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_j -b agent/manga-contract-enforcement-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_j
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane K

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_k -b agent/manga-production-line-agents-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_k
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane L

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_l -b agent/manga-catalog-global-market-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_l
# apply the corresponding lane patch from the generated package
git status --short
```

## Lane M

```bash
git fetch origin main
git worktree add ../phoenix_manga_lane_m -b agent/manga-release-readiness-20260714 b507f3029e2aa7e5d9adfdb258b16d17910dc4fe
cd ../phoenix_manga_lane_m
# apply the corresponding lane patch from the generated package
git status --short
```
