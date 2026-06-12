# Agent Instructions

This project follows `roadmap.tsv`. Before generating content, locate the exact
roadmap row for the requested topic and use that row as the source of truth.

## Roadmap Source Of Truth

Use `roadmap.tsv` as the planning source for topic generation.

## Fast Roadmap Lookup

When the user requests a topic by number, do not read the whole `roadmap.tsv`
first. Search directly for the tab-delimited `Ordem` column and inspect only the
matching row.

Preferred lookup pattern for topic number `<N>`:

```regex
^([^\t]*\t)<N>\t
```

Examples:

- Topic 19: search `^([^\t]*\t)19\t` in `roadmap.tsv`.
- Topic 091 or 91: search `^([^\t]*\t)0?91\t` if the user may include or omit leading zeros.

Only read a larger portion of `roadmap.tsv` if the direct search fails, returns
multiple ambiguous rows, or the user identifies the topic by title/level instead
of `Ordem`.

Important columns:

- `Nível`: CEFR level or module group.
- `Ordem`: global topic order.
- `Bloco`: learning block/category.
- `Tópico Principal`: topic title.
- `Subtópicos / Conteúdo`: required scope for the topic.
- `Status`: generation status.
- `Material Gerado`: whether core topic files exist.
- `Flashcards`: whether flashcards were generated or skipped.
- `Exercícios`: whether exercises were generated.
- `Teste`: whether test content was generated.
- `Revisado`: whether a human reviewed it.

## Topic Selection

When asked to generate a topic:

1. Locate the selected row in `roadmap.tsv`, preferably by direct search on `Ordem` when a topic number is provided.
2. Find the selected topic by `Ordem`, `Nível`, or `Tópico Principal`.
3. Use the roadmap row to determine level, block, title, and required subtópicos.
4. Create the topic folder under `topics/<level>/<order-topic-slug>/`.
5. Generate only the files required by this project.

Example folder names:

- `topics/a1/001-alfabeto-alemao-e-sons-basicos/`
- `topics/a1/004-cumprimentos-e-despedidas/`
- `topics/b1/091-verbos-com-preposicoes-fixas/`

Use three digits for `Ordem` so folders sort correctly.

Folder slugs must be unique across the whole `topics/` tree. Derive the slug
from `Tópico Principal`; when several roadmap rows share the same title,
disambiguate using `Subtópicos / Conteúdo` (for example,
`070-possessivos-nominativo-e-acusativo` and `071-possessivos-no-dativo`
instead of two folders named `pronomes-possessivos`).

## Topic Learning Load Evaluation

Before generating a topic, evaluate its learning load from the roadmap row. Use
the topic title, level, block, and subtópicos to decide how much practice the
student needs.

Evaluate two dimensions:

- `Difficulty`: how hard the topic is for the target student at that CEFR level.
- `Importance`: how critical the topic is for future German learning.

Use this evaluation to scale the amount of content inside the required files,
without creating extra source files unless explicitly requested.

Guidelines:

- Low difficulty and low/medium importance: short lesson, 1 short story, 3-4 exercise groups, 8-10 test questions.
- Medium difficulty or medium/high importance: fuller lesson, 1-2 short stories or story sections, 4-6 exercise groups, 10-14 test questions.
- High difficulty or high importance: detailed lesson, 2-3 short stories or guided contexts, 6-8 exercise groups, 14-20 test questions.

Treat these as flexible targets, not rigid quotas. If a topic is foundational
or error-prone, add more examples, contrastive explanations, guided practice,
and review questions so the student can learn it well before moving on.

For critical topics, prefer more varied practice over longer prose: recognition,
translation, fill-in-the-blank, sentence transformation, short production, and
review questions where appropriate for the level.

For `lesson.md`, scale the explanation by CEFR level, importance, and
difficulty. Important or error-prone topics should not end with a mostly empty
final page if more useful guidance would help the student. Add compact guided
practice, contrastive examples, mini-checks with explanations, or extra example
tables where appropriate. Keep this level-appropriate: A1/A2 should stay short,
clear, and patterned; B1/B2 can include more sentence-level contrast and usage
notes; C1/C2 can include nuance, register, and exceptions.

For `story.md`, scale the story by CEFR level, importance, and difficulty.
Important foundational topics should usually include more reading practice, but
the kind of reading must match the roadmap level. A1/A2 stories should use more
short, transparent sentences and guided completion. B1/B2 stories can use richer
connected paragraphs, reasons, opinions, and reformulation. C1/C2 stories can
use denser prose, register nuance, and analytical questions. Avoid leaving most
of the story page empty when the topic can support more level-appropriate
reading or guided practice.

## Content Quality Rules

- Use Brazilian Portuguese for headings, section subtitles, instructions,
  table headers, notes, and explanations.
- Keep German only where the learner should read or produce German.
- Do not copy exercise items into `test.yaml`. The test may assess the same
  skill, but it must use new sentences, contexts, names, and examples.
