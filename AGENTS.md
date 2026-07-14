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

Part I solution scripts are canonical for the six generated solution pages;
run `pnpm build:part1-solutions` after changing them. The investigations pass
JSON artifacts from I-01 through I-06. Run `pnpm build:part1-artifacts` after
changing a Part I schema, finding, fixture, or solution that affects the handoff.

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

## Tutorial prose

- Describe what the learner will do, what material they will use, and what
  result they will produce. Prefer “read the `.eml` files, extract links, and
  assign a risk score” over broad claims about careful reasoning.
- In course summaries and introductions, prioritize the actual curriculum:
  projects, Python concepts, datasets, notebook work, tests, and resulting
  artifacts. Do not make an abstract principle sound like the main learning
  outcome when concrete skills are more useful to the learner.
- Keep story language for atmosphere, but write instructions, learning goals,
  transitions, and outcomes literally. A learner should not need the plot to
  understand what happens next.
- Avoid unexplained metaphors and contrasts such as “the boundary of a
  conclusion” or “not a loud result, but a careful one.” Name the operation
  instead: split the data, compare metrics, inspect errors, or record a model
  limitation.
- Introduce unfamiliar terms with a short plain-language definition at first
  use. Prefer concrete nouns and existing identifiers over labels such as
  “discipline,” “signal,” “trace,” or “strategy” when those labels do not name
  a specific object in the lesson.
- When a lesson says that a score is not a probability or that a result does
  not prove a conclusion, state the concrete reason in the same paragraph:
  name the manually chosen weights, missing calibration data, unobserved event,
  or evidence source that the program does not inspect.
- Keep one main idea per sentence and use active constructions that place the
  learner or program before the action.
- After changing prominent copy, inspect the rendered page at desktop and
  mobile widths. Rebalance type size, line length, or grid columns when a
  longer heading changes the intended proportions.

## Verification

Run the narrow checks for the edited area and use `pnpm verify` before handing
off broad course changes. `pnpm build` verifies the rendered site, while
`pnpm test:python`, `pnpm test:notebooks`, and `pnpm test:archives` cover the
project code and generated teaching materials.
