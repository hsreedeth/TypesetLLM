"""Public, versioned theme registry and RolePilot Markdown contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import yaml

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
ROLEPILOT_CONTRACT_VERSION = 1
_ALLOWED_METADATA = frozenset({"rolepilot_contract", "target_role", "target_employer"})
_FRONT_MATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


@dataclass(frozen=True)
class Theme:
    name: str
    version: str
    template: Path
    contract_version: int | None = None


THEMES = {
    name: Theme(name, version, TEMPLATES_DIR / f"{name}.tex", contract)
    for name, version, contract in (
        ("vintage", "legacy-1", None),
        ("rolepilot-resume", "1.0.0", ROLEPILOT_CONTRACT_VERSION),
        ("rolepilot-letter", "1.0.0", ROLEPILOT_CONTRACT_VERSION),
        ("rolepilot-criteria", "1.0.0", ROLEPILOT_CONTRACT_VERSION),
    )
}


def get_theme(name: str) -> Theme:
    if not isinstance(name, str) or name not in THEMES:
        raise ValueError(f"Unknown theme {name!r}. Supported themes: {', '.join(THEMES)}.")
    return THEMES[name]


def theme_catalog() -> dict[str, dict[str, str | int]]:
    return {
        name: {"version": theme.version, **({"contract_version": theme.contract_version} if theme.contract_version else {})}
        for name, theme in THEMES.items()
    }


def validate_rolepilot_markdown(markdown: str, theme: Theme) -> None:
    """Reject unsupported metadata; body text is never edited or suppressed."""
    if theme.contract_version is None:
        return
    match = _FRONT_MATTER.match(markdown)
    if not match:
        raise ValueError("RolePilot themes require YAML front matter with rolepilot_contract: 1.")
    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValueError("RolePilot YAML front matter is invalid.") from exc
    if not isinstance(metadata, dict):
        raise ValueError("RolePilot YAML front matter must be a mapping.")
    unknown = set(metadata) - _ALLOWED_METADATA
    if unknown:
        raise ValueError(f"Unsupported RolePilot metadata: {', '.join(sorted(map(str, unknown)))}.")
    if type(metadata.get("rolepilot_contract")) is not int or metadata["rolepilot_contract"] != theme.contract_version:
        raise ValueError(f"RolePilot contract version must be {theme.contract_version}.")
    for key in ("target_role", "target_employer"):
        if key in metadata and not isinstance(metadata[key], str):
            raise ValueError(f"RolePilot metadata {key} must be text.")
    if not markdown[match.end():].strip():
        raise ValueError("RolePilot document body is empty.")
