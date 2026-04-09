from __future__ import annotations

import csv
import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from .moral_stories import load_moral_stories
from .schema import ItemRecord, TENSION_TAGS

WORD_RE = re.compile(r"[A-Za-z']+")
ABSURD_BLACKLIST = {"dragon", "wizard", "alien", "spaceship", "zombie", "magic"}
RELIGIOUS_LEXICON = {
    "christian",
    "church",
    "jesus",
    "bible",
    "pastor",
    "prayer",
    "satanism",
    "ultra-religious",
}
TEXT_REPLACEMENTS = {
    '""': '"',
    " grab's ": " grabs ",
    " Robs ": " Rob's ",
    "Robs friends": "Rob's friends",
    "Amy's end up": "Amy ends up",
    "pretty ladies shoes": "pretty lady's shoes",
    "the officers instructions": "the officer's instructions",
    "Shawns wants": "Shawn wants",
    "Mark annoyed at the cop": "Marcus, annoyed at the cop",
}
PROSOCIAL_KEYWORDS = {
    "safe",
    "safety",
    "protect",
    "help",
    "care",
    "respect",
    "support",
    "family",
    "friend",
    "child",
    "children",
    "loyal",
    "honest",
    "kind",
}
SELFISH_KEYWORDS = {
    "money",
    "win",
    "wager",
    "cash",
    "fame",
    "pleasure",
    "fun",
    "enjoy",
    "impress",
    "popular",
    "attention",
    "reward",
    "self",
}
HARM_KEYWORDS = {
    "hurt",
    "shock",
    "injure",
    "pain",
    "cry",
    "upset",
    "angry",
    "lose",
    "late",
    "damage",
    "steal",
    "betray",
    "lie",
    "break",
    "harm",
}
RELATIONAL_KEYWORDS = {
    "mother",
    "father",
    "wife",
    "husband",
    "friend",
    "teacher",
    "coworker",
    "boss",
    "neighbor",
    "kids",
    "children",
    "partner",
    "family",
}


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text)]


def _word_count(text: str) -> int:
    return len(_tokens(text))


def _lexical_overlap(left: str, right: str) -> float:
    left_set = set(_tokens(left))
    right_set = set(_tokens(right))
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def _contains_any(text: str, keywords: set[str]) -> bool:
    bag = set(_tokens(text))
    return bool(bag & keywords)


def _normalize_sentence(text: str) -> str:
    text = " ".join(text.strip().split())
    if not text:
        return text
    if text.startswith('"') and text.endswith('"') and len(text) >= 2:
        text = text[1:-1]
    for old, new in TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r'([!?])"\.$', r'\1"', text)
    text = text.replace('!".', '!"').replace('?".', '?"')
    if text.endswith('"') and len(text) >= 2 and text[-2] in ".!?":
        return text
    if text[-1] not in ".!?":
        text += "."
    return text


def _scenario_context(record: dict) -> str:
    situation = _normalize_sentence(record["situation"])
    intention = _normalize_sentence(record["intention"])
    return f"{situation} Goal: {intention}"


def infer_tension_tag(record: dict) -> tuple[str, float]:
    intention = record["intention"]
    moral_action = record["moral_action"]
    immoral_action = record["immoral_action"]
    moral_consequence = record["moral_consequence"]
    immoral_consequence = record["immoral_consequence"]

    if _contains_any(intention, PROSOCIAL_KEYWORDS) and _contains_any(
        f"{immoral_action} {immoral_consequence}", HARM_KEYWORDS
    ):
        return "bad_act_good_motive", 0.82
    if _contains_any(intention, SELFISH_KEYWORDS):
        return "good_act_bad_motive", 0.62
    if _lexical_overlap(moral_action, immoral_action) >= 0.45:
        return "appearance_vs_intention", 0.71
    if (
        _contains_any(moral_consequence, RELATIONAL_KEYWORDS)
        and _contains_any(immoral_consequence, RELATIONAL_KEYWORDS)
    ) or _contains_any(record["situation"], RELATIONAL_KEYWORDS):
        return "mixed_stakeholder_context", 0.58
    return "motive_vs_outcome", 0.54


