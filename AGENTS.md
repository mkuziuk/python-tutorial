# Project guidance

This repository contains a Russian-language project tutorial for Python and
classical machine learning. The Astro/Starlight site is in `src/`, Part I uses
four standalone Python projects under `projects/case-*`, and Part II uses six
Jupyter projects under `projects/part-2/case-*`.

Keep lesson pages, solution pages, downloadable projects, and generated assets
consistent. Part II solution notebooks are canonical; regenerate learner
notebooks with `pnpm build:notebooks`. Rebuild downloadable ZIP files and their
checksums with `pnpm build:archives`. Do not change story facts established in
`PLOT.md` or `PLOT_PART_2.md`, and follow `EDITORIAL_GUIDE_RU.md` for Russian
terminology and tone.

Part I solution scripts are canonical for the four generated solution pages;
run `pnpm build:part1-solutions` after changing them. The investigations pass
JSON artifacts from I-01 through I-04. Run `pnpm build:part1-artifacts` after
changing a Part I schema, finding, fixture, or solution that affects the handoff.

## Comments in tutorial code

- Document every meaningful statement either in an adjacent comment/docstring
  or in the lesson prose immediately after its listing. A learner should never
  have to infer a variable's role, the shape of a returned value, or why a
  branch exists. Obvious punctuation and syntax do not need separate comments.
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

## Explanation pattern from *Real-World Python*

Use the recurring teaching sequence from Lee Vaughan's *Real-World Python: A
Hacker's Guide to Solving Problems with Code* for new and substantially revised
lessons:

1. Before a listing, state the concrete operation, its input, and the value or
   side effect it will produce.
2. Show a small, coherent listing that performs one stage of the program. Avoid
   introducing several unrelated concepts in the same block.
3. Immediately after the listing, walk through every meaningful statement in
   execution order. Name the functions and variables, describe important data
   shapes such as `list[tuple]` or `dict[str, dossier]`, and explain conditions,
   constants, units, and chosen weights.
4. Show a concrete intermediate result before moving on: a short `print()`
   example, representative dictionary, count, table row, or expected terminal
   output. Connect that result to the next stage of the program.
5. Only then introduce the next listing. Keep the visible chain explicit:
   input file → parsed value → transformed value → decision → saved artifact.

Part I learner ZIPs intentionally contain an empty Python file that the learner
fills while following the chapter. Do not replace it with `TODO` stubs or a
finished implementation. The complete code belongs in the chapter and the
canonical solution, and those two versions must remain synchronized. Part I
tests are maintainer tools for checking that the tutorial works; keep test
commands and test-driven instructions out of student-facing pages and ZIPs.
Part II notebooks retain their separate learner/solution workflow described
above.

Treat schema labels and identifiers as implementation details, not learning
goals. Supply fixed values such as `finding_id` in the starter code when the
learner does not need to design them. At first use, explain the practical reason
for the identifier—for example, finding a record when list order changes—and
then return attention to the investigation task.

Do not replace this sequence with a large unexplained final listing. A complete
listing may appear at the end or on a solution page, but the main lesson must
have already introduced and explained its parts in runnable stages.

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
