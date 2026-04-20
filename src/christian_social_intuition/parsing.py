from __future__ import annotations

"""Recover structured judgments and explanations from occasionally messy model outputs."""

import json
import re

from .schema import FOCUS_LABELS

JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)
STANDALONE_AB_RE = re.compile(r"\b([AB])\b", re.IGNORECASE)
WORD_RE = re.compile(r"\S+")

FOCUS_ALIASES = {
    "motive": "motive/heart",
    "heart": "motive/heart",
    "heart_worse": "motive/heart",
    "heart-worse": "motive/heart",
    "intention": "motive/heart",
    "motive/heart": "motive/heart",
    "act": "outward act/rule",
    "rule": "outward act/rule",
    "duty": "outward act/rule",
    "outward act/rule": "outward act/rule",
    "consequence": "consequences/harm",
    "consequences": "consequences/harm",
    "harm": "consequences/harm",
    "outcome": "consequences/harm",
    "consequences/harm": "consequences/harm",
    "relationship": "relationship/role",
    "role": "relationship/role",
    "loyalty": "relationship/role",
    "relationship/role": "relationship/role",
}


def _extract_json_payload(text: str) -> dict | None:
    text = text.strip()
    candidates = [text]
    match = JSON_BLOCK_RE.search(text)
    if match:
        candidates.append(match.group(0))
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None


def _normalize_choice(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().upper()
    if value in {"A", "B"}:
        return value
    match = re.search(r"\b(?:OPTION\s+)?([AB])\b", value, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def _truncate_words(text: str, limit: int = 25) -> str:
    words = WORD_RE.findall(text.strip())
    return " ".join(words[:limit])


def normalize_focus(value: str | None) -> str | None:
    if value is None:
        return None
    key = value.strip().lower()
    if key in FOCUS_ALIASES:
        return FOCUS_ALIASES[key]
    for alias, normalized in FOCUS_ALIASES.items():
        if alias in key:
            return normalized
    return None


def parse_judgment_text(text: str) -> tuple[str | None, str | None]:
    payload = _extract_json_payload(text)
    if isinstance(payload, dict):
        act = _normalize_choice(
            payload.get("overall_problematic")
            or payload.get("j1_act")
            or payload.get("j2_act")
            or payload.get("overall")
            or payload.get("act")
        )
        heart = _normalize_choice(
            payload.get("heart_worse")
            or payload.get("j1_heart")
            or payload.get("j2_heart")
            or payload.get("heart")
            or payload.get("motive")
        )
        if act or heart:
            return act, heart

    act_match = re.search(r"(overall|problematic|act)[^AB]*\b([AB])\b", text, re.IGNORECASE)
    heart_match = re.search(r"(heart|motive)[^AB]*\b([AB])\b", text, re.IGNORECASE)
    if act_match or heart_match:
        act = _normalize_choice(act_match.group(2) if act_match else None)
        heart = _normalize_choice(heart_match.group(2) if heart_match else None)
        return act, heart

    letters = [match.group(1).upper() for match in STANDALONE_AB_RE.finditer(text)]
    if len(letters) >= 2:
        return letters[0], letters[1]
    if len(letters) == 1:
        return letters[0], None
    return None, None


def parse_explanation_text(text: str) -> tuple[str | None, str | None]:
    payload = _extract_json_payload(text)
    if isinstance(payload, dict):
        focus = normalize_focus(payload.get("focus") or payload.get("e_focus"))
        sentence = payload.get("text") or payload.get("e_text")
        if sentence is not None:
            sentence = _truncate_words(str(sentence))
        if focus is None and sentence:
            focus = normalize_focus(sentence)
        if focus in FOCUS_LABELS or sentence:
            return focus, sentence
        # Some smaller models mistakenly repeat judgment JSON before the explanation sentence.
        text = JSON_BLOCK_RE.sub(" ", text, count=1)

    focus_match = re.search(r"(focus|basis)[^A-Za-z/]*([A-Za-z/ -]+)", text, re.IGNORECASE)
    focus = normalize_focus(focus_match.group(2) if focus_match else None)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sentence = None
    for line in lines:
        normalized_line_focus = normalize_focus(line)
        if normalized_line_focus and len(line.split()) <= 4:
            continue
        if "focus" in line.lower():
            continue
        sentence = line
        break
    if sentence is not None:
        sentence = _truncate_words(sentence)
    if focus is None and sentence:
        focus = normalize_focus(sentence)

    if focus in FOCUS_LABELS or sentence:
        return focus, sentence
    return None, None
