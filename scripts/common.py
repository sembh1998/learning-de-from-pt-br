#!/usr/bin/env python3
"""Shared helpers for topic resolution and audio file naming."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOPICS_ROOT = REPO_ROOT / "topics"
AUDIO_ROOT = REPO_ROOT / "output" / "audio"
EXPORTS_ROOT = REPO_ROOT / "output" / "exports"

GERMAN_VOICE = "de_DE-karlsson-low"
PORTUGUESE_VOICE = "pt_BR-cadu-medium"
VOICES_DIR = REPO_ROOT / ".cache" / "piper-voices"


def resolve_topic_dirs(args: list[str]) -> list[Path]:
    """Resolve CLI args (topic numbers or folder paths) to topic directories.

    With no args, returns every topic folder containing a lesson.md.
    """
    if not args:
        return sorted(
            lesson.parent for lesson in TOPICS_ROOT.rglob("lesson.md")
        )

    found: list[Path] = []
    for arg in args:
        if re.fullmatch(r"\d+", arg):
            order = f"{int(arg):03d}"
            matches = sorted(TOPICS_ROOT.glob(f"*/{order}-*"))
            if not matches:
                raise SystemExit(f"Erro: nenhum tópico encontrado para a ordem {arg}.")
            if len(matches) > 1:
                listing = "\n  ".join(str(m) for m in matches)
                raise SystemExit(f"Erro: múltiplos tópicos para a ordem {arg}:\n  {listing}")
            found.append(matches[0])
        else:
            path = Path(arg).resolve()
            if not path.is_dir():
                raise SystemExit(f"Erro: pasta de tópico não encontrada: {arg}")
            found.append(path)
    return found


def audio_filename(text: str, voice: str, extension: str = "wav") -> str:
    """Deterministic audio file name for a snippet of spoken text.

    Both generate-audio.py and export-anki.py use this so exported decks
    reference the exact files produced by the TTS step.
    """
    digest = hashlib.sha1(f"{voice}|{text}".encode("utf-8")).hexdigest()[:16]
    return f"{digest}.{extension}"


def topic_audio_dir(topic_dir: Path) -> Path:
    return AUDIO_ROOT / topic_dir.name
