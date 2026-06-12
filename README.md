# German Learning Content Generator

A local content-generation system for German learning materials.

The goal is to generate editable German lessons from reusable Markdown and YAML
source files, then render printable PDFs locally with Typst. AI models should
generate the source content only, not the final PDFs.

```txt
topic folder
↓
AI-generated Markdown/YAML
↓
Typst templates
↓
local PDF output
```

## Project Goal

This project helps create German learning materials consistently and cheaply.
Each topic can contain lessons, vocabulary, flashcards, exercises, tests,
stories, and answer keys.

The content is designed for manual editing and repeated reuse. Markdown files
are human-readable. YAML files hold structured data. Typst templates render the
printable PDFs.

## Folder Structure

```txt
german-learning-content/
├── README.md
├── requirements.txt
├── roadmap.tsv
├── qa-baseline.txt
├── topics/
│   ├── a1/
│   │   └── 001-alfabeto-alemao-e-sons-basicos/
│   │       ├── lesson.md
│   │       ├── vocabulary.yaml
│   │       ├── flashcards.yaml
│   │       ├── exercises.yaml
│   │       ├── test.yaml
│   │       ├── story.md
│   │       └── answers.md
│   ├── a2/
│   ├── b1/
│   ├── b2/
│   ├── c1/
│   └── c2/
├── reviews/
│   └── 001-010/
│       ├── test.yaml
│       └── answers.md
├── templates/
│   ├── lesson.typ
│   ├── flashcards.typ
│   ├── exercises.typ
│   ├── test.typ
│   └── story.typ
├── prompts/
│   ├── lesson.prompt.md
│   ├── vocabulary.prompt.md
│   ├── flashcards.prompt.md
│   ├── exercises.prompt.md
│   ├── test.prompt.md
│   ├── story.prompt.md
│   ├── answers.prompt.md
│   └── review.prompt.md
├── scripts/
│   ├── generate-topic.sh
│   ├── compile-topic.sh
│   ├── compile-all.sh
│   ├── compile-review.sh
│   ├── validate-content.py
│   ├── sync-roadmap.py
│   ├── generate-audio.py
│   └── export-anki.py
└── output/
    ├── pdf/
    ├── audio/
    └── exports/
```

## Source Files

Each real topic folder should contain exactly these source files:

```txt
lesson.md
vocabulary.yaml
flashcards.yaml
exercises.yaml
test.yaml
story.md
answers.md
```

Markdown files are for prose content:

- `lesson.md`: lesson explanation, examples, mistakes, summary
- `story.md`: short German story, translation, vocabulary notes, questions
- `answers.md`: answer keys for exercises, tests, and story questions

YAML files are for structured reusable data:

- `vocabulary.yaml`: words and examples
- `flashcards.yaml`: card fronts, backs, examples
- `exercises.yaml`: practice exercises
- `test.yaml`: test questions

## How To Add A New Topic

Choose the topic from `roadmap.tsv`, then create a topic folder with the helper script:

```sh
scripts/generate-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Or create the folder manually:

```sh
mkdir -p topics/a1/001-alfabeto-alemao-e-sons-basicos
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/lesson.md
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/vocabulary.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/flashcards.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/exercises.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/test.yaml
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/story.md
touch topics/a1/001-alfabeto-alemao-e-sons-basicos/answers.md
```

Use lower-case folder names with a three-digit roadmap order prefix, such as
`001-alfabeto-alemao-e-sons-basicos` or `022-acusativo-objeto-direto`.

## How To Generate Content With AI

Use the prompt files in `prompts/`. Each prompt is designed for one output file.

Before generating a topic, analyze its learning load from `roadmap.tsv`:

- `Difficulty`: how hard the topic is for the target student at that CEFR level.
- `Importance`: how critical the topic is for future German learning.

Use that analysis to decide how much content the topic needs inside the standard
source files. Do not create extra source files just because a topic is larger.

Recommended scale:

- Low difficulty and low/medium importance: short lesson, 1 short story, 3-4 exercise groups, 8-10 test questions.
- Medium difficulty or medium/high importance: fuller lesson, 1-2 short stories or story sections, 4-6 exercise groups, 10-14 test questions.
- High difficulty or high importance: detailed lesson, 2-3 short stories or guided contexts, 6-8 exercise groups, 14-20 test questions.

Critical or error-prone topics should get more examples, contrastive notes,
guided practice, review questions, and varied exercises so the student can learn
the topic well before moving on.

Quality rules for generated content:

- Use Brazilian Portuguese for headings, section subtitles, instructions,
  table headers, notes, and explanations.
- Keep German only where the learner should read or produce German.
- Do not copy exercise items into `test.yaml`; use new contexts and examples
  for exam questions.
- Multiple-choice items should usually have exactly three options, with correct
  answers distributed across positions 1, 2, and 3.
- In `answers.md`, include a short explanation for every exercise and test
  answer, not only the answer or points.

Replace these variables before sending the prompt to an AI model:

```txt
{{LEVEL}}
{{TOPIC}}
{{LANGUAGE_OF_EXPLANATION}}
{{TARGET_STUDENT}}
```

Example values:

```txt
{{LEVEL}} = A1
{{TOPIC}} = Greetings and Introductions
{{LANGUAGE_OF_EXPLANATION}} = Brazilian Portuguese
{{TARGET_STUDENT}} = adult Brazilian Portuguese speaker learning German
```

Example workflow for one topic:

1. Use `prompts/lesson.prompt.md` and save the AI output to `lesson.md`.
2. Use `prompts/vocabulary.prompt.md` and save the AI output to `vocabulary.yaml`.
3. Use `prompts/flashcards.prompt.md` and save the AI output to `flashcards.yaml`.
4. Use `prompts/exercises.prompt.md` and save the AI output to `exercises.yaml`.
5. Use `prompts/test.prompt.md` and save the AI output to `test.yaml`.
6. Use `prompts/story.prompt.md` and save the AI output to `story.md`.
7. Use `prompts/answers.prompt.md` and save the AI output to `answers.md`.

The prompts instruct the AI to output only the requested Markdown or YAML file
content. Do not ask the AI to produce PDFs.

## How To Compile PDFs With Typst

Install the Typst CLI, then compile one topic:

```sh
scripts/compile-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile all topic folders:

