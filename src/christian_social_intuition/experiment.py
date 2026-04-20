from __future__ import annotations

"""Run the staged J1→E→J2 protocol against local chat-completions-compatible models."""

import json
from pathlib import Path
from typing import Iterable

from .ollama_client import OllamaClient
from .parsing import parse_explanation_text, parse_judgment_text
from .prompts import (
    DEFAULT_SYSTEM_PROMPT,
    build_explanation_prompt,
    build_frame_catalog,
    build_frame_message,
    build_judgment_prompt,
    load_frames,
)
from .schema import ExperimentResult, ItemRecord, MAIN_CONDITIONS, SANITY_CONDITION

CONDITION_FRAME_META = {
    "baseline": {"family": None, "position": None},
    "secular_pre": {"family": "secular", "position": "pre"},
    "christian_pre": {"family": "christian", "position": "pre"},
    "secular_post": {"family": "secular", "position": "post"},
    "christian_post": {"family": "christian", "position": "post"},
    SANITY_CONDITION: {"family": None, "position": None},
}


def load_items(path: str | Path) -> list[ItemRecord]:
    """Load the locked benchmark split from JSONL into ItemRecord instances."""
    rows: list[ItemRecord] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            rows.append(ItemRecord(**payload))
    return rows


def load_existing_results(path: str | Path) -> dict[tuple[str, str, str, str], dict]:
    """Index an existing result JSONL by model, condition, item, and frame variant for resume support."""
    result: dict[tuple[str, str, str, str], dict] = {}
    file_path = Path(path)
    if not file_path.exists():
        return result
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            payload = json.loads(line)
            variant_id = payload.get("frame_variant_id") or ""
            key = (payload["model"], payload["condition"], payload["item_id"], variant_id)
            result[key] = payload
    return result


def select_sanity_subset(items: Iterable[ItemRecord], *, size: int, seed: int = 42) -> list[ItemRecord]:
    """Choose a small tag-stratified subset for the judgment-only baseline sanity condition."""
    import random
    from collections import defaultdict

    rng = random.Random(seed)
    grouped: dict[str, list[ItemRecord]] = defaultdict(list)
    for item in items:
        grouped[item.primary_tension_tag].append(item)
    for bucket in grouped.values():
        rng.shuffle(bucket)

    selected: list[ItemRecord] = []
    while len(selected) < size and any(grouped.values()):
        for tag in list(grouped):
            if grouped[tag]:
                selected.append(grouped[tag].pop())
                if len(selected) >= size:
                    break
    return sorted(selected, key=lambda row: row.item_id)


