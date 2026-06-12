#!/usr/bin/env python3
"""Export flashcards.yaml files to an Anki deck (.apkg) with optional audio.

Builds one subdeck per topic: "Alemão::B2::104 partizip i como adjetivo".
Each note creates two cards: DE -> PT (recognition) and PT -> DE (production).
If scripts/generate-audio.py already produced clips under
output/audio/<topic>/cards/, they are embedded in the deck automatically.

Usage:
  .venv/bin/python scripts/export-anki.py                 # all topics
  .venv/bin/python scripts/export-anki.py 22 104          # by roadmap order
  .venv/bin/python scripts/export-anki.py --output meu-deck.apkg 99 100 101
  .venv/bin/python scripts/export-anki.py --csv           # also write CSVs
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (
    EXPORTS_ROOT,
    GERMAN_VOICE,
    audio_filename,
    resolve_topic_dirs,
    topic_audio_dir,
)

DECK_ROOT_NAME = "Alemão"
MODEL_ID = 1735201001


def stable_id(name: str) -> int:
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:10], 16)


def build_model():
    import genanki

    css = """
.card { font-family: sans-serif; font-size: 24px; text-align: center; color: #222; background: #fdfdfb; }
.example { font-size: 18px; color: #555; margin-top: 14px; }
.translation { font-size: 16px; color: #888; font-style: italic; }
"""
    return genanki.Model(
        MODEL_ID,
        "Alemão PT-BR (com áudio)",
        fields=[
            {"name": "Front"},
            {"name": "Back"},
            {"name": "Example"},
            {"name": "ExampleTranslation"},
            {"name": "FrontAudio"},
            {"name": "ExampleAudio"},
        ],
        templates=[
            {
                "name": "DE → PT",
                "qfmt": "{{Front}}<br>{{FrontAudio}}",
                "afmt": (
                    "{{FrontSide}}<hr id=answer>{{Back}}"
                    '<div class="example">{{Example}} {{ExampleAudio}}</div>'
                    '<div class="translation">{{ExampleTranslation}}</div>'
                ),
            },
            {
                "name": "PT → DE",
                "qfmt": "{{Back}}",
                "afmt": (
                    "{{FrontSide}}<hr id=answer>{{Front}} {{FrontAudio}}"
                    '<div class="example">{{Example}} {{ExampleAudio}}</div>'
                    '<div class="translation">{{ExampleTranslation}}</div>'
                ),
            },
        ],
        css=css,
    )


def find_audio(topic_dir: Path, text: str) -> Path | None:
    base = topic_audio_dir(topic_dir) / "cards"
    for extension in ("mp3", "wav"):
        candidate = base / audio_filename(text, GERMAN_VOICE, extension)
        if candidate.exists():
            return candidate
    return None


def deck_name_for(topic_dir: Path) -> str:
    level = topic_dir.parent.name.upper()
    title = topic_dir.name.replace("-", " ")
    return f"{DECK_ROOT_NAME}::{level}::{title}"


def load_cards(topic_dir: Path) -> list[dict]:
    path = topic_dir / "flashcards.yaml"
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: YAML inválido ignorado: {path} ({exc})")
        return []
    cards = data.get("cards") or []
    return [card for card in cards if isinstance(card, dict) and card.get("front")]


def export_csv(topic_dir: Path, cards: list[dict]) -> Path:
    out_dir = EXPORTS_ROOT / "anki-csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{topic_dir.name}.csv"
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        for card in cards:
            writer.writerow(
                [
                    card.get("front", ""),
                    card.get("back", ""),
                    card.get("example", ""),
                    card.get("example_translation", ""),
                ]
            )
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta flashcards para Anki.")
    parser.add_argument("topics", nargs="*", help="Números de ordem ou pastas de tópicos (vazio = todos)")
    parser.add_argument("--output", default=None, help="Arquivo .apkg de saída (padrão: output/exports/alemao.apkg)")
    parser.add_argument("--csv", action="store_true", help="Também exporta CSVs por tópico (sem áudio)")
    args = parser.parse_args()

    try:
        import genanki
    except ImportError:
        print("Erro: genanki não instalado. Rode: uv pip install --python .venv/bin/python -r requirements.txt")
        return 2

    topic_dirs = resolve_topic_dirs(args.topics)
    model = build_model()
    decks = []
    media_files: list[str] = []
    total_notes = 0
    skipped: list[str] = []

    for topic_dir in topic_dirs:
        cards = load_cards(topic_dir)
        if not cards:
            skipped.append(topic_dir.name)
            continue

        deck_name = deck_name_for(topic_dir)
        deck = genanki.Deck(stable_id(deck_name), deck_name)

        for card in cards:
            fields = {
                "Front": str(card.get("front", "")),
                "Back": str(card.get("back", "")),
                "Example": str(card.get("example", "")),
                "ExampleTranslation": str(card.get("example_translation", "")),
                "FrontAudio": "",
                "ExampleAudio": "",
            }
            for text_field, audio_field in (("Front", "FrontAudio"), ("Example", "ExampleAudio")):
                text = fields[text_field].strip()
                if not text:
                    continue
                audio_path = find_audio(topic_dir, text)
                if audio_path:
                    fields[audio_field] = f"[sound:{audio_path.name}]"
                    media_files.append(str(audio_path))

            note = genanki.Note(
                model=model,
                fields=list(fields.values()),
                guid=genanki.guid_for(topic_dir.name, fields["Front"]),
                tags=[topic_dir.parent.name, topic_dir.name],
            )
            deck.add_note(note)
            total_notes += 1

        decks.append(deck)
        if args.csv:
            export_csv(topic_dir, cards)

    if not decks:
        print("Nenhum flashcard encontrado para exportar.")
        return 1

    EXPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output) if args.output else EXPORTS_ROOT / "alemao.apkg"
    package = genanki.Package(decks)
    package.media_files = sorted(set(media_files))
    package.write_to_file(str(output_path))

    print(f"Exportado: {output_path}")
    print(f"- {len(decks)} subdeck(s), {total_notes} nota(s), {len(set(media_files))} arquivo(s) de áudio")
    if skipped:
        print(f"- Sem flashcards (pulados): {', '.join(skipped)}")
    if args.csv:
        print(f"- CSVs em {EXPORTS_ROOT / 'anki-csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
