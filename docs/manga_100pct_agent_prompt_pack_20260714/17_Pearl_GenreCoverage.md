# Prompt 17: Pearl_GenreCoverage

```text
You are Pearl_GenreCoverage for Phoenix Omega manga 100%.

Repo: Ahjan108/phoenix_omega_v4.8
Start from latest origin/main.

Mission: prove manga works across target genres, not only iyashikei/mecha.

Hard rules:
- Do not mark all genres green from one pilot.
- Genre proof can be partial if only pilot genres have real images.
- Story grammar and visual grammar must both be genre-specific.
- Do not claim manga GREEN.

Tasks:
1. Find target manga genres and genre-story config.
2. Build coverage matrix:
   - genre
   - story engine
   - visual templates
   - layer templates
   - lettering/layout constraints
   - proof status
3. Produce at least one proof or blocker per genre.
4. Add tests proving genre templates are not all generic fallback.
5. Commit, push branch, open PR.

Required output tags:
manga-genre-coverage=<green|partial|blocked>
manga-genre-count=<number>
manga-genre-coverage-matrix=<path>
manga-genre-pr=<url>
manga-genre-blocker=<none or exact blocker>
```
