#!/usr/bin/env python3
from __future__ import annotations

import math
import re
import sys
import unicodedata
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOPICS_ROOT = REPO_ROOT / "topics"
YAML_SOURCE_FILES = (
    "vocabulary.yaml",
    "flashcards.yaml",
    "exercises.yaml",
    "test.yaml",
)

ENGLISH_MARKDOWN_LABELS = {
    "# Story:",
    "# Answers:",
    "Level:",
    "## Goal",
    "## Explanation",
    "## Examples",
    "## Common mistakes",
    "## Summary",
    "## German Story",
    "## Line-by-line translation",
    "## Vocabulary notes",
    "## Comprehension questions",
    "## Exercises answer key",
    "## Test answer key",
    "## Story questions",
    "| German | Translation | Note |",
    "| German | Translation |",
    "| ID | Answer | Note |",
    "| ID | Answer | Points |",
    "| Question | Answer |",
}

COMMAND_PREFIX_RE = re.compile(
    r"^(transforme|traduza|complete|corrija|ordene|responda)\b\s*:?\s*",
    flags=re.IGNORECASE,
)


def issue(issues: list[str], path: Path, message: str) -> None:
    issues.append(f"{path.relative_to(REPO_ROOT)}: {message}")


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = COMMAND_PREFIX_RE.sub("", text)
    text = text.replace("ß", "ss")
    text = re.sub(r"[_\"'“”.,!?;:()\[\]{}<>/\\|-]+", " ", text)
    return " ".join(text.split())


def looks_reused(left: object, right: object) -> bool:
    left_norm = normalize_text(left)
    right_norm = normalize_text(right)
    if not left_norm or not right_norm:
        return False
    if left_norm == right_norm and len(left_norm) >= 6:
        return True
    shorter, longer = sorted((left_norm, right_norm), key=len)
    return len(shorter) >= 12 and shorter in longer


def load_yaml(path: Path, issues: list[str]) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - validation should report parser details.
        issue(issues, path, f"YAML inválido: {exc}")
        return {}


def topic_dirs(paths: list[Path]) -> list[Path]:
    if not paths:
        paths = [DEFAULT_TOPICS_ROOT]

    found: set[Path] = set()
    for path in paths:
        path = path.resolve()
        if path.is_file():
            path = path.parent
        if (path / "lesson.md").exists():
            found.add(path)
            continue
        if path.is_dir():
            for lesson in path.rglob("lesson.md"):
                found.add(lesson.parent)

    return sorted(found)


def iter_exercise_items(exercises_data: object):
    if not isinstance(exercises_data, dict):
        return
    for group_index, group in enumerate(exercises_data.get("exercises", []) or [], start=1):
        if not isinstance(group, dict):
            continue
        for item_index, item in enumerate(group.get("items", []) or [], start=1):
            if isinstance(item, dict):
                yield f"{group_index}.{item_index}", item


def iter_test_questions(test_data: object):
    if not isinstance(test_data, dict):
        return
    for question_index, question in enumerate(test_data.get("questions", []) or [], start=1):
        if isinstance(question, dict):
            yield str(question_index), question


def check_reused_test_items(topic_dir: Path, issues: list[str], exercises_data: object, test_data: object) -> None:
    exercise_items = list(iter_exercise_items(exercises_data))
    for test_id, question in iter_test_questions(test_data):
        test_question = question.get("question", "")
        test_answer = question.get("answer", "")
        for exercise_id, item in exercise_items:
            same_question = looks_reused(test_question, item.get("question", ""))
            same_pair = same_question and looks_reused(test_answer, item.get("answer", ""))
            if same_question or same_pair:
                issue(
                    issues,
                    topic_dir / "test.yaml",
                    f"questão {test_id} parece repetir o exercício {exercise_id}",
                )
                break


def check_multiple_choice_distribution(path: Path, label: str, rows: list[tuple[str, dict]], issues: list[str]) -> None:
    positions: list[int] = []
    for item_id, item in rows:
        options = item.get("options")
        if not options:
            continue
        if not isinstance(options, list):
            issue(issues, path, f"{label} {item_id} tem `options` que não é lista")
            continue
        if len(options) != 3:
            issue(issues, path, f"{label} {item_id} tem {len(options)} opções; use 3 por padrão")
        answer = item.get("answer")
        try:
            position = [normalize_text(option) for option in options].index(normalize_text(answer)) + 1
        except ValueError:
            issue(issues, path, f"{label} {item_id} tem resposta que não aparece nas opções")
            continue
        positions.append(position)

    total = len(positions)
    if total < 3:
        return

    counts = {position: positions.count(position) for position in (1, 2, 3)}
    if counts[3] == 0:
        issue(issues, path, "nenhuma resposta correta está na posição 3")
    if total >= 4 and any(count == 0 for count in counts.values()):
        issue(issues, path, f"distribuição de respostas pouco variada: {counts}")
    if total >= 4 and max(counts.values()) > math.ceil(total * 0.7):
        issue(issues, path, f"respostas corretas concentradas demais: {counts}")


