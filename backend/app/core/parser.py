"""Tree-sitter parser utilities for Insight."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from tree_sitter import Tree
from tree_sitter_languages import get_parser

from app.core.language_config import get_language_config, normalize_language


class UnsupportedLanguageError(ValueError):
    pass


@lru_cache(maxsize=64)
def _load_parser(grammar_name: str) -> Any:
    return get_parser(grammar_name)


def parse_code(code: str, language: str | None) -> Tree:
    """
    Parse source code into a Tree-sitter tree.

    Raises:
        ValueError: if code is empty.
        UnsupportedLanguageError: if the language cannot be mapped to a grammar.
        RuntimeError: if Tree-sitter fails to load or parse the grammar.
    """
    if not code or not code.strip():
        raise ValueError("Cannot parse empty code")

    config = get_language_config(language)
    if config is None:
        normalized = normalize_language(language)
        raise UnsupportedLanguageError(f"Unsupported language for AST parsing: {normalized}")

    try:
        parser = _load_parser(config.grammar_name)
        return parser.parse(bytes(code, "utf8"))
    except Exception as exc:
        raise RuntimeError(f"Tree-sitter parse failed for {config.display_name}: {exc}") from exc
