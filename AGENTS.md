# Project guidance

This repository contains a Russian-language project tutorial for Python and
classical machine learning. The Astro/Starlight site is in `src/`, Part I uses
six standalone Python projects under `projects/case-*`, and Part II uses six
Jupyter projects under `projects/part-2/case-*`.

Keep lesson pages, solution pages, downloadable projects, and generated assets
consistent. Part II solution notebooks are canonical; regenerate learner
notebooks with `pnpm build:notebooks`. Rebuild downloadable ZIP files and their
checksums with `pnpm build:archives`. Do not change story facts established in
`PLOT.md` or `PLOT_PART_2.md`, and follow `EDITORIAL_GUIDE_RU.md` for Russian
terminology and tone.

## Comments in tutorial code

- State the direct effect of the adjacent line or block and name the relevant
  function, variable, class, or value when that makes the comment clearer.
- Prefer a positive statement such as “`urlparse` separates the URL into
  components” over explaining the operation through what it does not do.
- Put broader caveats about security, probability, production limitations, or
  interpretation in the surrounding prose unless they are required to use the
  code correctly.
- Do not restate obvious syntax. Explain a reason, invariant, unit, assumption,
  data boundary, or non-obvious library behavior.
- Keep duplicated comments synchronized across lesson pages, solution pages,
  scripts, and notebooks. Preserve learner/solution boundaries in Part II.

## Verification

Run the narrow checks for the edited area and use `pnpm verify` before handing
off broad course changes. `pnpm build` verifies the rendered site, while
`pnpm test:python`, `pnpm test:notebooks`, and `pnpm test:archives` cover the
project code and generated teaching materials.