- Multiple-choice items should usually have exactly three options.
- Distribute correct multiple-choice answers across option positions 1, 2, and
  3. Avoid making the correct answer mostly option 1 or 2.
- In `answers.md`, include a short explanation for every exercise and test
  answer, not only the answer or points.

## Required Topic Files

Each generated topic folder must contain:

```txt
lesson.md
vocabulary.yaml
flashcards.yaml
exercises.yaml
test.yaml
story.md
answers.md
```

Exception: if flashcards are not useful for the selected topic, still create
`flashcards.yaml`, but make it explicit that flashcards were intentionally
skipped.

Use this shape when skipping flashcards:

```yaml
topic: Topic Title
level: A1
cards: []
note: Flashcards skipped because this topic is better practiced through exercises and examples.
```

## Flashcard Evaluation

Before generating `flashcards.yaml`, decide whether flashcards are useful for
the selected topic.

Flashcards are usually useful for:

- Vocabulary topics.
- Fixed phrases.
- Verb forms.
- Articles and gender patterns.
- Irregular forms.
- Idioms and expressions.
- Prepositions with required cases.

Flashcards are often not enough or may be skipped for:

- Broad review topics.
- Writing tasks.
- Debate or speaking practice.
- Complex syntax topics that require full sentence production.
- Pronunciation topics that need audio or guided reading more than memorization.

If flashcards are useful, generate concise cards with a German front, translated
back, German example, and translation.

If flashcards are weak for the topic, skip them with `cards: []` and focus the
learning value in `lesson.md`, `exercises.yaml`, `story.md`, and `test.yaml`.

## Content Generation Rules

- Do not generate PDFs directly with AI.
- Markdown and YAML are the source of truth.
- Typst is only for rendering printable PDFs.
- Keep files small, editable, and reusable.
- Use the prompt files in `prompts/` as contracts for output format.
- Keep YAML valid and simple.
- Keep Markdown clean and predictable.
- Prefer Brazilian Portuguese for explanations unless asked otherwise.
- Generate content appropriate to the roadmap level.
- Do not invent roadmap topics outside `roadmap.tsv` unless explicitly asked.

## After Generation

After generating a topic:

1. Validate YAML files parse successfully.
2. Run `python3 scripts/validate-content.py <topic-folder>` and fix all content
   QA issues. New topics must pass with zero issues; `qa-baseline.txt` only
   covers legacy topics and must not receive new entries.
3. Compile PDFs with `scripts/compile-topic.sh <topic-folder>` if Typst is available.
4. Generate audio with `.venv/bin/python scripts/generate-audio.py <ordem>` if
   the local environment is set up (see Audio Generation below).
5. Export the Anki deck with `.venv/bin/python scripts/export-anki.py` if the
   topic has flashcards.
6. Update `roadmap.tsv` status by running `python3 scripts/sync-roadmap.py`.
   Do not edit `roadmap.tsv` by hand.
7. Report which files were created.
8. Report whether flashcards were generated or intentionally skipped, and why.

## Audio Generation

The project uses Piper TTS with two fixed voices:

- German: `de_DE-karlsson-low`
- Brazilian Portuguese: `pt_BR-cadu-medium`

Setup (one time):

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Generate audio for a topic (voices download automatically on first run):

```sh
.venv/bin/python scripts/generate-audio.py 104
```

Outputs per topic under `output/audio/<topic-folder>/`:

- `cards/*.wav`: one clip per flashcard front and example, consumed by the
  Anki exporter.
- `vocab-review.wav`: passive-listening track (German word, Portuguese
  translation, German example, Portuguese translation).
- `story.wav`: the `## História em alemão` section read aloud.

Audio rules for generated content:

- `story.md` must always contain a `## História em alemão` section with the
  German story as plain paragraphs, because the audio script extracts exactly
  that section.
- Keep flashcard `front` and `example` fields as clean German text (no
  Markdown, no parenthetical Portuguese) so the TTS clips sound natural.

## Anki Export

Export flashcards to a single `.apkg` with one subdeck per topic:

```sh
.venv/bin/python scripts/export-anki.py            # all topics
.venv/bin/python scripts/export-anki.py 99 100     # specific topics
```

The deck embeds audio clips automatically when `output/audio/<topic>/cards/`
exists, so run `generate-audio.py` before exporting when audio is wanted.
Each note produces two cards: DE → PT (recognition) and PT → DE (production).
Re-importing the same export updates existing notes instead of duplicating
them.

## Cumulative Reviews

Spaced review is required for retention. After every block of 10 topics is
completed (001-010, 011-020, 021-030, ...), generate a cumulative review:

1. Create the folder `reviews/<start>-<end>/` (for example `reviews/001-010/`).
2. Generate `test.yaml` using `prompts/review.prompt.md`, mixing all topics of
   the block with fresh sentences and interleaved questions.
3. Generate `answers.md` with a `## Gabarito do teste` table that includes an
   explanation column, following the same rules as topic answer keys.
4. Compile with `scripts/compile-review.sh <start>-<end>`.

Review tests must never copy items from the original exercises or tests of the
covered topics.