def candidate_score(record: dict, tag: str, confidence: float) -> float:
    situation = record["situation"]
    intention = record["intention"]
    moral_action = record["moral_action"]
    immoral_action = record["immoral_action"]
    moral_consequence = record["moral_consequence"]
    immoral_consequence = record["immoral_consequence"]

    score = 0.0
    score += min(_word_count(situation), 28) / 28
    score += min(_word_count(intention), 14) / 14
    score += 0.8 * _lexical_overlap(moral_action, immoral_action)
    score += 0.4 * abs(_word_count(moral_consequence) - _word_count(immoral_consequence)) / 12
    score += confidence
    if tag != "motive_vs_outcome":
        score += 0.25
    return round(score, 4)


def _is_everyday(record: dict) -> bool:
    all_text = " ".join(
        [
            record["norm"],
            record["situation"],
            record["intention"],
            record["moral_action"],
            record["moral_consequence"],
            record["immoral_action"],
            record["immoral_consequence"],
        ]
    ).lower()
    if any(word in all_text for word in ABSURD_BLACKLIST):
        return False
    if any(word in all_text for word in RELIGIOUS_LEXICON):
        return False
    return 6 <= _word_count(record["situation"]) <= 40 and 4 <= _word_count(record["intention"]) <= 18


def flip_item_options(item: ItemRecord) -> None:
    item.option_a, item.option_b = item.option_b, item.option_a
    item.option_a_alignment, item.option_b_alignment = item.option_b_alignment, item.option_a_alignment
    item.moral_option = "A" if item.option_a_alignment == "moral" else "B"


def rebalance_option_order(items: list[ItemRecord], *, seed: int = 42) -> list[ItemRecord]:
    rng = random.Random(seed)
    grouped: dict[str, list[ItemRecord]] = defaultdict(list)
    for item in items:
        grouped[item.primary_tension_tag].append(item)

    for bucket in grouped.values():
        rng.shuffle(bucket)
        a_count = sum(item.moral_option == "A" for item in bucket)
        target_a = len(bucket) // 2
        if len(bucket) % 2 == 1 and a_count > target_a:
            target_a += 1

        if a_count > target_a:
            need = a_count - target_a
            for item in [row for row in bucket if row.moral_option == "A"][:need]:
                flip_item_options(item)
        elif a_count < target_a:
            need = target_a - a_count
            for item in [row for row in bucket if row.moral_option == "B"][:need]:
                flip_item_options(item)

    target_total_a = len(items) // 2
    current_total_a = sum(item.moral_option == "A" for item in items)
    if current_total_a > target_total_a:
        candidates = []
        for bucket in grouped.values():
            a_count = sum(item.moral_option == "A" for item in bucket)
            if a_count > len(bucket) // 2:
                candidates.extend([item for item in bucket if item.moral_option == "A"])
        rng.shuffle(candidates)
        for item in candidates[: current_total_a - target_total_a]:
            flip_item_options(item)
    elif current_total_a < target_total_a:
        candidates = []
        for bucket in grouped.values():
            a_count = sum(item.moral_option == "A" for item in bucket)
            if a_count < math.ceil(len(bucket) / 2):
                candidates.extend([item for item in bucket if item.moral_option == "B"])
        rng.shuffle(candidates)
        for item in candidates[: target_total_a - current_total_a]:
            flip_item_options(item)
    return items