def check_multiple_choice(topic_dir: Path, issues: list[str], exercises_data: object, test_data: object) -> None:
    exercise_rows = [(item_id, item) for item_id, item in iter_exercise_items(exercises_data)]
    test_rows = [(item_id, item) for item_id, item in iter_test_questions(test_data)]
    check_multiple_choice_distribution(topic_dir / "exercises.yaml", "exercício", exercise_rows, issues)
    check_multiple_choice_distribution(topic_dir / "test.yaml", "questão", test_rows, issues)


def markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading == -1:
        return text[start:]
    return text[start:next_heading]


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def check_answer_explanations(topic_dir: Path, issues: list[str]) -> None:
    path = topic_dir / "answers.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")

    for heading in ("## Gabarito dos exercícios", "## Gabarito do teste"):
        section = markdown_section(text, heading)
        if not section:
            issue(issues, path, f"seção ausente: {heading}")
            continue

        lines = [line for line in section.splitlines() if line.startswith("|")]
        if len(lines) < 2:
            issue(issues, path, f"{heading} não tem tabela de respostas")
            continue

        headers = split_markdown_row(lines[0])
        explanation_index = next(
            (index for index, header in enumerate(headers) if header.casefold() in {"explicação", "observação"}),
            None,
        )
        if explanation_index is None:
            issue(issues, path, f"{heading} não tem coluna de explicação")
            continue

        for line_number, line in enumerate(lines[2:], start=3):
            cells = split_markdown_row(line)
            if len(cells) <= explanation_index or not cells[explanation_index]:
                issue(issues, path, f"{heading}, linha de tabela {line_number}, explicação vazia")


def check_markdown_labels(topic_dir: Path, issues: list[str]) -> None:
    for name in ("lesson.md", "story.md", "answers.md"):
        path = topic_dir / name
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped in ENGLISH_MARKDOWN_LABELS or any(stripped.startswith(prefix) for prefix in ("# Story:", "# Answers:")):
                issue(issues, path, f"rótulo em inglês na linha {line_number}: {stripped}")


def validate_topic(topic_dir: Path, issues: list[str]) -> None:
    parsed_yaml: dict[str, object] = {}
    for name in YAML_SOURCE_FILES:
        path = topic_dir / name
        if path.exists():
            parsed_yaml[name] = load_yaml(path, issues)
        else:
            issue(issues, path, "arquivo obrigatório ausente")

    check_markdown_labels(topic_dir, issues)
    check_answer_explanations(topic_dir, issues)
    check_reused_test_items(
        topic_dir,
        issues,
        parsed_yaml.get("exercises.yaml", {}),
        parsed_yaml.get("test.yaml", {}),
    )
    check_multiple_choice(
        topic_dir,
        issues,
        parsed_yaml.get("exercises.yaml", {}),
        parsed_yaml.get("test.yaml", {}),
    )


def main(argv: list[str]) -> int:
    baseline_path: Path | None = None
    paths: list[Path] = []
    args = iter(argv)
    for arg in args:
        if arg == "--baseline":
            try:
                baseline_path = Path(next(args))
            except StopIteration:
                print("Erro: --baseline requer um arquivo.", file=sys.stderr)
                return 2
        else:
            paths.append(Path(arg))

    issues: list[str] = []
    topics = topic_dirs(paths)

    if not topics:
        print("Nenhum tópico encontrado.", file=sys.stderr)
        return 2

    for topic_dir in topics:
        validate_topic(topic_dir, issues)

    if baseline_path and baseline_path.exists():
        known = {
            line.strip()
            for line in baseline_path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
        ignored = [item for item in issues if item in known]
        issues = [item for item in issues if item not in known]
        if ignored:
            print(f"({len(ignored)} problema(s) conhecidos ignorados pela baseline)")

    if issues:
        print(f"Content QA encontrou {len(issues)} problema(s):")
        for item in issues:
            print(f"- {item}")
        return 1

    print(f"Content QA OK: {len(topics)} tópico(s) verificado(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
