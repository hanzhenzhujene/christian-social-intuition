from __future__ import annotations

"""Lexical-echo and controlled-semantic explanation metrics used in the paper."""

import re
from typing import Iterable


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    lowered = text.lower()
    return re.sub(r"\s+", " ", lowered).strip()


def _contains_term(text: str, term: str) -> bool:
    if not term:
        return False
    pattern = re.escape(term.lower())
    return re.search(rf"(?<!\w){pattern}(?!\w)", text) is not None


def count_term_hits(text: str | None, terms: Iterable[str]) -> int:
    normalized = normalize_text(text)
    if not normalized:
        return 0
    return sum(1 for term in terms if _contains_term(normalized, term))


def matched_terms(text: str | None, terms: Iterable[str]) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    matches: list[str] = []
    for term in terms:
        if _contains_term(normalized, term):
            matches.append(term)
    return matches


def strip_terms(text: str | None, terms: Iterable[str]) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return ""
    stripped = normalized
    for term in terms:
        if not term:
            continue
        pattern = re.compile(rf"(?<!\w){re.escape(term.lower())}(?!\w)")
        stripped = pattern.sub(" ", stripped)
    return re.sub(r"\s+", " ", stripped).strip()


def compute_explanation_metrics(
    text: str | None,
    *,
    strict_echo_terms: Iterable[str],
    non_echo_semantic_terms: Iterable[str],
) -> dict[str, int]:
    strict_terms = list(strict_echo_terms)
    semantic_terms = list(non_echo_semantic_terms)
    frame_echo_score = count_term_hits(text, strict_terms)
    semantic_non_echo_score = count_term_hits(text, semantic_terms)
    semantic_score_raw = frame_echo_score + semantic_non_echo_score

    stripped = strip_terms(text, strict_terms)
    semantic_score_controlled = count_term_hits(stripped, semantic_terms)

    return {
        "frame_echo_score": frame_echo_score,
        "frame_echo_present": int(frame_echo_score > 0),
        "semantic_score_raw": semantic_score_raw,
        "semantic_raw_present": int(semantic_score_raw > 0),
        "semantic_score_controlled": semantic_score_controlled,
        "semantic_controlled_present": int(semantic_score_controlled > 0),
        "restructure_beyond_echo": int(frame_echo_score == 0 and semantic_score_controlled > 0),
    }
