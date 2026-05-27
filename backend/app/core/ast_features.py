"""Feature extraction over Tree-sitter ASTs."""

from __future__ import annotations

from collections import Counter, deque
from typing import Any

LOOP_TYPES = {
    "for_statement", "while_statement", "do_statement", "enhanced_for_statement",
    "for_in_statement", "for_each_statement", "foreach_statement", "repeat_statement",
}
CONDITIONAL_TYPES = {
    "if_statement", "elif_clause", "else_clause", "switch_statement", "case_statement",
    "match_statement", "conditional_expression", "ternary_expression",
}
FUNCTION_TYPES = {
    "function_definition", "function_declaration", "method_definition", "method_declaration",
    "arrow_function", "lambda", "lambda_expression", "function_item", "constructor_declaration",
}
CALL_TYPES = {"call", "call_expression", "method_invocation", "invocation_expression"}
RETURN_TYPES = {"return_statement", "yield", "yield_expression"}
ASSIGNMENT_TYPES = {"assignment", "assignment_expression", "augmented_assignment_expression"}
BINARY_TYPES = {"binary_expression", "boolean_operator", "comparison_operator"}
COLLECTION_TYPES = {
    "list", "list_comprehension", "dictionary", "dictionary_comprehension", "set", "array",
    "array_creation_expression", "object", "map", "hash", "tuple",
}

FEATURE_KEYS = [
    "total_nodes", "unique_node_types", "max_depth", "avg_branching_factor",
    "loop_count", "conditional_count", "function_count", "call_count", "return_count",
    "assignment_count", "binary_expression_count", "collection_count", "identifier_count",
    "literal_count", "comment_count", "nested_loop_count", "max_loop_depth",
    "has_function", "has_loop", "has_conditional", "has_collection", "has_recursion_signal",
]


def _safe_node_text(node: Any, source_bytes: bytes) -> str:
    try:
        return source_bytes[node.start_byte:node.end_byte].decode("utf8", errors="ignore")
    except Exception:
        return ""


def extract_ast_features(root_node: Any, source_code: str = "") -> dict[str, float]:
    """Walk an AST and return numeric structural features for ML inference."""
    source_bytes = source_code.encode("utf8")
    counter: Counter[str] = Counter()
    identifier_names: Counter[str] = Counter()

    total_children = 0
    non_leaf_nodes = 0
    max_depth = 0
    nested_loop_count = 0
    max_loop_depth = 0

    queue = deque([(root_node, 0, 0)])  # node, depth, active loop depth

    while queue:
        node, depth, loop_depth = queue.popleft()
        node_type = getattr(node, "type", "unknown")
        counter[node_type] += 1
        max_depth = max(max_depth, depth)

        children = list(getattr(node, "children", []) or [])
        if children:
            non_leaf_nodes += 1
            total_children += len(children)

        next_loop_depth = loop_depth
        if node_type in LOOP_TYPES:
            next_loop_depth = loop_depth + 1
            max_loop_depth = max(max_loop_depth, next_loop_depth)
            if loop_depth > 0:
                nested_loop_count += 1

        if node_type in {"identifier", "property_identifier"}:
            text = _safe_node_text(node, source_bytes)
            if text:
                identifier_names[text] += 1

        for child in children:
            queue.append((child, depth + 1, next_loop_depth))

    total_nodes = sum(counter.values())
    avg_branching_factor = total_children / non_leaf_nodes if non_leaf_nodes else 0.0

    function_names = {name for name, count in identifier_names.items() if count >= 2}
    has_recursion_signal = 1 if function_names and _looks_recursive(source_code, function_names) else 0

    features = {
        "total_nodes": float(total_nodes),
        "unique_node_types": float(len(counter)),
        "max_depth": float(max_depth),
        "avg_branching_factor": float(avg_branching_factor),
        "loop_count": float(sum(counter[t] for t in LOOP_TYPES)),
        "conditional_count": float(sum(counter[t] for t in CONDITIONAL_TYPES)),
        "function_count": float(sum(counter[t] for t in FUNCTION_TYPES)),
        "call_count": float(sum(counter[t] for t in CALL_TYPES)),
        "return_count": float(sum(counter[t] for t in RETURN_TYPES)),
        "assignment_count": float(sum(counter[t] for t in ASSIGNMENT_TYPES)),
        "binary_expression_count": float(sum(counter[t] for t in BINARY_TYPES)),
        "collection_count": float(sum(counter[t] for t in COLLECTION_TYPES)),
        "identifier_count": float(counter["identifier"] + counter["property_identifier"]),
        "literal_count": float(sum(count for node_type, count in counter.items() if "literal" in node_type or node_type in {"string", "integer", "float", "true", "false"})),
        "comment_count": float(counter["comment"]),
        "nested_loop_count": float(nested_loop_count),
        "max_loop_depth": float(max_loop_depth),
        "has_function": 1.0 if sum(counter[t] for t in FUNCTION_TYPES) else 0.0,
        "has_loop": 1.0 if sum(counter[t] for t in LOOP_TYPES) else 0.0,
        "has_conditional": 1.0 if sum(counter[t] for t in CONDITIONAL_TYPES) else 0.0,
        "has_collection": 1.0 if sum(counter[t] for t in COLLECTION_TYPES) else 0.0,
        "has_recursion_signal": float(has_recursion_signal),
    }

    return {key: features.get(key, 0.0) for key in FEATURE_KEYS}


def _looks_recursive(source_code: str, repeated_identifiers: set[str]) -> bool:
    """Simple source-level recursion signal used as a feature, not a final decision."""
    lowered = source_code.lower()
    for name in repeated_identifiers:
        if not name or len(name) < 3:
            continue
        token = name.lower()
        if f"def {token}" in lowered and f"{token}(" in lowered:
            return True
        if f"function {token}" in lowered and f"{token}(" in lowered:
            return True
    return False
