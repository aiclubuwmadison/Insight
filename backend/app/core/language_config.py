"""
Language normalization and Tree-sitter grammar configuration.

This module maps editor/language IDs such as "py", "js", and "typescriptreact"
to the grammar names expected by tree_sitter_languages.get_parser().
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LanguageConfig:
    display_name: str
    grammar_name: str
    aliases: tuple[str, ...]


LANGUAGE_CONFIGS: dict[str, LanguageConfig] = {
    "python": LanguageConfig("Python", "python", ("py", "python3")),
    "javascript": LanguageConfig("JavaScript", "javascript", ("js", "jsx", "node")),
    "typescript": LanguageConfig("TypeScript", "typescript", ("ts", "tsx", "typescriptreact")),
    "java": LanguageConfig("Java", "java", ()),
    "c": LanguageConfig("C", "c", ()),
    "cpp": LanguageConfig("C++", "cpp", ("c++", "cc", "cxx", "hpp", "h++")),
    "c_sharp": LanguageConfig("C#", "c_sharp", ("c#", "cs", "csharp")),
    "go": LanguageConfig("Go", "go", ("golang",)),
    "rust": LanguageConfig("Rust", "rust", ("rs",)),
    "ruby": LanguageConfig("Ruby", "ruby", ("rb",)),
    "php": LanguageConfig("PHP", "php", ()),
    "swift": LanguageConfig("Swift", "swift", ()),
    "kotlin": LanguageConfig("Kotlin", "kotlin", ("kt",)),
    "scala": LanguageConfig("Scala", "scala", ()),
    "r": LanguageConfig("R", "r", ("rscript",)),
    "bash": LanguageConfig("Bash", "bash", ("sh", "shell", "zsh")),
    "html": LanguageConfig("HTML", "html", ()),
    "css": LanguageConfig("CSS", "css", ()),
    "json": LanguageConfig("JSON", "json", ()),
    "yaml": LanguageConfig("YAML", "yaml", ("yml",)),
    "toml": LanguageConfig("TOML", "toml", ()),
    "xml": LanguageConfig("XML", "xml", ()),
    "sql": LanguageConfig("SQL", "sql", ()),
    "markdown": LanguageConfig("Markdown", "markdown", ("md",)),
    "dockerfile": LanguageConfig("Dockerfile", "dockerfile", ("docker",)),
    "lua": LanguageConfig("Lua", "lua", ()),
    "perl": LanguageConfig("Perl", "perl", ("pl",)),
    "haskell": LanguageConfig("Haskell", "haskell", ("hs",)),
    "elixir": LanguageConfig("Elixir", "elixir", ("ex", "exs")),
    "erlang": LanguageConfig("Erlang", "erlang", ("erl",)),
    "ocaml": LanguageConfig("OCaml", "ocaml", ("ml",)),
    "clojure": LanguageConfig("Clojure", "clojure", ("clj",)),
    "dart": LanguageConfig("Dart", "dart", ()),
    "fortran": LanguageConfig("Fortran", "fortran", ("f90", "f95")),
    "julia": LanguageConfig("Julia", "julia", ("jl",)),
    "nim": LanguageConfig("Nim", "nim", ()),
    "zig": LanguageConfig("Zig", "zig", ()),
    "solidity": LanguageConfig("Solidity", "solidity", ("sol",)),
    "verilog": LanguageConfig("Verilog", "verilog", ("sv", "systemverilog")),
    "vue": LanguageConfig("Vue", "vue", ()),
    "svelte": LanguageConfig("Svelte", "svelte", ()),
    "regex": LanguageConfig("Regex", "regex", ("regexp",)),
    "make": LanguageConfig("Make", "make", ("makefile",)),
    "cmake": LanguageConfig("CMake", "cmake", ()),
    "latex": LanguageConfig("LaTeX", "latex", ("tex",)),
    "graphql": LanguageConfig("GraphQL", "graphql", ("gql",)),
    "proto": LanguageConfig("Protocol Buffers", "proto", ("protobuf",)),
    "embedded_template": LanguageConfig("Embedded Template", "embedded_template", ("erb",)),
    "elm": LanguageConfig("Elm", "elm", ()),
    "hack": LanguageConfig("Hack", "hack", ()),
    "ql": LanguageConfig("QL", "ql", ()),
    "scheme": LanguageConfig("Scheme", "scheme", ("scm",)),
}

_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, config in LANGUAGE_CONFIGS.items():
    _ALIAS_TO_CANONICAL[canonical] = canonical
    _ALIAS_TO_CANONICAL[config.grammar_name] = canonical
    for alias in config.aliases:
        _ALIAS_TO_CANONICAL[alias] = canonical


def normalize_language(language: str | None) -> str:
    """Return the canonical language key used by this backend."""
    if not language:
        return "unknown"

    key = language.strip().lower().replace(" ", "_").replace("-", "_")
    return _ALIAS_TO_CANONICAL.get(key, "unknown")


def get_language_config(language: str | None) -> LanguageConfig | None:
    canonical = normalize_language(language)
    if canonical == "unknown":
        return None
    return LANGUAGE_CONFIGS.get(canonical)


def supported_languages() -> list[str]:
    return sorted(LANGUAGE_CONFIGS.keys())
