# Review Test Prompt

Generate the complete contents of `test.yaml` for a cumulative review covering
a range of previously studied topics.

Variables:
- Level: `{{LEVEL}}`
- Topic range: `{{TOPIC_RANGE}}` (example: 001-010)
- Topics covered: `{{TOPICS_COVERED}}` (list of roadmap topic titles in the range)
- Language of explanation: `{{LANGUAGE_OF_EXPLANATION}}`
- Target student: `{{TARGET_STUDENT}}`

Inputs you may receive:
- The `vocabulary.yaml` files of the topics in the range.
- The `lesson.md` files of the topics in the range.
- The `test.yaml` files of the topics in the range.

Strict output rules:
- Output only valid YAML.
- Do not wrap the answer in code fences.
- Do not add comments, explanations, notes, or metadata outside the YAML.
- Use exactly the field names shown below.
- Use `options` only for multiple-choice questions.
- Keep answers exact and easy to grade.
- Use questions and instructions in `{{LANGUAGE_OF_EXPLANATION}}` unless the actual item text is German.
- Write for `{{TARGET_STUDENT}}` at level `{{LEVEL}}`.

Review-specific rules:
- Generate 20-30 questions mixing every topic in the range. Do not focus on
  only one or two topics.
- Prioritize the topics most likely to be forgotten or confused: grammar
  contrasts, case endings, verb forms, and high-frequency vocabulary.
- Reuse the **skills and vocabulary** of the covered topics, but never copy
  questions, sentences, or answer pairs from the original `exercises.yaml` or
  `test.yaml` files. Use fresh contexts, names, and sentence frames.
- Mix question types: multiple choice, fill-in-the-blank, translation, and
  sentence transformation, as appropriate for the level.
- Interleave topics: consecutive questions should usually come from different
  topics in the range.
- For `multiple_choice` questions, use exactly 3 options and distribute the
  correct answers across positions 1, 2, and 3 within the file.
- Make distractors plausible and wrong for one focused reason, ideally based
  on confusions between topics of the range.

Required YAML shape:

topic: Revisão {{TOPIC_RANGE}}
level: {{LEVEL}}
questions:
  - type: multiple_choice
    question: Qual frase está correta?
    options:
      - Ich sehe der Mann.
      - Ich sehe den Mann.
      - Ich sehe dem Mann.
    answer: Ich sehe den Mann.