def build_candidate_items(
    stories: Iterable[dict],
    *,
    seed: int = 42,
) -> list[ItemRecord]:
    rng = random.Random(seed)
    items: list[ItemRecord] = []
    for record in stories:
        if not _is_everyday(record):
            continue
        tag, confidence = infer_tension_tag(record)
        score = candidate_score(record, tag, confidence)
        moral_is_a = rng.random() < 0.5

        moral_option_text = (
            f"{_normalize_sentence(record['moral_action'])} {_normalize_sentence(record['moral_consequence'])}"
        )
        immoral_option_text = (
            f"{_normalize_sentence(record['immoral_action'])} {_normalize_sentence(record['immoral_consequence'])}"
        )

        option_a = moral_option_text if moral_is_a else immoral_option_text
        option_b = immoral_option_text if moral_is_a else moral_option_text

        item = ItemRecord(
            item_id="",
            source_story_id=record["ID"],
            scenario_context=_scenario_context(record),
            option_a=option_a,
            option_b=option_b,
            primary_tension_tag=tag,
            notes_on_motive=_normalize_sentence(record["intention"]),
            notes_on_consequence=(
                f"Moral path: {_normalize_sentence(record['moral_consequence'])} "
                f"Immoral path: {_normalize_sentence(record['immoral_consequence'])}"
            ),
            norm=_normalize_sentence(record["norm"]),
            intention=_normalize_sentence(record["intention"]),
            option_a_alignment="moral" if moral_is_a else "immoral",
            option_b_alignment="immoral" if moral_is_a else "moral",
            moral_option="A" if moral_is_a else "B",
            heuristic_score=score,
            heuristic_confidence=round(confidence, 3),
            metadata={
                "moral_action": _normalize_sentence(record["moral_action"]),
                "moral_consequence": _normalize_sentence(record["moral_consequence"]),
                "immoral_action": _normalize_sentence(record["immoral_action"]),
                "immoral_consequence": _normalize_sentence(record["immoral_consequence"]),
                "action_overlap": round(_lexical_overlap(record["moral_action"], record["immoral_action"]), 3),
            },
        )
        items.append(item)
    return items


def select_candidate_pool(
    items: list[ItemRecord],
    *,
    limit: int = 150,
) -> list[ItemRecord]:
    target_per_tag = math.ceil(limit / len(TENSION_TAGS))
    grouped: dict[str, list[ItemRecord]] = defaultdict(list)
    for item in sorted(items, key=lambda row: row.heuristic_score, reverse=True):
        grouped[item.primary_tension_tag].append(item)

    selected: list[ItemRecord] = []
    seen: set[str] = set()
    for tag in TENSION_TAGS:
        for item in grouped[tag][:target_per_tag]:
            if item.source_story_id in seen:
                continue
            selected.append(item)
            seen.add(item.source_story_id)

    if len(selected) < limit:
        for item in sorted(items, key=lambda row: row.heuristic_score, reverse=True):
            if item.source_story_id in seen:
                continue
            selected.append(item)
            seen.add(item.source_story_id)
            if len(selected) >= limit:
                break

    selected = selected[:limit]
    for index, item in enumerate(selected, start=1):
        item.item_id = f"ms_{index:03d}"
    return rebalance_option_order(selected, seed=limit)


def stratified_split(
    items: list[ItemRecord],
    *,
    dev_size: int = 30,
    eval_size: int = 120,
    seed: int = 42,
) -> tuple[list[ItemRecord], list[ItemRecord]]:
    rng = random.Random(seed)
    grouped: dict[str, list[ItemRecord]] = defaultdict(list)
    for item in items:
        grouped[item.primary_tension_tag].append(item)
    for bucket in grouped.values():
        rng.shuffle(bucket)

    dev: list[ItemRecord] = []
    evaluation: list[ItemRecord] = []
    dev_quota = {tag: round(dev_size * len(grouped[tag]) / len(items)) for tag in grouped}

    for tag in grouped:
        bucket = grouped[tag]
        take = min(len(bucket), dev_quota.get(tag, 0))
        dev.extend(bucket[:take])
        evaluation.extend(bucket[take:])

    if len(dev) < dev_size:
        leftovers = [item for item in evaluation if item not in dev]
        rng.shuffle(leftovers)
        need = dev_size - len(dev)
        dev.extend(leftovers[:need])
        evaluation = [item for item in evaluation if item not in dev]
    elif len(dev) > dev_size:
        rng.shuffle(dev)
        spill = dev[dev_size:]
        dev = dev[:dev_size]
        evaluation.extend(spill)

    evaluation = sorted(evaluation, key=lambda row: row.item_id)[:eval_size]
    dev = sorted(dev, key=lambda row: row.item_id)
    rebalance_option_order(dev, seed=seed)
    rebalance_option_order(evaluation, seed=seed + 1)
    return dev, evaluation


def write_jsonl(path: str | Path, rows: Iterable[ItemRecord]) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")
    return out_path


