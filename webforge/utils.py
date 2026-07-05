from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any


SECRET_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{12,})"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
)


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, value: Any) -> None:
    ensure_dir(path.parent)
    text = json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == text:
        return
    path.write_text(text, encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    final_text = text.rstrip() + "\n"
    if path.exists() and path.read_text(encoding="utf-8", errors="replace") == final_text:
        return
    path.write_text(final_text, encoding="utf-8")


def append_jsonl(path: Path, value: Any) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(stable_json(value) + "\n")


def read_text(path: Path, max_chars: int | None = None) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if max_chars is not None:
        return text[:max_chars]
    return text


def redact_secrets(text: str) -> tuple[str, int]:
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        count += 1
        if len(match.groups()) >= 2:
            return match.group(0).replace(match.group(2), "[REDACTED]")
        return "[REDACTED]"

    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(repl, redacted)
    return redacted, count


def find_secret_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            hits.append(match.group(0)[:24] + ("..." if len(match.group(0)) > 24 else ""))
    return hits


def discover_design_sources(root: Path) -> list[Path]:
    names = {
        "Diseno_detallado_fabrica_software_SDD-2.md",
        "Diseno_detallado_arnes_dev_legacy-2.md",
        "Diseno_detallado_orquestador_maestro_SDD-2.md",
        "Diseno_detallado_agentes_y_skills_software-2.md",
        "CheckList_Implementacion_software-2.md",
    }

    def ascii_name(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        return "".join(char for char in normalized if not unicodedata.combining(char))

    sources: list[Path] = []
    for candidate in root.glob("*.md"):
        if ascii_name(candidate.name) in names:
            sources.append(candidate)
    return sorted(set(sources))


def short_hash(value: Any, size: int = 12) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()[:size]
