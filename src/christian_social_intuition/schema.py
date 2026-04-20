from __future__ import annotations

"""Shared schema objects and canonical condition/tag labels used across the project."""

from dataclasses import asdict, dataclass, field
from typing import Any

FOCUS_LABELS = (
    "motive/heart",
    "outward act/rule",
    "consequences/harm",
    "relationship/role",
)

TENSION_TAGS = (
    "motive_vs_outcome",
    "appearance_vs_intention",
    "good_act_bad_motive",
    "bad_act_good_motive",
    "mixed_stakeholder_context",
)

MAIN_CONDITIONS = (
    "baseline",
    "secular_pre",
    "christian_pre",
    "secular_post",
    "christian_post",
)

SANITY_CONDITION = "baseline_judgment_only"
ALL_CONDITIONS = MAIN_CONDITIONS + (SANITY_CONDITION,)


@dataclass(slots=True)
class ItemRecord:
    item_id: str
    source_story_id: str
    scenario_context: str
    option_a: str
    option_b: str
    primary_tension_tag: str
    notes_on_motive: str
    notes_on_consequence: str
    norm: str
    intention: str
    option_a_alignment: str
    option_b_alignment: str
    moral_option: str
    heuristic_score: float
    heuristic_confidence: float
    source_split: str = "full"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ExperimentResult:
    model: str
    split: str
    run_id: str
    condition: str
    item_id: str
    seed: int
    temperature: float
    max_judgment_tokens: int
    max_explanation_tokens: int
    frame_mode: str
    frame_family: str | None
    frame_variant_id: str | None
    frame_position: str | None
    frames_config_version: str | None
    j1_act: str | None
    j1_heart: str | None
    e_focus: str | None
    e_text: str | None
    j2_act: str | None
    j2_heart: str | None
    raw_trace: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