class ExperimentRunner:
    """Run the staged protocol and emit schema-aligned rows plus a manifest."""

    def __init__(
        self,
        *,
        model: str,
        frames_path: str | Path,
        split: str,
        run_id: str,
        frame_mode: str = "selected",
        ollama_base_url: str = "http://127.0.0.1:11434",
        timeout: int = 120,
        temperature: float = 0.0,
        max_judgment_tokens: int = 80,
        max_explanation_tokens: int = 100,
        seed: int = 42,
    ):
        self.frame_config = load_frames(frames_path)
        self.frame_catalog = build_frame_catalog(self.frame_config)
        self.selected_ids = self.frame_config.get("selected_v2", {})
        self.family_ids = self.frame_config.get("family_audit_v2", {})
        self.frames_config_version = self.frame_config.get("version")
        self.frames_path = str(frames_path)
        self.model = model
        self.split = split
        self.run_id = run_id
        self.frame_mode = frame_mode
        self.client = OllamaClient(model, base_url=ollama_base_url, timeout=timeout)
        self.temperature = temperature
        self.max_judgment_tokens = max_judgment_tokens
        self.max_explanation_tokens = max_explanation_tokens
        self.seed = seed

    def _system_prompt(self, frame_key: str | None) -> str:
        _ = frame_key
        return DEFAULT_SYSTEM_PROMPT

    def _chat(self, messages: list[dict[str, str]], *, max_tokens: int) -> tuple[str, dict]:
        response = self.client.chat(
            messages,
            temperature=self.temperature,
            max_tokens=max_tokens,
            seed=self.seed,
        )
        text = self.client.extract_text(response)
        return text, response

    def _resolve_variants_for_condition(self, condition: str) -> list[dict | None]:
        meta = CONDITION_FRAME_META[condition]
        family = meta["family"]
        if family is None:
            return [None]
        if self.frame_mode == "family_audit":
            variant_ids = self.family_ids.get(family, [])
            return [self.frame_catalog[variant_id] for variant_id in variant_ids]
        selected_id = self.selected_ids.get(family)
        if not selected_id:
            raise KeyError(f"No selected_v2 frame variant configured for family '{family}'.")
        return [self.frame_catalog[selected_id]]

    def _build_manifest(
        self,
        *,
        output_path: Path,
        items: list[ItemRecord],
        sanity_item_count: int,
        config_path: str | Path | None,
    ) -> dict:
        condition_variants = {
            condition: [
                variant["id"] if variant is not None else "none"
                for variant in self._resolve_variants_for_condition(condition)
            ]
            for condition in (*MAIN_CONDITIONS, SANITY_CONDITION)
        }
        return {
            "run_id": self.run_id,
            "model": self.model,
            "split": self.split,
            "item_count": len(items),
            "sanity_item_count": sanity_item_count,
            "seed": self.seed,
            "temperature": self.temperature,
            "max_judgment_tokens": self.max_judgment_tokens,
            "max_explanation_tokens": self.max_explanation_tokens,
            "condition_set": list(MAIN_CONDITIONS) + [SANITY_CONDITION],
            "frame_mode": self.frame_mode,
            "frames_config_version": self.frames_config_version,
            "frames_path": self.frames_path,
            "config_path": str(config_path) if config_path is not None else None,
            "output_path": str(output_path),
            "condition_variants": condition_variants,
        }

    def run_condition(self, item: ItemRecord, condition: str, *, frame_variant: dict | None = None) -> ExperimentResult:
        """Execute one item under one condition while preserving prompts and raw responses in `raw_trace`."""
        meta = CONDITION_FRAME_META[condition]
        frame_family = meta["family"]
        frame_position = meta["position"]
        messages: list[dict[str, str]] = [{"role": "system", "content": self._system_prompt(frame_family)}]
        raw_trace: dict[str, dict] = {}

        if frame_position == "pre" and frame_variant is not None:
            frame_message = build_frame_message(frame_variant, remaining_steps=False)
            messages.append({"role": "user", "content": frame_message})
            raw_trace["pre_frame"] = {
                "prompt": frame_message,
                "frame_variant_id": frame_variant["id"],
                "frame_family": frame_variant["family"],
            }

        j1_prompt = build_judgment_prompt(item, stage_name="J1")
        messages.append({"role": "user", "content": j1_prompt})
        j1_text, j1_response = self._chat(messages, max_tokens=self.max_judgment_tokens)
        j1_act, j1_heart = parse_judgment_text(j1_text)
        raw_trace["j1"] = {"prompt": j1_prompt, "raw_text": j1_text, "response": j1_response}
        messages.append({"role": "assistant", "content": j1_text})

        if condition == SANITY_CONDITION:
            return ExperimentResult(
                model=self.model,
                split=self.split,
                run_id=self.run_id,
                condition=condition,
                item_id=item.item_id,
                seed=self.seed,
                temperature=self.temperature,
                max_judgment_tokens=self.max_judgment_tokens,
                max_explanation_tokens=self.max_explanation_tokens,
                frame_mode=self.frame_mode,
                frame_family=frame_variant["family"] if frame_variant else frame_family,
                frame_variant_id=frame_variant["id"] if frame_variant else None,
                frame_position=frame_position,
                frames_config_version=self.frames_config_version,
                j1_act=j1_act,
                j1_heart=j1_heart,
                e_focus=None,
                e_text=None,
                j2_act=None,
                j2_heart=None,
                raw_trace=raw_trace,
            )

        if frame_position == "post" and frame_variant is not None:
            frame_message = build_frame_message(frame_variant, remaining_steps=True)
            messages.append({"role": "user", "content": frame_message})
            raw_trace["post_frame"] = {
                "prompt": frame_message,
                "frame_variant_id": frame_variant["id"],
                "frame_family": frame_variant["family"],
            }

        e_prompt = build_explanation_prompt(item, j1_act=j1_act, j1_heart=j1_heart)
        messages.append({"role": "user", "content": e_prompt})
        e_text_raw, e_response = self._chat(messages, max_tokens=self.max_explanation_tokens)
        e_focus, e_text = parse_explanation_text(e_text_raw)
        raw_trace["explanation"] = {"prompt": e_prompt, "raw_text": e_text_raw, "response": e_response}
        messages.append({"role": "assistant", "content": e_text_raw})

        j2_prompt = build_judgment_prompt(item, stage_name="J2")
        messages.append({"role": "user", "content": j2_prompt})
        j2_text, j2_response = self._chat(messages, max_tokens=self.max_judgment_tokens)
        j2_act, j2_heart = parse_judgment_text(j2_text)
        raw_trace["j2"] = {"prompt": j2_prompt, "raw_text": j2_text, "response": j2_response}

        return ExperimentResult(
            model=self.model,
            split=self.split,
            run_id=self.run_id,
            condition=condition,
            item_id=item.item_id,
            seed=self.seed,
            temperature=self.temperature,
            max_judgment_tokens=self.max_judgment_tokens,
            max_explanation_tokens=self.max_explanation_tokens,
            frame_mode=self.frame_mode,
            frame_family=frame_variant["family"] if frame_variant else frame_family,
            frame_variant_id=frame_variant["id"] if frame_variant else None,
            frame_position=frame_position,
            frames_config_version=self.frames_config_version,
            j1_act=j1_act,
            j1_heart=j1_heart,
            e_focus=e_focus,
            e_text=e_text,
            j2_act=j2_act,
            j2_heart=j2_heart,
            raw_trace=raw_trace,
        )

    def run_items(
        self,
        items: Iterable[ItemRecord],
        *,
        output_path: str | Path,
        include_sanity_subset: list[ItemRecord] | None = None,
        resume: bool = True,
        config_path: str | Path | None = None,
    ) -> Path:
        """Run a split end-to-end, append new rows to disk, and write a manifest beside the JSONL file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        existing = load_existing_results(output_file) if resume else {}
        item_list = list(items)

        manifest = self._build_manifest(
            output_path=output_file,
            items=item_list,
            sanity_item_count=len(include_sanity_subset or []),
            config_path=config_path,
        )
        output_file.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        sanity_ids = {item.item_id for item in include_sanity_subset or []}
        with output_file.open("a", encoding="utf-8") as handle:
            for item in item_list:
                for condition in MAIN_CONDITIONS:
                    for frame_variant in self._resolve_variants_for_condition(condition):
                        variant_id = frame_variant["id"] if frame_variant is not None else ""
                        key = (self.model, condition, item.item_id, variant_id)
                        if key in existing:
                            continue
                        result = self.run_condition(item, condition, frame_variant=frame_variant)
                        handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
                        handle.flush()
                if item.item_id in sanity_ids:
                    sanity_key = (self.model, SANITY_CONDITION, item.item_id, "")
                    if sanity_key not in existing:
                        sanity_result = self.run_condition(item, SANITY_CONDITION, frame_variant=None)
                        handle.write(json.dumps(sanity_result.to_dict(), ensure_ascii=False) + "\n")
                        handle.flush()
        return output_file