```sh
scripts/compile-all.sh
```

The generated PDFs are written to:

```txt
output/pdf/<topic-folder>/
```

Example output:

```txt
output/pdf/001-alfabeto-alemao-e-sons-basicos/lesson.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/flashcards.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/exercises.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/test.pdf
output/pdf/001-alfabeto-alemao-e-sons-basicos/story.pdf
```

The scripts run simple Typst commands like:

```sh
typst compile --root . templates/lesson.typ output/pdf/001-alfabeto-alemao-e-sons-basicos/lesson.pdf --input topic=../topics/a1/001-alfabeto-alemao-e-sons-basicos
```

## Recommended Workflow

1. Choose a topic from `roadmap.tsv`.
2. Create a topic folder under `topics/<level>/` using the roadmap order and title.
3. Generate Markdown and YAML using the prompt templates.
4. Save the generated content into the topic folder.
5. Manually review and edit the content.
6. Validate that YAML files are parseable.
7. Run content QA:

```sh
python3 scripts/validate-content.py --baseline qa-baseline.txt
```

8. Compile PDFs locally with Typst.
9. Generate audio and export the Anki deck (see below).
10. Sync the roadmap status:

```sh
python3 scripts/sync-roadmap.py
```

11. Keep editing the source Markdown/YAML, then recompile PDFs as needed.

New topics must pass content QA with zero issues. `qa-baseline.txt` exists only
to grandfather legacy topics generated before the QA rules; do not add new
entries to it.

## Audio And Anki

One-time setup of the local Python environment (uses [uv](https://docs.astral.sh/uv/)):

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Generate audio with Piper TTS (voices `de_DE-karlsson-low` and
`pt_BR-cadu-medium` are downloaded automatically to `.cache/piper-voices/` on
first run):

```sh
.venv/bin/python scripts/generate-audio.py            # all topics
.venv/bin/python scripts/generate-audio.py 22 104     # specific topics
```

Per topic this writes to `output/audio/<topic-folder>/`:

- `cards/*.wav`: one clip per flashcard front and example (used by the Anki export).
- `vocab-review.wav`: passive-listening loop, German + Portuguese.
- `story.wav`: the German story read aloud.

If `ffmpeg` is installed, the WAV files are converted to MP3 automatically.

Export flashcards to Anki (one `.apkg` with a subdeck per topic, audio
embedded when available):

```sh
.venv/bin/python scripts/export-anki.py               # all topics
.venv/bin/python scripts/export-anki.py 99 100        # specific topics
```

Import `output/exports/alemao.apkg` into Anki. Each note creates two cards:
DE → PT (recognition) and PT → DE (production). Re-importing updates notes in
place.

## Cumulative Reviews

After every block of 10 completed topics, generate a cumulative review test in
`reviews/<start>-<end>/` (for example `reviews/001-010/`) using
`prompts/review.prompt.md`, plus an `answers.md` answer key. Compile it with:

```sh
scripts/compile-review.sh 001-010
```

## Study Cadence Suggestion

1. One new topic per day: read `lesson.md`, listen to `story.wav`, do the exercises.
2. Anki every day (10-20 minutes), importing new topics as they are generated.
3. Listen to `vocab-review.wav` of recent topics during idle time.
4. One cumulative review test at the end of every 10-topic block.

## Examples

Create a new topic:

```sh
scripts/generate-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile one topic:

```sh
scripts/compile-topic.sh topics/a1/001-alfabeto-alemao-e-sons-basicos
```

Compile everything:

```sh
scripts/compile-all.sh
```

Validate YAML with Ruby if available:

```sh
ruby -e 'require "yaml"; ARGV.each { |f| YAML.load_file(f); puts "ok #{f}" }' topics/a1/001-alfabeto-alemao-e-sons-basicos/*.yaml
```

## Important Design Rules

- Do not generate PDFs directly with the AI.
- Do not use `.docx` as the source format.
- Markdown and YAML are the source of truth.
- Typst is only for rendering printable PDFs.
- Keep files small and reusable.
- The content should be easy to edit manually.
- The system should work locally.
- Prefer simple scripts over complex frameworks.
- Avoid unnecessary dependencies.