def write_review_csv(path: str | Path, rows: Iterable[ItemRecord]) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "item_id",
        "source_story_id",
        "primary_tension_tag",
        "heuristic_score",
        "heuristic_confidence",
        "norm",
        "scenario_context",
        "option_a",
        "option_b",
        "notes_on_motive",
        "notes_on_consequence",
        "option_a_alignment",
        "option_b_alignment",
        "moral_option",
        "metadata",
        "manual_accept",
        "manual_tag",
        "manual_notes",
    ]
    with out_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = row.to_dict()
            payload["metadata"] = json.dumps(payload.get("metadata", {}), ensure_ascii=False)
            payload["manual_accept"] = ""
            payload["manual_tag"] = ""
            payload["manual_notes"] = ""
            writer.writerow({key: payload.get(key, "") for key in fieldnames})
    return out_path


def apply_review_overrides(
    candidate_path: str | Path,
    review_csv_path: str | Path,
    *,
    dev_path: str | Path,
    eval_path: str | Path,
    dev_size: int = 30,
    eval_size: int = 120,
    seed: int = 42,
) -> dict[str, Path]:
    by_id: dict[str, ItemRecord] = {}
    with Path(candidate_path).open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            by_id[payload["item_id"]] = ItemRecord(**payload)

    unresolved_rows = 0
    with Path(review_csv_path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            item_id = row["item_id"]
            if item_id not in by_id:
                continue
            item = by_id[item_id]
            manual_accept = row.get("manual_accept", "").strip().lower()
            if not manual_accept:
                unresolved_rows += 1
                continue
            if manual_accept in {"0", "n", "no", "false", "reject"}:
                by_id.pop(item_id, None)
                continue
            if manual_accept not in {"1", "y", "yes", "true", "accept", "keep"}:
                raise ValueError(
                    f"Invalid manual_accept value for {item_id}: {row.get('manual_accept')!r}. "
                    "Use accept/keep or reject/no style values."
                )
            manual_tag = row.get("manual_tag", "").strip()
            if manual_tag and manual_tag not in TENSION_TAGS:
                raise ValueError(
                    f"Invalid manual_tag value for {item_id}: {manual_tag!r}. "
                    f"Expected one of {', '.join(TENSION_TAGS)}."
                )
            if manual_tag in TENSION_TAGS:
                item.primary_tension_tag = manual_tag
            manual_notes = row.get("manual_notes", "").strip()
            if manual_notes:
                item.metadata["manual_notes"] = manual_notes

    if unresolved_rows:
        raise ValueError(
            f"Review sheet is incomplete: {unresolved_rows} rows still have blank manual_accept. "
            "Fill manual_accept for every candidate before locking splits."
        )

    reviewed = sorted(by_id.values(), key=lambda row: row.item_id)
    if len(reviewed) < dev_size + eval_size:
        raise ValueError(
            f"Only {len(reviewed)} items remain after review, but dev_size + eval_size requires "
            f"{dev_size + eval_size}. Rebuild the candidate pool or accept more items."
        )
    dev_items, eval_items = stratified_split(reviewed, dev_size=dev_size, eval_size=eval_size, seed=seed)
    return {
        "dev": write_jsonl(dev_path, dev_items),
        "eval": write_jsonl(eval_path, eval_items),
    }


def build_and_export_items(
    raw_path: str | Path,
    *,
    candidate_path: str | Path,
    dev_path: str | Path,
    eval_path: str | Path,
    review_csv_path: str | Path,
    candidate_limit: int = 150,
    dev_size: int = 30,
    eval_size: int = 120,
    seed: int = 42,
) -> dict[str, Path]:
    stories = load_moral_stories(raw_path)
    candidates = build_candidate_items(stories, seed=seed)
    selected = select_candidate_pool(candidates, limit=candidate_limit)
    dev_items, eval_items = stratified_split(selected, dev_size=dev_size, eval_size=eval_size, seed=seed)

    return {
        "candidate_pool": write_jsonl(candidate_path, selected),
        "dev": write_jsonl(dev_path, dev_items),
        "eval": write_jsonl(eval_path, eval_items),
        "review_csv": write_review_csv(review_csv_path, selected),
    }
