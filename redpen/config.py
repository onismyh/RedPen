"""Configuration loading from ~/.redpen.toml."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

CONFIG_PATH = Path.home() / ".redpen.toml"


@dataclass
class Config:
    author: str = "AI Reviewer"

    # apply defaults
    add_comments: bool = True


def load_config() -> Config:
    """Load config from ~/.redpen.toml, falling back to defaults."""
    cfg = Config()
    if not CONFIG_PATH.exists():
        return cfg

    with open(CONFIG_PATH, "rb") as f:
        data = tomllib.load(f)

    default = data.get("default", {})
    if "author" in default:
        cfg.author = default["author"]
    if "add_comments" in default:
        cfg.add_comments = default["add_comments"]

    return cfg
