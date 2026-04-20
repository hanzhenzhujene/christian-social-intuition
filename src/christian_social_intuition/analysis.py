from __future__ import annotations

"""Aggregate staged-run outputs into paper-facing tables, figures, and reports."""

import json
import math
import warnings
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
from PIL import Image

from .paired_stats import cohens_dz, paired_bootstrap_ci, paired_mean, sign_flip_permutation_test
from .parsing import parse_explanation_text, parse_judgment_text
from .schema import MAIN_CONDITIONS, SANITY_CONDITION, TENSION_TAGS
from .text_metrics import compute_explanation_metrics, matched_terms

CONDITION_ORDER = ["baseline", "secular_pre", "christian_pre", "secular_post", "christian_post"]
CONDITION_LABELS = {
    "baseline": "Baseline",
    "secular_pre": "Secular pre",
    "christian_pre": "Christian pre",
    "secular_post": "Secular post",
    "christian_post": "Christian post",
    SANITY_CONDITION: "Judgment-only baseline",
}
MODEL_ORDER = ["qwen2.5:7b-instruct", "qwen2.5:0.5b-instruct"]
FRAME_COLORS = {
    "baseline": "#7A7F86",
    "secular": "#2C7FB8",
    "christian": "#C76D1F",
}
MEASURE_COLORS = {
    "act": "#4C78A8",
    "heart": "#D64F4F",
    "raw": "#B04A5A",
    "controlled": "#1B7F79",
    "coarse": "#5D6B78",
}

MAIN_TEXT_CONTRASTS = [
    "christian_pre_vs_secular_pre_j1_heart_shift",
    "christian_pre_vs_secular_pre_j1_act_shift",
    "christian_post_vs_secular_post_explanation_raw",
    "christian_post_vs_secular_post_explanation_controlled",
    "christian_post_vs_secular_post_j2_act_revision",
    "christian_post_vs_secular_post_j2_heart_revision",
]

MAIN_TEXT_CONTRAST_LABELS = {
    "christian_pre_vs_secular_pre_j1_heart_shift": "C-pre - S-pre on J1 heart shift",
    "christian_pre_vs_secular_pre_j1_act_shift": "C-pre - S-pre on J1 act shift",
    "christian_post_vs_secular_post_explanation_raw": "C-post - S-post on raw explanation score",
    "christian_post_vs_secular_post_explanation_controlled": "C-post - S-post on controlled semantic score",
    "christian_post_vs_secular_post_j2_act_revision": "C-post - S-post on J1→J2 act revision",
    "christian_post_vs_secular_post_j2_heart_revision": "C-post - S-post on J1→J2 heart revision",
}


def _condition_sort_key(condition: str) -> int:
    try:
        return CONDITION_ORDER.index(condition)
    except ValueError:
        return len(CONDITION_ORDER)


def _condition_label(condition: str) -> str:
    return CONDITION_LABELS.get(condition, condition.replace("_", " ").title())


def _condition_color(condition: str) -> str:
    if condition == "baseline":
        return FRAME_COLORS["baseline"]
    if "christian" in condition:
        return FRAME_COLORS["christian"]
    return FRAME_COLORS["secular"]


def _condition_marker(condition: str) -> str:
    return "s" if condition.endswith("post") else "o"


def _condition_hatch(condition: str) -> str:
    return "//" if condition.endswith("post") else ""


def _model_sort_key(model: str) -> int:
    try:
        return MODEL_ORDER.index(model)
    except ValueError:
        return len(MODEL_ORDER)


def _model_label(model: str) -> str:
    if model == "qwen2.5:7b-instruct":
        return "Qwen 2.5 7B"
    if model == "qwen2.5:0.5b-instruct":
        return "Qwen 2.5 0.5B"
    return model


def _style_axis(ax: plt.Axes, *, grid_axis: str = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#C8CDD3")
    ax.spines["bottom"].set_color("#C8CDD3")
    ax.grid(axis=grid_axis, color="#D9D9D9", linewidth=0.8, alpha=0.85)
    ax.set_axisbelow(True)
    ax.set_facecolor("#FFFFFF")


def _add_pre_post_bands(ax: plt.Axes, *, pre: tuple[float, float], post: tuple[float, float]) -> None:
    ax.axhspan(pre[0], pre[1], color="#F4F8FC", alpha=0.95, zorder=0)
    ax.axhspan(post[0], post[1], color="#FFF6EE", alpha=0.95, zorder=0)


def _save_release_png(fig: plt.Figure, output_path: str | Path) -> Path:
    """Save a figure as a paper-safe RGB PNG for downstream LaTeX compilation."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    with Image.open(out) as image:
        if image.mode != "RGB":
            image.convert("RGB").save(out)
    return out


def _format_pct_text(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.1f}%"


def _ensure_frame_columns(df: pd.DataFrame) -> pd.DataFrame:
    working = df.copy()
    defaults = {
        "split": "eval",
        "run_id": "legacy",
        "seed": np.nan,
        "temperature": np.nan,
        "max_judgment_tokens": np.nan,
        "max_explanation_tokens": np.nan,
        "frame_mode": "selected",
        "frame_family": None,
        "frame_variant_id": None,
        "frame_position": None,
        "frames_config_version": None,
        "e_text": None,
        "raw_trace": None,
    }
    for column, default in defaults.items():
        if column not in working.columns:
            working[column] = default
    return working


def _filter_frame_mode(results_df: pd.DataFrame, frame_mode: str) -> pd.DataFrame:
    working = _ensure_frame_columns(results_df)
    subset = working[working["frame_mode"].fillna("selected") == frame_mode].copy()
    if subset.empty and frame_mode == "selected":
        return working.copy()
    return subset


def _join_item_metadata(results_df: pd.DataFrame, item_df: pd.DataFrame | None) -> pd.DataFrame:
    if item_df is None or item_df.empty:
        return results_df
    working = results_df.copy()
    candidate_columns = ["item_id", "primary_tension_tag", "moral_option", "source_story_id", "scenario_context"]
    keep_columns = [column for column in candidate_columns if column in item_df.columns]
    merge_columns = ["item_id"] + [column for column in keep_columns if column != "item_id" and column not in working.columns]
    if len(merge_columns) == 1:
        return working
    return working.merge(item_df[merge_columns].drop_duplicates(subset=["item_id"]), on="item_id", how="left")


def _metric_with_ci(values: Iterable[float], *, bootstrap_samples: int, bootstrap_seed: int) -> tuple[float, float, float]:
    values_list = list(values)
    estimate = paired_mean(values_list)
    ci_low, ci_high = paired_bootstrap_ci(values_list, n_boot=bootstrap_samples, seed=bootstrap_seed)
    return estimate, ci_low, ci_high


def _interpret_contrast(metric: str, estimate: float, p_value: float) -> str:
    if math.isnan(estimate):
        return "No estimate available for this contrast."
    magnitude = abs(estimate)
    if magnitude < 0.01:
        magnitude_text = "virtually no difference"
    elif magnitude < 0.03:
        magnitude_text = "a modest difference"
    else:
        magnitude_text = "a clearer difference"
    if estimate > 0:
        direction = "Christian exceeds the matched secular control"
    elif estimate < 0:
        direction = "Christian falls below the matched secular control"
    else:
        direction = "Christian and secular are tied"
    if math.isnan(p_value):
        significance = "without a stable paired significance estimate"
    elif p_value < 0.05:
        significance = "with paired evidence against the null"
    else:
        significance = "but the paired test remains weak"
    if estimate == 0:
        return f"For {metric}, {direction}; the paired test remains weak."
    return f"For {metric}, {direction}; the contrast shows {magnitude_text} {significance}."


def _binary_mean(series: pd.Series) -> float:
    if series.empty:
        return math.nan
    return float(series.astype(float).mean())


def _pp(value: float | int | None) -> float:
    if value is None or pd.isna(value):
        return math.nan
    return float(value) * 100.0


def _format_pp_ci(estimate: float, ci_low: float, ci_high: float) -> str:
    if any(pd.isna(value) for value in [estimate, ci_low, ci_high]):
        return "n/a"
    return f"{_pp(estimate):+.2f} pp [{_pp(ci_low):+.2f}, {_pp(ci_high):+.2f}]"


def _format_p_value(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    if value < 0.001:
        return "<0.001"
    return f"{value:.3f}"


def load_results(paths: str | Path | Iterable[str | Path]) -> pd.DataFrame:
    """Load one or more JSONL result files and backfill parsed fields from raw traces if needed."""
    if isinstance(paths, (str, Path)):
        path_list = [paths]
    else:
        path_list = list(paths)
    rows: list[dict] = []
    for path in path_list:
        source_path = Path(path)
        with source_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                payload = json.loads(line)
                raw_trace = payload.get("raw_trace")
                if isinstance(raw_trace, dict):
                    j1_raw = raw_trace.get("j1", {}).get("raw_text")
                    if j1_raw and (not payload.get("j1_act") or not payload.get("j1_heart")):
                        parsed_act, parsed_heart = parse_judgment_text(str(j1_raw))
                        payload["j1_act"] = payload.get("j1_act") or parsed_act
                        payload["j1_heart"] = payload.get("j1_heart") or parsed_heart

                    explanation_raw = raw_trace.get("explanation", {}).get("raw_text")
                    if explanation_raw and (not payload.get("e_focus") or not payload.get("e_text")):
                        parsed_focus, parsed_text = parse_explanation_text(str(explanation_raw))
                        payload["e_focus"] = payload.get("e_focus") or parsed_focus
                        payload["e_text"] = payload.get("e_text") or parsed_text

                    j2_raw = raw_trace.get("j2", {}).get("raw_text")
                    if j2_raw and payload.get("condition") != SANITY_CONDITION and (
                        not payload.get("j2_act") or not payload.get("j2_heart")
                    ):
                        parsed_act, parsed_heart = parse_judgment_text(str(j2_raw))
                        payload["j2_act"] = payload.get("j2_act") or parsed_act
                        payload["j2_heart"] = payload.get("j2_heart") or parsed_heart
                payload["source_result_path"] = str(source_path)
                rows.append(payload)
    return _ensure_frame_columns(pd.DataFrame(rows))


def load_annotation(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def build_annotation_sheet(results_df: pd.DataFrame) -> pd.DataFrame:
    """Create the coder-facing CSV used for pending explanation annotation."""
    sheet = _ensure_frame_columns(results_df)
    sheet = sheet[sheet["condition"] != SANITY_CONDITION].copy()
    sheet["consistency_score"] = ""
    sheet["christian_lexicon_present"] = ""
    sheet["unsupported_motive_inference"] = ""
    sheet["notes"] = ""
    keep = [
        "model",
        "split",
        "run_id",
        "condition",
        "item_id",
        "frame_mode",
        "frame_family",
        "frame_variant_id",
        "j1_act",
        "j1_heart",
        "e_focus",
        "e_text",
        "j2_act",
        "j2_heart",
        "consistency_score",
        "christian_lexicon_present",
        "unsupported_motive_inference",
        "notes",
    ]
    return sheet[keep].sort_values(["model", "condition", "item_id", "frame_variant_id"]).reset_index(drop=True)


def enrich_results(
    results_df: pd.DataFrame,
    *,
    lexicons: dict | None = None,
    annotation_df: pd.DataFrame | None = None,
    item_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Attach lexical metrics, item metadata, and optional human-coded fields to raw results."""
    working = _filter_frame_mode(results_df, "selected")
    working = _join_item_metadata(working, item_df)
    lexicons = lexicons or {}
    strict_terms = lexicons.get("strict_echo_terms", [])
    semantic_terms = lexicons.get("non_echo_semantic_terms", [])

    metrics = working["e_text"].map(
        lambda text: compute_explanation_metrics(
            text,
            strict_echo_terms=strict_terms,
            non_echo_semantic_terms=semantic_terms,
        )
    )
    metrics_df = pd.DataFrame(metrics.tolist()) if not metrics.empty else pd.DataFrame()
    if not metrics_df.empty:
        working = pd.concat([working.reset_index(drop=True), metrics_df.reset_index(drop=True)], axis=1)
    else:
        for column in [
            "frame_echo_score",
            "frame_echo_present",
            "semantic_score_raw",
            "semantic_raw_present",
            "semantic_score_controlled",
            "semantic_controlled_present",
            "restructure_beyond_echo",
        ]:
            working[column] = 0

    working["motive_focus_present"] = (working["e_focus"] == "motive/heart").astype(int)
    working["j2_act_revision"] = (
        working["j2_act"].notna() & working["j1_act"].notna() & (working["j2_act"] != working["j1_act"])
    ).astype(int)
    working["j2_heart_revision"] = (
        working["j2_heart"].notna() & working["j1_heart"].notna() & (working["j2_heart"] != working["j1_heart"])
    ).astype(int)
    working["frame_variant_id"] = working["frame_variant_id"].fillna("none")
    working["frame_family"] = working["frame_family"].fillna("none")

    if annotation_df is not None and not annotation_df.empty:
        ann = annotation_df.copy()
        merge_keys = [key for key in ["model", "condition", "item_id"] if key in ann.columns]
        if "frame_variant_id" in ann.columns and "frame_variant_id" in working.columns:
            merge_keys.append("frame_variant_id")
        working = working.merge(ann, on=merge_keys, how="left")
    else:
        working["consistency_score"] = pd.NA
        working["christian_lexicon_present"] = pd.NA
        working["unsupported_motive_inference"] = pd.NA
    return working


def build_condition_pairs(results_df: pd.DataFrame, *, item_df: pd.DataFrame | None = None, lexicons: dict | None = None) -> pd.DataFrame:
    """Join each non-baseline condition to its baseline row for item-level paired analyses."""
    working = enrich_results(results_df, lexicons=lexicons, item_df=item_df)
    baseline = working[working["condition"] == "baseline"].copy()
    baseline_cols = [
        "model",
        "item_id",
        "j1_act",
        "j1_heart",
        "motive_focus_present",
        "frame_echo_present",
        "semantic_raw_present",
        "semantic_controlled_present",
        "restructure_beyond_echo",
        "frame_echo_score",
        "semantic_score_raw",
        "semantic_score_controlled",
    ]
    baseline = baseline[baseline_cols].drop_duplicates(subset=["model", "item_id"])
    baseline = baseline.rename(
        columns={
            "j1_act": "j1_act_base",
            "j1_heart": "j1_heart_base",
            "motive_focus_present": "motive_focus_present_base",
            "frame_echo_present": "frame_echo_present_base",
            "semantic_raw_present": "semantic_raw_present_base",
            "semantic_controlled_present": "semantic_controlled_present_base",
            "restructure_beyond_echo": "restructure_beyond_echo_base",
            "frame_echo_score": "frame_echo_score_base",
            "semantic_score_raw": "semantic_score_raw_base",
            "semantic_score_controlled": "semantic_score_controlled_base",
        }
    )

    cond = working[working["condition"].isin([condition for condition in MAIN_CONDITIONS if condition != "baseline"])].copy()
    paired = cond.merge(baseline, on=["model", "item_id"], how="left")

    paired["j1_act_shift"] = (paired["j1_act"] != paired["j1_act_base"]).astype(int)
    paired["j1_heart_shift"] = (paired["j1_heart"] != paired["j1_heart_base"]).astype(int)
    paired["no_j1_change_vs_baseline"] = ((paired["j1_act_shift"] == 0) & (paired["j1_heart_shift"] == 0)).astype(int)

    for base_col, cond_col, target in [
        ("motive_focus_present_base", "motive_focus_present", "motive_focus_delta"),
        ("frame_echo_present_base", "frame_echo_present", "frame_echo_delta"),
        ("semantic_raw_present_base", "semantic_raw_present", "semantic_raw_delta"),
        ("semantic_controlled_present_base", "semantic_controlled_present", "semantic_controlled_delta"),
        ("restructure_beyond_echo_base", "restructure_beyond_echo", "restructure_delta"),
    ]:
        paired[target] = paired[cond_col].astype(float) - paired[base_col].astype(float)
    for base_col, cond_col, target in [
        ("frame_echo_score_base", "frame_echo_score", "frame_echo_score_delta"),
        ("semantic_score_raw_base", "semantic_score_raw", "semantic_score_raw_delta"),
        ("semantic_score_controlled_base", "semantic_score_controlled", "semantic_score_controlled_delta"),
    ]:
        paired[target] = paired[cond_col].astype(float) - paired[base_col].astype(float)

    paired["dissociated_explanation_shift"] = (
        (paired["semantic_score_controlled_delta"] > 0) & (paired["no_j1_change_vs_baseline"] == 1)
    ).astype(int)
    paired["motive_focus_shift"] = paired["motive_focus_delta"]
    paired["act_a_to_b"] = ((paired["j1_act"] == "A") & (paired["j2_act"] == "B")).astype(int)
    paired["act_b_to_a"] = ((paired["j1_act"] == "B") & (paired["j2_act"] == "A")).astype(int)
    paired["heart_a_to_b"] = ((paired["j1_heart"] == "A") & (paired["j2_heart"] == "B")).astype(int)
    paired["heart_b_to_a"] = ((paired["j1_heart"] == "B") & (paired["j2_heart"] == "A")).astype(int)

    if "moral_option" in paired.columns:
        paired["toward_moral_option"] = (
            paired["j2_act"].eq(paired["moral_option"]) & paired["j1_act"].ne(paired["moral_option"])
        ).astype(int)
        paired["away_from_moral_option"] = (
            paired["j1_act"].eq(paired["moral_option"]) & paired["j2_act"].ne(paired["moral_option"])
        ).astype(int)
    else:
        paired["toward_moral_option"] = 0
        paired["away_from_moral_option"] = 0
    return paired


def compute_condition_summary(
    results_df: pd.DataFrame,
    *,
    item_df: pd.DataFrame | None = None,
    annotation_df: pd.DataFrame | None = None,
    lexicons: dict | None = None,
    bootstrap_samples: int = 1000,
    bootstrap_seed: int = 42,
) -> pd.DataFrame:
    """Summarize baseline-relative movement and revision rates for every released condition."""
    working = enrich_results(results_df, lexicons=lexicons, annotation_df=annotation_df, item_df=item_df)
    paired = build_condition_pairs(results_df, item_df=item_df, lexicons=lexicons)
    rows: list[dict] = []

    for model in sorted(working["model"].dropna().unique(), key=_model_sort_key):
        model_base = working[(working["model"] == model) & (working["condition"] == "baseline")]
        if model_base.empty:
            continue
        base_row = {
            "model": model,
            "condition": "baseline",
            "n_items": int(len(model_base)),
            "j1_act_shift_rate": 0.0,
            "j1_act_shift_ci_low": 0.0,
            "j1_act_shift_ci_high": 0.0,
            "j1_heart_shift_rate": 0.0,
            "j1_heart_shift_ci_low": 0.0,
            "j1_heart_shift_ci_high": 0.0,
            "j2_act_revision_rate": _binary_mean(model_base["j2_act_revision"]),
            "j2_heart_revision_rate": _binary_mean(model_base["j2_heart_revision"]),
            "motive_focus_rate": _binary_mean(model_base["motive_focus_present"]),
            "motive_focus_delta_vs_baseline": 0.0,
            "frame_echo_rate": _binary_mean(model_base["frame_echo_present"]),
            "frame_echo_delta_vs_baseline": 0.0,
            "frame_echo_score_delta_vs_baseline": 0.0,
            "semantic_raw_rate": _binary_mean(model_base["semantic_raw_present"]),
            "semantic_raw_delta_vs_baseline": 0.0,
            "semantic_score_raw_delta_vs_baseline": 0.0,
            "semantic_controlled_rate": _binary_mean(model_base["semantic_controlled_present"]),
            "semantic_controlled_delta_vs_baseline": 0.0,
            "semantic_score_controlled_delta_vs_baseline": 0.0,
            "restructure_beyond_echo_rate": _binary_mean(model_base["restructure_beyond_echo"]),
            "restructure_delta_vs_baseline": 0.0,
            "semantic_score_raw_mean": float(model_base["semantic_score_raw"].mean()),
            "semantic_score_controlled_mean": float(model_base["semantic_score_controlled"].mean()),
            "dissociated_explanation_shift_rate": 0.0,
            "consistency_score_mean": float(pd.to_numeric(model_base["consistency_score"], errors="coerce").mean()),
            "posthoc_christianization_index": 0.0,
            "posthoc_controlled_semantic_index": 0.0,
        }
        rows.append(base_row)

        model_pairs = paired[paired["model"] == model]
        for condition in [condition for condition in MAIN_CONDITIONS if condition != "baseline"]:
            subset = model_pairs[model_pairs["condition"] == condition]
            if subset.empty:
                continue
            row = {
                "model": model,
                "condition": condition,
                "n_items": int(len(subset)),
                "j2_act_revision_rate": _binary_mean(subset["j2_act_revision"]),
                "j2_heart_revision_rate": _binary_mean(subset["j2_heart_revision"]),
                "motive_focus_rate": _binary_mean(subset["motive_focus_present"]),
                "frame_echo_rate": _binary_mean(subset["frame_echo_present"]),
                "semantic_raw_rate": _binary_mean(subset["semantic_raw_present"]),
                "semantic_controlled_rate": _binary_mean(subset["semantic_controlled_present"]),
                "restructure_beyond_echo_rate": _binary_mean(subset["restructure_beyond_echo"]),
                "semantic_score_raw_mean": float(subset["semantic_score_raw"].mean()),
                "semantic_score_controlled_mean": float(subset["semantic_score_controlled"].mean()),
                "dissociated_explanation_shift_rate": _binary_mean(subset["dissociated_explanation_shift"]),
                "consistency_score_mean": float(pd.to_numeric(subset["consistency_score"], errors="coerce").mean()),
            }
            for source, prefix in [
                ("j1_act_shift", "j1_act_shift_rate"),
                ("j1_heart_shift", "j1_heart_shift_rate"),
                ("motive_focus_delta", "motive_focus_delta_vs_baseline"),
                ("frame_echo_delta", "frame_echo_delta_vs_baseline"),
                ("semantic_raw_delta", "semantic_raw_delta_vs_baseline"),
                ("semantic_controlled_delta", "semantic_controlled_delta_vs_baseline"),
                ("restructure_delta", "restructure_delta_vs_baseline"),
                ("frame_echo_score_delta", "frame_echo_score_delta_vs_baseline"),
                ("semantic_score_raw_delta", "semantic_score_raw_delta_vs_baseline"),
                ("semantic_score_controlled_delta", "semantic_score_controlled_delta_vs_baseline"),
            ]:
                estimate, ci_low, ci_high = _metric_with_ci(
                    subset[source].tolist(),
                    bootstrap_samples=bootstrap_samples,
                    bootstrap_seed=bootstrap_seed,
                )
                row[prefix] = estimate
                row[f"{prefix}_ci_low"] = ci_low
                row[f"{prefix}_ci_high"] = ci_high

            stable = subset[subset["no_j1_change_vs_baseline"] == 1]
            row["posthoc_christianization_index"] = (
                float(stable["semantic_score_raw_delta"].mean()) if not stable.empty else math.nan
            )
            row["posthoc_controlled_semantic_index"] = (
                float(stable["semantic_score_controlled_delta"].mean()) if not stable.empty else math.nan
            )
            rows.append(row)

    return pd.DataFrame(rows).sort_values(["model", "condition"], key=lambda s: s.map(_model_sort_key) if s.name == "model" else s.map(_condition_sort_key)).reset_index(drop=True)


def compute_sanity_agreement(results_df: pd.DataFrame) -> pd.DataFrame:
    """Measure agreement between staged baseline J1 and the judgment-only baseline subset."""
    working = _filter_frame_mode(results_df, "selected")
    baseline = working[working["condition"] == "baseline"][["model", "item_id", "j1_act", "j1_heart"]].copy()
    sanity = working[working["condition"] == SANITY_CONDITION][["model", "item_id", "j1_act", "j1_heart"]].copy()
    if baseline.empty or sanity.empty:
        return pd.DataFrame(columns=["model", "n_items", "j1_act_agreement", "j1_heart_agreement"])
    merged = baseline.merge(sanity, on=["model", "item_id"], suffixes=("_baseline", "_sanity"))
    rows = []
    for model in sorted(merged["model"].unique(), key=_model_sort_key):
        subset = merged[merged["model"] == model]
        rows.append(
            {
                "model": model,
                "n_items": int(len(subset)),
                "j1_act_agreement": float((subset["j1_act_baseline"] == subset["j1_act_sanity"]).mean()),
                "j1_heart_agreement": float((subset["j1_heart_baseline"] == subset["j1_heart_sanity"]).mean()),
            }
        )
    return pd.DataFrame(rows)


def _paired_condition_values(
    pairs_df: pd.DataFrame,
    *,
    model: str,
    lhs_condition: str,
    rhs_condition: str,
    value_column: str,
) -> pd.Series:
    subset = pairs_df[(pairs_df["model"] == model) & (pairs_df["condition"].isin([lhs_condition, rhs_condition]))].copy()
    if subset.empty:
        return pd.Series(dtype=float)
    wide = subset.pivot_table(index="item_id", columns="condition", values=value_column, aggfunc="mean")
    if lhs_condition not in wide.columns or rhs_condition not in wide.columns:
        return pd.Series(dtype=float)
    return (wide[lhs_condition] - wide[rhs_condition]).dropna()


def compute_direct_control_contrasts(
    results_df: pd.DataFrame,
    *,
    item_df: pd.DataFrame | None = None,
    lexicons: dict | None = None,
    bootstrap_samples: int = 1000,
    bootstrap_seed: int = 42,
    permutation_samples: int = 5000,
) -> pd.DataFrame:
    """Compute paired Christian-versus-secular contrasts with CIs, p-values, and effect sizes."""
    pairs = build_condition_pairs(results_df, item_df=item_df, lexicons=lexicons)
    specs = [
        {
            "contrast": "christian_pre_vs_secular_pre_j1_act_shift",
            "lhs": "christian_pre",
            "rhs": "secular_pre",
            "metric": "j1_act_shift",
            "metric_label": "first-pass act shift vs baseline",
            "group": "first_pass",
        },
        {
            "contrast": "christian_pre_vs_secular_pre_j1_heart_shift",
            "lhs": "christian_pre",
            "rhs": "secular_pre",
            "metric": "j1_heart_shift",
            "metric_label": "first-pass heart shift vs baseline",
            "group": "first_pass",
        },
        {
            "contrast": "christian_post_vs_secular_post_explanation_raw",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "semantic_score_raw",
            "metric_label": "raw Christian/heart-language score",
            "group": "explanation",
        },
        {
            "contrast": "christian_post_vs_secular_post_explanation_controlled",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "semantic_score_controlled",
            "metric_label": "lexical-controlled motive/heart semantic score",
            "group": "explanation",
        },
        {
            "contrast": "christian_post_vs_secular_post_restructure_beyond_echo",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "restructure_beyond_echo",
            "metric_label": "restructuring beyond direct echo",
            "group": "explanation",
        },
        {
            "contrast": "christian_post_vs_secular_post_explanation_raw_presence",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "semantic_raw_present",
            "metric_label": "raw Christian/heart-language presence",
            "group": "explanation",
        },
        {
            "contrast": "christian_post_vs_secular_post_explanation_controlled_presence",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "semantic_controlled_present",
            "metric_label": "lexical-controlled motive/heart presence",
            "group": "explanation",
        },
        {
            "contrast": "christian_post_vs_secular_post_dissociated_explanation_shift",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "dissociated_explanation_shift",
            "metric_label": "dissociated explanation shift with J1 fixed",
            "group": "mechanism",
        },
        {
            "contrast": "christian_post_vs_secular_post_j2_act_revision",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "j2_act_revision",
            "metric_label": "J1 to J2 act revision",
            "group": "revision",
        },
        {
            "contrast": "christian_post_vs_secular_post_j2_heart_revision",
            "lhs": "christian_post",
            "rhs": "secular_post",
            "metric": "j2_heart_revision",
            "metric_label": "J1 to J2 heart revision",
            "group": "revision",
        },
    ]
    rows: list[dict] = []
    for model in sorted(pairs["model"].dropna().unique(), key=_model_sort_key):
        model_rows: list[dict] = []
        for spec in specs:
            diffs = _paired_condition_values(
                pairs,
                model=model,
                lhs_condition=spec["lhs"],
                rhs_condition=spec["rhs"],
                value_column=spec["metric"],
            )
            estimate = paired_mean(diffs.tolist())
            ci_low, ci_high = paired_bootstrap_ci(diffs.tolist(), n_boot=bootstrap_samples, seed=bootstrap_seed)
            p_value = sign_flip_permutation_test(diffs.tolist(), n_perm=permutation_samples, seed=bootstrap_seed)
            effect_size = cohens_dz(diffs.tolist())
            lhs_mean = float(
                pairs[(pairs["model"] == model) & (pairs["condition"] == spec["lhs"])][spec["metric"]].astype(float).mean()
            )
            rhs_mean = float(
                pairs[(pairs["model"] == model) & (pairs["condition"] == spec["rhs"])][spec["metric"]].astype(float).mean()
            )
            row = {
                "model": model,
                "contrast": spec["contrast"],
                "group": spec["group"],
                "lhs_condition": spec["lhs"],
                "rhs_condition": spec["rhs"],
                "metric": spec["metric_label"],
                "n_items": int(len(diffs)),
                "lhs_mean": lhs_mean,
                "rhs_mean": rhs_mean,
                "estimate": estimate,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "p_value": p_value,
                "effect_size_dz": effect_size,
                "interpretation": _interpret_contrast(spec["metric_label"], estimate, p_value),
            }
            rows.append(row)
            model_rows.append(row)

        raw_row = next((row for row in model_rows if row["contrast"] == "christian_post_vs_secular_post_explanation_raw"), None)
        controlled_row = next(
            (row for row in model_rows if row["contrast"] == "christian_post_vs_secular_post_explanation_controlled"),
            None,
        )
        if raw_row is not None and controlled_row is not None:
            denominator = raw_row["estimate"]
            if pd.isna(denominator) or denominator <= 0 or abs(denominator) < 1e-9:
                survival_ratio = math.nan
                interpretation = (
                    "There is no positive raw Christian-post advantage to summarize with a lexical-control survival ratio."
                )
            else:
                survival_ratio = controlled_row["estimate"] / denominator
                interpretation = f"{survival_ratio * 100:.1f}% of the raw Christian-post explanation advantage survives lexical-echo control."
            rows.append(
                {
                    "model": model,
                    "contrast": "christian_post_vs_secular_post_explanation_survival_ratio",
                    "group": "explanation",
                    "lhs_condition": "christian_post",
                    "rhs_condition": "secular_post",
                    "metric": "controlled/raw survival ratio",
                    "n_items": int(min(raw_row["n_items"], controlled_row["n_items"])),
                    "lhs_mean": math.nan,
                    "rhs_mean": math.nan,
                    "estimate": survival_ratio,
                    "ci_low": math.nan,
                    "ci_high": math.nan,
                    "p_value": math.nan,
                    "effect_size_dz": math.nan,
                    "interpretation": interpretation,
                }
            )
    return pd.DataFrame(rows)


def build_main_text_direct_contrasts(direct_contrasts_df: pd.DataFrame) -> pd.DataFrame:
    """Collapse the full direct-contrast table into the six paper headline rows."""
    if direct_contrasts_df.empty:
        return pd.DataFrame(
            columns=[
                "contrast",
                "contrast_label",
                "qwen_7b_estimate_pp",
                "qwen_7b_ci_low_pp",
                "qwen_7b_ci_high_pp",
                "qwen_7b_estimate_with_ci",
                "qwen_7b_p_value",
                "qwen_7b_effect_size_dz",
                "qwen_05b_estimate_pp",
                "qwen_05b_ci_low_pp",
                "qwen_05b_ci_high_pp",
                "qwen_05b_estimate_with_ci",
                "qwen_05b_p_value",
                "qwen_05b_effect_size_dz",
                "interpretation",
            ]
        )

    keep = direct_contrasts_df[direct_contrasts_df["contrast"].isin(MAIN_TEXT_CONTRASTS)].copy()
    rows: list[dict] = []
    for contrast in MAIN_TEXT_CONTRASTS:
        subset = keep[keep["contrast"] == contrast]
        if subset.empty:
            continue
        row: dict[str, object] = {
            "contrast": contrast,
            "contrast_label": MAIN_TEXT_CONTRAST_LABELS[contrast],
            "interpretation": "",
        }
        for model, prefix in [("qwen2.5:7b-instruct", "qwen_7b"), ("qwen2.5:0.5b-instruct", "qwen_05b")]:
            model_row = subset[subset["model"] == model]
            if model_row.empty:
                row[f"{prefix}_estimate_pp"] = math.nan
                row[f"{prefix}_ci_low_pp"] = math.nan
                row[f"{prefix}_ci_high_pp"] = math.nan
                row[f"{prefix}_estimate_with_ci"] = "n/a"
                row[f"{prefix}_p_value"] = math.nan
                row[f"{prefix}_effect_size_dz"] = math.nan
                continue
            series = model_row.iloc[0]
            row[f"{prefix}_estimate_pp"] = _pp(series["estimate"])
            row[f"{prefix}_ci_low_pp"] = _pp(series["ci_low"])
            row[f"{prefix}_ci_high_pp"] = _pp(series["ci_high"])
            row[f"{prefix}_estimate_with_ci"] = _format_pp_ci(series["estimate"], series["ci_low"], series["ci_high"])
            row[f"{prefix}_p_value"] = float(series["p_value"])
            row[f"{prefix}_effect_size_dz"] = float(series["effect_size_dz"])
            if model == "qwen2.5:7b-instruct":
                row["interpretation"] = str(series["interpretation"])
        rows.append(row)
    return pd.DataFrame(rows)


def build_appendix_direct_contrasts(direct_contrasts_df: pd.DataFrame) -> pd.DataFrame:
    """Format the full direct-contrast table for appendix export."""
    if direct_contrasts_df.empty:
        return pd.DataFrame()
    appendix = direct_contrasts_df[
        direct_contrasts_df["contrast"] != "christian_post_vs_secular_post_explanation_survival_ratio"
    ].copy()
    appendix["estimate_pp"] = appendix["estimate"].map(_pp)
    appendix["ci_low_pp"] = appendix["ci_low"].map(_pp)
    appendix["ci_high_pp"] = appendix["ci_high"].map(_pp)
    appendix["estimate_with_ci"] = appendix.apply(
        lambda row: _format_pp_ci(row["estimate"], row["ci_low"], row["ci_high"]),
        axis=1,
    )
    appendix["p_value_display"] = appendix["p_value"].map(_format_p_value)
    return appendix


def select_qualitative_examples(
    results_df: pd.DataFrame,
    *,
    item_df: pd.DataFrame | None,
    lexicons: dict | None = None,
) -> pd.DataFrame:
    """Select deterministic illustrative examples for the appendix and release notes."""
    working = enrich_results(results_df, lexicons=lexicons, item_df=item_df)
    working = working[working["model"] == "qwen2.5:7b-instruct"].copy()
    if working.empty:
        return pd.DataFrame()

    strict_terms = (lexicons or {}).get("strict_echo_terms", [])
    semantic_terms = (lexicons or {}).get("non_echo_semantic_terms", [])
    by_condition = {
        (row["item_id"], row["condition"]): row
        for row in working.to_dict(orient="records")
    }

    def _row(item_id: str, condition: str) -> dict | None:
        return by_condition.get((item_id, condition))

    def _example_record(*, item_id: str, rule_id: str, selection_rule: str, focal_condition: str, note: str) -> dict:
        focal = _row(item_id, focal_condition) or {}
        item_meta = None
        if item_df is not None and not item_df.empty:
            item_match = item_df[item_df["item_id"] == item_id]
            if not item_match.empty:
                item_meta = item_match.iloc[0].to_dict()
        explanation_text = focal.get("e_text")
        matched_echo = matched_terms(explanation_text, strict_terms)
        matched_semantic = matched_terms(explanation_text, semantic_terms)
        record: dict[str, object] = {
            "rule_id": rule_id,
            "selection_rule": selection_rule,
            "note": note,
            "model": "qwen2.5:7b-instruct",
            "item_id": item_id,
            "focal_condition": focal_condition,
            "primary_tension_tag": focal.get("primary_tension_tag") or (item_meta or {}).get("primary_tension_tag"),
            "scenario_context": focal.get("scenario_context") or (item_meta or {}).get("scenario_context"),
            "option_a": focal.get("option_a") or (item_meta or {}).get("option_a"),
            "option_b": focal.get("option_b") or (item_meta or {}).get("option_b"),
            "focal_explanation_text": explanation_text,
            "matched_strict_echo_terms": ", ".join(matched_echo),
            "matched_non_echo_terms": ", ".join(matched_semantic),
            "frame_echo_score": focal.get("frame_echo_score"),
            "semantic_score_raw": focal.get("semantic_score_raw"),
            "semantic_score_controlled": focal.get("semantic_score_controlled"),
            "restructure_beyond_echo": focal.get("restructure_beyond_echo"),
        }
        for condition in [
            "baseline",
            "secular_pre",
            "christian_pre",
            "secular_post",
            "christian_post",
        ]:
            source = _row(item_id, condition) or {}
            prefix = condition
            record[f"{prefix}_j1_act"] = source.get("j1_act")
            record[f"{prefix}_j1_heart"] = source.get("j1_heart")
            record[f"{prefix}_e_focus"] = source.get("e_focus")
            record[f"{prefix}_e_text"] = source.get("e_text")
            record[f"{prefix}_j2_act"] = source.get("j2_act")
            record[f"{prefix}_j2_heart"] = source.get("j2_heart")
        return record

    examples: list[dict] = []
    example1 = working[
        (working["condition"] == "christian_post")
        & (working["frame_echo_score"] > 0)
        & (working["semantic_score_controlled"] == 0)
    ].sort_values("item_id")
    if not example1.empty:
        examples.append(
            _example_record(
                item_id=str(example1.iloc[0]["item_id"]),
                rule_id="A1",
                selection_rule="Earliest 7B christian_post example with lexical echo present and zero controlled semantic score.",
                focal_condition="christian_post",
                note="Illustrates direct lexical echo without residual controlled-semantic content.",
            )
        )

    example2 = working[
        (working["condition"] == "christian_post")
        & (working["frame_echo_score"] == 0)
        & (working["semantic_score_controlled"] > 0)
    ].sort_values("item_id")
    if not example2.empty:
        examples.append(
            _example_record(
                item_id=str(example2.iloc[0]["item_id"]),
                rule_id="A2",
                selection_rule="Earliest 7B christian_post example with positive controlled semantic score and no strict lexical echo.",
                focal_condition="christian_post",
                note="Illustrates residual motive/heart semantics after lexical echo is absent.",
            )
        )

    pairs = build_condition_pairs(results_df, item_df=item_df, lexicons=lexicons)
    example3 = pairs[
        (pairs["model"] == "qwen2.5:7b-instruct")
        & (pairs["condition"] == "christian_pre")
        & (pairs["j1_heart_shift"] == 1)
        & (pairs["j1_act_shift"] == 0)
    ].sort_values("item_id")
    if not example3.empty:
        examples.append(
            _example_record(
                item_id=str(example3.iloc[0]["item_id"]),
                rule_id="A3",
                selection_rule="Earliest 7B christian_pre example with J1 heart shift relative to baseline and no J1 act shift.",
                focal_condition="christian_pre",
                note="Illustrates stage separation at first pass: heart judgment moves while act judgment stays fixed.",
            )
        )

    return pd.DataFrame(examples)


def build_figure_notes() -> str:
    """Return the interpretation notes shipped with the released paper figures."""
    return "\n".join(
        [
            "# Figure Notes",
            "",
            "## Figure 1: first_pass_shift.png",
            "- Data slice: `condition_summary.csv` rows for `secular_pre`, `christian_pre`, `secular_post`, `christian_post` across the two Qwen models.",
            "- Transformation: item-level shift rates vs baseline with bootstrap confidence intervals, plotted as within-condition act-versus-heart dumbbells.",
            "- Infer: heart-level pre-framing movement is larger than act-level movement; 0.5B attenuates that pattern.",
            "- Do not infer: a significant Christian-over-secular advantage from this figure alone.",
            "",
            "## Figure 2: explanation_layer_effect.png",
            "- Data slice: `condition_summary.csv` rows for the four framed conditions across both Qwen models.",
            "- Transformation: baseline deltas for coarse explanation focus, raw semantic score, and controlled semantic score, plotted as within-timing secular-versus-Christian comparisons.",
            "- Infer: explanation outputs are prompt-sensitive relative to baseline; the controlled row is the key diagnostic layer for checking whether anything survives lexical echo removal.",
            "- Do not infer: Christian-post exceeds secular-post after lexical control unless the direct contrast table also supports it.",
            "",
            "## Figure 3: judgment_explanation_dissociation.png",
            "- Data slice: `condition_summary.csv` rows for the four framed conditions across both Qwen models.",
            "- Transformation: x-axis is first-pass heart shift vs baseline; y-axis is controlled semantic explanation shift vs baseline; the dashed diagonal marks equal movement in both stages.",
            "- Infer: some conditions move explanation more than first-pass judgment.",
            "- Do not infer: Christian superiority or hidden internal mechanisms.",
            "",
            "## Figure 4: j1_j2_revision.png",
            "- Data slice: `revision_summary.csv` for `baseline`, `secular_pre`, `christian_pre`, `secular_post`, and `christian_post` across both Qwen models.",
            "- Transformation: condition-level act and heart revision rates from `J1` to `J2`, plotted as lollipops to emphasize small magnitudes rather than area.",
            "- Infer: revision is rare and secondary to explanation movement.",
            "- Do not infer: substantial downstream judgment rewriting.",
            "",
            "## Figure 5: cross_model_summary.png",
            "- Data slice: `direct_control_contrasts.csv` for the direct pre-framing heart contrast and direct post-framing controlled explanation contrast.",
            "- Transformation: paired Christian-minus-secular estimates with bootstrap intervals, connected across model size as a same-family slopegraph.",
            "- Infer: the smaller Qwen model attenuates the Christian-specific story.",
            "- Do not infer: scale-stable robustness of a Christian-specific mechanism.",
            "",
            "## Figure 6: heterogeneity_effects.png",
            "- Data slice: `heterogeneity_summary.csv` by `primary_tension_tag` for the two exploratory contrasts.",
            "- Transformation: within-tag Christian-minus-secular estimates with bootstrap intervals; labels include per-tag item counts from the locked eval split.",
            "- Infer: where motive-sensitive effects might concentrate.",
            "- Do not infer: confirmed category-level effects.",
            "",
        ]
    )


def compute_causal_contrasts(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Extract a compact contrast table from the broader condition summary frame."""
    rows = []
    for model in sorted(summary_df["model"].dropna().unique(), key=_model_sort_key):
        model_df = summary_df[summary_df["model"] == model].set_index("condition")
        if {"christian_pre", "secular_pre"}.issubset(model_df.index):
            rows.append(
                {
                    "model": model,
                    "contrast": "christian_minus_secular_pre_j1_act",
                    "estimate": float(model_df.loc["christian_pre", "j1_act_shift_rate"] - model_df.loc["secular_pre", "j1_act_shift_rate"]),
                }
            )
            rows.append(
                {
                    "model": model,
                    "contrast": "christian_minus_secular_pre_j1_heart",
                    "estimate": float(model_df.loc["christian_pre", "j1_heart_shift_rate"] - model_df.loc["secular_pre", "j1_heart_shift_rate"]),
                }
            )
        if {"christian_post", "secular_post"}.issubset(model_df.index):
            metric_name = (
                "semantic_score_controlled_delta_vs_baseline"
                if "semantic_score_controlled_delta_vs_baseline" in model_df.columns
                else "motive_focus_delta_vs_baseline"
            )
            rows.append(
                {
                    "model": model,
                    "contrast": "christian_minus_secular_post_semantic_controlled",
                    "estimate": float(
                        model_df.loc["christian_post", metric_name]
                        - model_df.loc["secular_post", metric_name]
                    ),
                }
            )
    return pd.DataFrame(rows)


def compute_revision_summary(results_df: pd.DataFrame, *, item_df: pd.DataFrame | None = None, lexicons: dict | None = None) -> pd.DataFrame:
    """Summarize J1-to-J2 revision rates, directions, and toward/away-moral-option movement."""
    pairs = build_condition_pairs(results_df, item_df=item_df, lexicons=lexicons)
    rows = []
    for model in sorted(pairs["model"].dropna().unique(), key=_model_sort_key):
        for condition in CONDITION_ORDER:
            if condition == "baseline":
                base = enrich_results(results_df, lexicons=lexicons, item_df=item_df)
                subset = base[(base["model"] == model) & (base["condition"] == "baseline")]
                if subset.empty:
                    continue
                rows.append(
                    {
                        "model": model,
                        "condition": condition,
                        "n_items": int(len(subset)),
                        "j2_act_revision_rate": _binary_mean(subset["j2_act_revision"]),
                        "j2_heart_revision_rate": _binary_mean(subset["j2_heart_revision"]),
                        "act_a_to_b_count": int(((subset["j1_act"] == "A") & (subset["j2_act"] == "B")).sum()),
                        "act_b_to_a_count": int(((subset["j1_act"] == "B") & (subset["j2_act"] == "A")).sum()),
                        "heart_a_to_b_count": int(((subset["j1_heart"] == "A") & (subset["j2_heart"] == "B")).sum()),
                        "heart_b_to_a_count": int(((subset["j1_heart"] == "B") & (subset["j2_heart"] == "A")).sum()),
                        "toward_moral_option_rate": float(
                            (
                                subset.get("j2_act", pd.Series(dtype=object)).eq(subset.get("moral_option", pd.Series(dtype=object)))
                                & subset.get("j1_act", pd.Series(dtype=object)).ne(subset.get("moral_option", pd.Series(dtype=object)))
                            ).mean()
                        )
                        if "moral_option" in subset.columns
                        else math.nan,
                        "away_from_moral_option_rate": float(
                            (
                                subset.get("j1_act", pd.Series(dtype=object)).eq(subset.get("moral_option", pd.Series(dtype=object)))
                                & subset.get("j2_act", pd.Series(dtype=object)).ne(subset.get("moral_option", pd.Series(dtype=object)))
                            ).mean()
                        )
                        if "moral_option" in subset.columns
                        else math.nan,
                    }
                )
                continue

            subset = pairs[(pairs["model"] == model) & (pairs["condition"] == condition)]
            if subset.empty:
                continue
            rows.append(
                {
                    "model": model,
                    "condition": condition,
                    "n_items": int(len(subset)),
                    "j2_act_revision_rate": _binary_mean(subset["j2_act_revision"]),
                    "j2_heart_revision_rate": _binary_mean(subset["j2_heart_revision"]),
                    "act_a_to_b_count": int(subset["act_a_to_b"].sum()),
                    "act_b_to_a_count": int(subset["act_b_to_a"].sum()),
                    "heart_a_to_b_count": int(subset["heart_a_to_b"].sum()),
                    "heart_b_to_a_count": int(subset["heart_b_to_a"].sum()),
                    "toward_moral_option_rate": _binary_mean(subset["toward_moral_option"]),
                    "away_from_moral_option_rate": _binary_mean(subset["away_from_moral_option"]),
                }
            )
    return pd.DataFrame(rows)


def compute_heterogeneity_summary(
    results_df: pd.DataFrame,
    *,
    item_df: pd.DataFrame | None,
    lexicons: dict | None = None,
    bootstrap_samples: int = 1000,
    bootstrap_seed: int = 42,
) -> pd.DataFrame:
    """Estimate exploratory direct contrasts within each locked primary tension tag."""
    if item_df is None or item_df.empty:
        return pd.DataFrame(
            columns=["model", "primary_tension_tag", "contrast", "n_items", "estimate", "ci_low", "ci_high"]
        )
    pairs = build_condition_pairs(results_df, item_df=item_df, lexicons=lexicons)
    rows = []
    for model in sorted(pairs["model"].dropna().unique(), key=_model_sort_key):
        for tag in TENSION_TAGS:
            tag_pairs = pairs[(pairs["model"] == model) & (pairs["primary_tension_tag"] == tag)]
            if tag_pairs.empty:
                continue
            for contrast, lhs, rhs, metric, metric_label in [
                ("pre_heart_shift", "christian_pre", "secular_pre", "j1_heart_shift", "Christian minus secular pre on J1 heart shift"),
                (
                    "post_controlled_explanation",
                    "christian_post",
                    "secular_post",
                    "semantic_score_controlled",
                    "Christian minus secular post on controlled explanation semantic score",
                ),
            ]:
                diffs = _paired_condition_values(
                    tag_pairs,
                    model=model,
                    lhs_condition=lhs,
                    rhs_condition=rhs,
                    value_column=metric,
                )
                estimate, ci_low, ci_high = _metric_with_ci(
                    diffs.tolist(),
                    bootstrap_samples=bootstrap_samples,
                    bootstrap_seed=bootstrap_seed,
                )
                rows.append(
                    {
                        "model": model,
                        "primary_tension_tag": tag,
                        "contrast": contrast,
                        "metric": metric_label,
                        "n_items": int(len(diffs)),
                        "estimate": estimate,
                        "ci_low": ci_low,
                        "ci_high": ci_high,
                    }
                )
    return pd.DataFrame(rows)


def compute_family_audit_summary(
    results_df: pd.DataFrame,
    *,
    item_df: pd.DataFrame | None = None,
    lexicons: dict | None = None,
    bootstrap_samples: int = 1000,
    bootstrap_seed: int = 42,
) -> pd.DataFrame:
    """Aggregate paraphrase-family audit rows when those runs are present in the input data."""
    audit_rows = _filter_frame_mode(results_df, "family_audit")
    if audit_rows.empty:
        return pd.DataFrame(
            columns=[
                "model",
                "contrast",
                "family_mean_estimate",
                "ci_low",
                "ci_high",
                "min_variant_estimate",
                "max_variant_estimate",
                "sign_stable_across_pairs",
                "n_pairwise_variant_contrasts",
            ]
        )
    pairs = build_condition_pairs(audit_rows, item_df=item_df, lexicons=lexicons)
    rows = []
    for model in sorted(pairs["model"].dropna().unique(), key=_model_sort_key):
        for contrast, lhs, rhs, metric in [
            ("family_audit_pre_heart_shift", "christian_pre", "secular_pre", "j1_heart_shift"),
            (
                "family_audit_post_controlled_explanation",
                "christian_post",
                "secular_post",
                "semantic_score_controlled",
            ),
        ]:
            subset = pairs[(pairs["model"] == model) & (pairs["condition"].isin([lhs, rhs]))].copy()
            if subset.empty:
                continue
            family_means = subset.groupby(["item_id", "condition"], as_index=False)[metric].mean()
            family_wide = family_means.pivot(index="item_id", columns="condition", values=metric)
            if lhs not in family_wide.columns or rhs not in family_wide.columns:
                continue
            family_diffs = (family_wide[lhs] - family_wide[rhs]).dropna()
            estimate, ci_low, ci_high = _metric_with_ci(
                family_diffs.tolist(),
                bootstrap_samples=bootstrap_samples,
                bootstrap_seed=bootstrap_seed,
            )

            lhs_variants = sorted(subset[subset["condition"] == lhs]["frame_variant_id"].dropna().unique())
            rhs_variants = sorted(subset[subset["condition"] == rhs]["frame_variant_id"].dropna().unique())
            pairwise_estimates = []
            for lhs_variant in lhs_variants:
                lhs_values = subset[(subset["condition"] == lhs) & (subset["frame_variant_id"] == lhs_variant)][
                    ["item_id", metric]
                ].rename(columns={metric: "lhs_value"})
                for rhs_variant in rhs_variants:
                    rhs_values = subset[(subset["condition"] == rhs) & (subset["frame_variant_id"] == rhs_variant)][
                        ["item_id", metric]
                    ].rename(columns={metric: "rhs_value"})
                    merged = lhs_values.merge(rhs_values, on="item_id", how="inner")
                    if merged.empty:
                        continue
                    pairwise_estimates.append(float((merged["lhs_value"] - merged["rhs_value"]).mean()))
            nonzero_signs = {int(math.copysign(1, value)) for value in pairwise_estimates if value != 0}
            rows.append(
                {
                    "model": model,
                    "contrast": contrast,
                    "family_mean_estimate": estimate,
                    "ci_low": ci_low,
                    "ci_high": ci_high,
                    "min_variant_estimate": float(min(pairwise_estimates)) if pairwise_estimates else math.nan,
                    "max_variant_estimate": float(max(pairwise_estimates)) if pairwise_estimates else math.nan,
                    "sign_stable_across_pairs": len(nonzero_signs) <= 1 if pairwise_estimates else False,
                    "n_pairwise_variant_contrasts": len(pairwise_estimates),
                }
            )
    return pd.DataFrame(rows)


def compute_mixed_effects(paired_df: pd.DataFrame) -> pd.DataFrame:
    """Run lightweight mixed-effects confirmation models on the paired item frame."""
    if paired_df.empty:
        return pd.DataFrame(
            columns=["model", "metric", "term", "coef", "std_err", "z_or_t", "pvalue", "converged", "notes"]
        )
    metrics = [
        "j1_act_shift",
        "j1_heart_shift",
        "j2_act_revision",
        "j2_heart_revision",
        "motive_focus_shift",
        "semantic_controlled_present",
        "dissociated_explanation_shift",
    ]
    rows = []
    for model in sorted(paired_df["model"].unique(), key=_model_sort_key):
        model_df = paired_df[paired_df["model"] == model].copy()
        for metric in metrics:
            metric_values = model_df[metric].dropna()
            if model_df["item_id"].nunique() < 10:
                rows.append(
                    {
                        "model": model,
                        "metric": metric,
                        "term": "MODEL_SKIPPED",
                        "coef": math.nan,
                        "std_err": math.nan,
                        "z_or_t": math.nan,
                        "pvalue": math.nan,
                        "converged": False,
                        "notes": "insufficient_items_for_stable_mixedlm",
                    }
                )
                continue
            if metric_values.empty or metric_values.nunique() < 2:
                rows.append(
                    {
                        "model": model,
                        "metric": metric,
                        "term": "MODEL_SKIPPED",
                        "coef": math.nan,
                        "std_err": math.nan,
                        "z_or_t": math.nan,
                        "pvalue": math.nan,
                        "converged": False,
                        "notes": "no_metric_variation",
                    }
                )
                continue
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fit = smf.mixedlm(
                        f"{metric} ~ C(condition)",
                        data=model_df,
                        groups=model_df["item_id"],
                    ).fit(reml=False)
                converged = bool(getattr(fit, "converged", True))
                for term in fit.params.index:
                    rows.append(
                        {
                            "model": model,
                            "metric": metric,
                            "term": term,
                            "coef": float(fit.params[term]),
                            "std_err": float(fit.bse[term]),
                            "z_or_t": float(fit.tvalues[term]),
                            "pvalue": float(fit.pvalues[term]),
                            "converged": converged,
                            "notes": "",
                        }
                    )
            except Exception as exc:
                rows.append(
                    {
                        "model": model,
                        "metric": metric,
                        "term": "MODEL_FAILED",
                        "coef": math.nan,
                        "std_err": math.nan,
                        "z_or_t": math.nan,
                        "pvalue": math.nan,
                        "converged": False,
                        "notes": type(exc).__name__,
                    }
                )
    return pd.DataFrame(rows)


def plot_first_pass_shift(summary_df: pd.DataFrame, output_path: str | Path) -> Path:
    """Render the released figure comparing first-pass act and heart shift rates."""
    plot_df = summary_df[summary_df["condition"].isin({"secular_pre", "christian_pre", "secular_post", "christian_post"})].copy()
    models = sorted(plot_df["model"].dropna().unique(), key=_model_sort_key)
    fig, axes = plt.subplots(1, len(models), figsize=(12.6, 5.7), sharey=True, sharex=True)
    if len(models) == 1:
        axes = [axes]
    display_order = {
        "secular_post": 0,
        "christian_post": 1,
        "secular_pre": 2,
        "christian_pre": 3,
    }

    def _ci_series(frame: pd.DataFrame, primary: str, fallback: str, value_col: str) -> pd.Series:
        if primary in frame.columns and frame[primary].notna().any():
            return pd.to_numeric(frame[primary], errors="coerce").fillna(frame[value_col])
        if fallback in frame.columns and frame[fallback].notna().any():
            return pd.to_numeric(frame[fallback], errors="coerce").fillna(frame[value_col])
        return pd.to_numeric(frame[value_col], errors="coerce")

    global_high = []
    for _, row in plot_df.iterrows():
        global_high.extend(
            [
                row.get("j1_act_shift_rate_ci_high", row.get("j1_act_shift_ci_high", row.get("j1_act_shift_rate", 0.0))),
                row.get("j1_heart_shift_rate_ci_high", row.get("j1_heart_shift_ci_high", row.get("j1_heart_shift_rate", 0.0))),
            ]
        )
    x_max = max(float(np.nanmax(np.array(global_high, dtype=float))), 0.02) + 0.04

    for ax, model in zip(axes, models, strict=True):
        model_df = plot_df[plot_df["model"] == model].copy()
        model_df["order"] = model_df["condition"].map(display_order)
        model_df = model_df.sort_values("order")
        ypos = np.arange(len(model_df))

        act = model_df["j1_act_shift_rate"].to_numpy()
        heart = model_df["j1_heart_shift_rate"].to_numpy()
        act_low = _ci_series(model_df, "j1_act_shift_rate_ci_low", "j1_act_shift_ci_low", "j1_act_shift_rate").to_numpy()
        act_high = _ci_series(model_df, "j1_act_shift_rate_ci_high", "j1_act_shift_ci_high", "j1_act_shift_rate").to_numpy()
        heart_low = _ci_series(model_df, "j1_heart_shift_rate_ci_low", "j1_heart_shift_ci_low", "j1_heart_shift_rate").to_numpy()
        heart_high = _ci_series(model_df, "j1_heart_shift_rate_ci_high", "j1_heart_shift_ci_high", "j1_heart_shift_rate").to_numpy()
        act_err = np.vstack([np.clip(act - act_low, 0, None), np.clip(act_high - act, 0, None)])
        heart_err = np.vstack([np.clip(heart - heart_low, 0, None), np.clip(heart_high - heart, 0, None)])

        _add_pre_post_bands(ax, pre=(-0.5, 1.5), post=(1.5, 3.5))
        ax.axvline(0, color="#6F6F6F", linewidth=1.0)
        for y, x_act, x_heart in zip(ypos, act, heart, strict=True):
            ax.plot([x_act, x_heart], [y, y], color="#BEC6D1", linewidth=2.2, zorder=1)
        ax.errorbar(
            act,
            ypos,
            xerr=act_err,
            fmt="o",
            color=MEASURE_COLORS["act"],
            markeredgecolor="#2D3A4A",
            markeredgewidth=0.8,
            markersize=7.5,
            capsize=3,
            linewidth=1.5,
            label="J1 overall problematic",
        )
        ax.errorbar(
            heart,
            ypos,
            xerr=heart_err,
            fmt="D",
            color=MEASURE_COLORS["heart"],
            markeredgecolor="#4A2323",
            markeredgewidth=0.8,
            markersize=7.2,
            capsize=3,
            linewidth=1.5,
            label="J1 heart / motive worse",
        )
        ax.set_title(_model_label(model), fontsize=11)
        ax.set_yticks(ypos)
        ax.set_yticklabels([_condition_label(condition) for condition in model_df["condition"]])
        ax.invert_yaxis()
        ax.set_xlabel("Items shifted vs baseline")
        ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.set_xlim(-0.002, x_max)
        ax.text(
            0.985,
            0.80,
            "Pre-J1\nframe",
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=8.5,
            color="#55708D",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.78},
        )
        ax.text(
            0.985,
            0.23,
            "Post-J1\nframe",
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=8.5,
            color="#9B6A3D",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": "none", "alpha": 0.78},
        )
        _style_axis(ax, grid_axis="x")

    axes[0].set_ylabel("Condition")
    handles = [
        Line2D([0], [0], marker="o", color=MEASURE_COLORS["act"], label="J1 overall problematic", markersize=7, linestyle=""),
        Line2D([0], [0], marker="D", color=MEASURE_COLORS["heart"], label="J1 heart / motive worse", markersize=7, linestyle=""),
        Line2D([0, 1], [0, 0], color="#BEC6D1", linewidth=2.2, label="Within-condition gap"),
    ]
    fig.suptitle("First-pass movement is concentrated in heart-level judgments", x=0.06, ha="left", fontweight="bold")
    fig.text(
        0.06,
        0.92,
        "Within each timing, heart-level movement exceeds act-level movement. Ordering the rows by framing position makes the pre-versus-post distinction readable at a glance.",
        fontsize=9,
        color="#4E4E4E",
    )
    fig.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=3)
    fig.tight_layout()
    fig.subplots_adjust(top=0.84, bottom=0.17)
    out = _save_release_png(fig, output_path)
    plt.close(fig)
    return out


def plot_explanation_layer_effect(summary_df: pd.DataFrame, output_path: str | Path) -> Path:
    """Render the released figure for coarse, raw, and lexical-controlled explanation movement."""
    plot_df = summary_df[summary_df["condition"].isin({"secular_pre", "christian_pre", "secular_post", "christian_post"})].copy()
    plot_df["order"] = plot_df["condition"].map(_condition_sort_key)
    plot_df = plot_df.sort_values(["model", "order"], key=lambda s: s.map(_model_sort_key) if s.name == "model" else s)
    models = sorted(plot_df["model"].dropna().unique(), key=_model_sort_key)
    raw_metric = (
        "semantic_score_raw_delta_vs_baseline"
        if "semantic_score_raw_delta_vs_baseline" in plot_df.columns
        else "semantic_raw_delta_vs_baseline"
    )
    controlled_metric = (
        "semantic_score_controlled_delta_vs_baseline"
        if "semantic_score_controlled_delta_vs_baseline" in plot_df.columns
        else "semantic_controlled_delta_vs_baseline"
    )
    metrics = [
        ("motive_focus_delta_vs_baseline", "Coarse motive/heart label", MEASURE_COLORS["coarse"]),
        (raw_metric, "Raw Christian / heart-language score", MEASURE_COLORS["raw"]),
        (controlled_metric, "Lexical-controlled semantic score", MEASURE_COLORS["controlled"]),
    ]
    fig, axes = plt.subplots(len(metrics), len(models), figsize=(12.8, 9.8), sharex="row", sharey=True)
    if len(models) == 1:
        axes = np.array([[ax] for ax in axes])

    metric_limits: dict[str, tuple[float, float]] = {}
    timing_pairs = [
        ("Pre-J1 frame", "secular_pre", "christian_pre"),
        ("Post-J1 frame", "secular_post", "christian_post"),
    ]
    for metric, _, _ in metrics:
        vals = pd.to_numeric(plot_df[metric], errors="coerce")
        lows = pd.to_numeric(plot_df.get(f"{metric}_ci_low", vals), errors="coerce")
        highs = pd.to_numeric(plot_df.get(f"{metric}_ci_high", vals), errors="coerce")
        x_min = min(float(np.nanmin(np.append(lows.to_numpy(), 0.0))), -0.01)
        x_max = max(float(np.nanmax(np.append(highs.to_numpy(), 0.01))), 0.01)
        pad = max(0.015, 0.08 * (x_max - x_min if x_max > x_min else 0.1))
        metric_limits[metric] = (x_min - pad, x_max + pad)

    for row_idx, (metric, title, color) in enumerate(metrics):
        for col_idx, model in enumerate(models):
            ax = axes[row_idx, col_idx]
            model_df = plot_df[plot_df["model"] == model].set_index("condition")
            ax.axvline(0, color="#6F6F6F", linewidth=1.0)
            _add_pre_post_bands(ax, pre=(-0.5, 0.5), post=(0.5, 1.5))
            for y, (_, secular_condition, christian_condition) in zip([0, 1], timing_pairs, strict=True):
                secular_row = model_df.loc[secular_condition]
                christian_row = model_df.loc[christian_condition]
                sec_val = float(secular_row[metric])
                chr_val = float(christian_row[metric])
                sec_low = float(secular_row.get(f"{metric}_ci_low", sec_val))
                sec_high = float(secular_row.get(f"{metric}_ci_high", sec_val))
                chr_low = float(christian_row.get(f"{metric}_ci_low", chr_val))
                chr_high = float(christian_row.get(f"{metric}_ci_high", chr_val))
                ax.plot([sec_val, chr_val], [y, y], color="#C5CBD4", linewidth=2.2, zorder=1)
                ax.errorbar(
                    sec_val,
                    y,
                    xerr=np.array([[max(sec_val - sec_low, 0)], [max(sec_high - sec_val, 0)]]),
                    fmt="o",
                    color=FRAME_COLORS["secular"],
                    ecolor=FRAME_COLORS["secular"],
                    markeredgecolor="#244A6A",
                    markeredgewidth=0.8,
                    markersize=6.8,
                    capsize=3,
                    linewidth=1.4,
                    zorder=3,
                )
                ax.errorbar(
                    chr_val,
                    y,
                    xerr=np.array([[max(chr_val - chr_low, 0)], [max(chr_high - chr_val, 0)]]),
                    fmt="D",
                    color=FRAME_COLORS["christian"],
                    ecolor=FRAME_COLORS["christian"],
                    markeredgecolor="#6C3B14",
                    markeredgewidth=0.8,
                    markersize=6.4,
                    capsize=3,
                    linewidth=1.4,
                    zorder=3,
                )
            ax.set_yticks([0, 1])
            ax.set_yticklabels([label for label, _, _ in timing_pairs])
            ax.invert_yaxis()
            ax.set_xlim(*metric_limits[metric])
            ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            ax.set_title(_model_label(model) if row_idx == 0 else "", fontsize=11)
            if col_idx == 0:
                ax.set_ylabel(title)
            _style_axis(ax, grid_axis="x")
            if row_idx == len(metrics) - 1:
                ax.set_xlabel("Change vs baseline")

    handles = [
        Line2D([0], [0], marker="o", color=FRAME_COLORS["secular"], markeredgecolor="#244A6A", label="Secular control", markersize=7, linestyle=""),
        Line2D([0], [0], marker="D", color=FRAME_COLORS["christian"], markeredgecolor="#6C3B14", label="Christian frame", markersize=6.8, linestyle=""),
        Line2D([0, 1], [0, 0], color="#C5CBD4", linewidth=2.2, label="Within-timing comparison"),
    ]
    fig.suptitle("Explanation movement is clear, but matched-control residuals remain weak", x=0.06, ha="left", fontweight="bold")
    fig.text(
        0.06,
        0.95,
        "Each row compares secular and Christian framing within the same timing. The controlled row is the key diagnostic layer because direct lexical echo has been removed.",
        fontsize=9,
        color="#4E4E4E",
    )
    fig.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=3)
    fig.tight_layout()
    fig.subplots_adjust(top=0.9, bottom=0.12)
    out = _save_release_png(fig, output_path)
    plt.close(fig)
    return out


def plot_judgment_explanation_dissociation(summary_df: pd.DataFrame, output_path: str | Path) -> Path:
    """Plot explanation movement against first-pass movement to visualize stage dissociation."""
    plot_df = summary_df[summary_df["condition"].isin({"secular_pre", "christian_pre", "secular_post", "christian_post"})].copy()
    y_metric = (
        "semantic_score_controlled_delta_vs_baseline"
        if "semantic_score_controlled_delta_vs_baseline" in plot_df.columns
        else "semantic_controlled_delta_vs_baseline"
    )
    models = sorted(plot_df["model"].dropna().unique(), key=_model_sort_key)
    fig, axes = plt.subplots(1, len(models), figsize=(12.0, 5.8), sharex=True, sharey=True)
    if len(models) == 1:
        axes = [axes]
    limit_min = min(float(plot_df["j1_heart_shift_rate"].min()), float(plot_df[y_metric].min()), 0.0) - 0.01
    limit_max = max(float(plot_df["j1_heart_shift_rate"].max()), float(plot_df[y_metric].max()), 0.01) + 0.02

    for ax, model in zip(axes, models, strict=True):
        model_df = plot_df[plot_df["model"] == model]
        ax.axvline(0, color="#7A7A7A", linewidth=1.0)
        ax.axhline(0, color="#7A7A7A", linewidth=1.0)
        ax.plot([limit_min, limit_max], [limit_min, limit_max], linestyle="--", color="#B0B6BE", linewidth=1.2, zorder=0)
        ax.fill_between([limit_min, limit_max], [limit_min, limit_max], limit_max, color="#F0F7F3", alpha=0.6, zorder=0)
        for row in model_df.itertuples():
            ax.scatter(
                row.j1_heart_shift_rate,
                getattr(row, y_metric),
                s=125,
                marker=_condition_marker(row.condition),
                color=_condition_color(row.condition),
                edgecolor="#303030",
                linewidth=0.9,
            )
            ax.annotate(
                {
                    "secular_pre": "S-pre",
                    "christian_pre": "C-pre",
                    "secular_post": "S-post",
                    "christian_post": "C-post",
                }.get(row.condition, _condition_label(row.condition)),
                (row.j1_heart_shift_rate, getattr(row, y_metric)),
                xytext=(8, 9 if "christian" in row.condition else -14),
                textcoords="offset points",
                fontsize=9,
                bbox={"boxstyle": "round,pad=0.18", "fc": "white", "ec": "none", "alpha": 0.82},
            )
        ax.set_title(_model_label(model), fontsize=11)
        ax.set_xlabel("First-pass heart shift vs baseline")
        ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.set_xlim(limit_min, limit_max)
        ax.set_ylim(limit_min, limit_max)
        ax.set_aspect("equal", adjustable="box")
        ax.text(0.04, 0.93, "Explanation > J1", transform=ax.transAxes, fontsize=8.5, color="#48745D")
        _style_axis(ax, grid_axis="both")

    axes[0].set_ylabel("Lexical-controlled explanation shift vs baseline")
    handles = [
        Patch(facecolor=FRAME_COLORS["christian"], edgecolor="#303030", label="Christian frame"),
        Patch(facecolor=FRAME_COLORS["secular"], edgecolor="#303030", label="Secular frame"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#666666", markeredgecolor="#303030", label="Pre-J1 framing", markersize=7),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#666666", markeredgecolor="#303030", label="Post-J1 framing", markersize=7),
    ]
    fig.suptitle("Explanation change can outpace first-pass judgment change", x=0.06, ha="left", fontweight="bold")
    fig.text(
        0.06,
        0.92,
        "The dashed diagonal marks equal movement in the two stages. Points above that line indicate stronger explanation movement than first-pass heart movement.",
        fontsize=9,
        color="#4E4E4E",
    )
    fig.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=4)
    fig.tight_layout()
    fig.subplots_adjust(top=0.84, bottom=0.18)
    out = _save_release_png(fig, output_path)
    plt.close(fig)
    return out


def plot_revision_figure(revision_df: pd.DataFrame, output_path: str | Path) -> Path:
    """Render the released J1-to-J2 revision figure with low-area lollipop marks."""
    plot_df = revision_df[revision_df["condition"].isin(CONDITION_ORDER)].copy()
    models = sorted(plot_df["model"].dropna().unique(), key=_model_sort_key)
    fig, axes = plt.subplots(2, len(models), figsize=(12.8, 7.6), sharex=True, sharey="row")
    if len(models) == 1:
        axes = np.array([[axes[0]], [axes[1]]])
    metrics = [("j2_act_revision_rate", "Act revision rate"), ("j2_heart_revision_rate", "Heart revision rate")]
    x_max = max(float(plot_df["j2_act_revision_rate"].max()), float(plot_df["j2_heart_revision_rate"].max()), 0.01) + 0.03

    for row_idx, (metric, title) in enumerate(metrics):
        for col_idx, model in enumerate(models):
            ax = axes[row_idx, col_idx]
            model_df = plot_df[plot_df["model"] == model].copy()
            model_df["order"] = model_df["condition"].map(_condition_sort_key)
            model_df = model_df.sort_values("order")
            positions = np.arange(len(model_df))
            _add_pre_post_bands(ax, pre=(0.5, 2.5), post=(2.5, 4.5))
            for y, row in zip(positions, model_df.itertuples(), strict=True):
                value = float(getattr(row, metric))
                ax.hlines(y, 0, value, color="#C8CED6", linewidth=2.0, zorder=1)
                ax.scatter(
                    value,
                    y,
                    s=70,
                    marker="s" if row.condition.endswith("post") else "o",
                    color=_condition_color(row.condition),
                    edgecolor="#404040",
                    linewidth=0.8,
                    zorder=3,
                )
                ax.text(value + x_max * 0.02, y, _format_pct_text(value), va="center", ha="left", fontsize=8.5, color="#4E4E4E")
            ax.set_title(_model_label(model) if row_idx == 0 else "", fontsize=11)
            ax.set_ylabel(title)
            ax.set_yticks(positions)
            ax.set_yticklabels([_condition_label(condition) for condition in model_df["condition"]])
            ax.invert_yaxis()
            ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
            ax.set_xlim(0, x_max)
            if row_idx == len(metrics) - 1:
                ax.set_xlabel("Revision rate")
            _style_axis(ax, grid_axis="x")

    fig.suptitle("J1-to-J2 revision remains rare", x=0.06, ha="left", fontweight="bold")
    fig.text(
        0.06,
        0.93,
        "Revision is treated as a secondary mechanism check rather than a primary estimand: most rates stay close to zero even when explanation language moves.",
        fontsize=9,
        color="#4E4E4E",
    )
    fig.tight_layout()
    fig.subplots_adjust(top=0.88)
    out = _save_release_png(fig, output_path)
    plt.close(fig)
    return out


def plot_heterogeneity(heterogeneity_df: pd.DataFrame, output_path: str | Path) -> Path:
    """Render the exploratory heterogeneity figure across the locked item categories."""
    if heterogeneity_df.empty:
        raise ValueError("No heterogeneity results available.")
    metrics = [
        ("pre_heart_shift", "Christian - secular pre on J1 heart shift"),
        ("post_controlled_explanation", "Christian - secular post on controlled explanation shift"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.9), sharey=True)
    model_colors = {"qwen2.5:7b-instruct": "#B04A5A", "qwen2.5:0.5b-instruct": "#4C78A8"}
    model_markers = {"qwen2.5:7b-instruct": "o", "qwen2.5:0.5b-instruct": "s"}
    counts = heterogeneity_df.groupby("primary_tension_tag")["n_items"].max().to_dict()
    labels = [f"{tag.replace('_', ' ')} (n={int(counts.get(tag, 0))})" for tag in TENSION_TAGS]
    limit = max(
        float(np.abs(heterogeneity_df["ci_low"]).max()),
        float(np.abs(heterogeneity_df["ci_high"]).max()),
        0.05,
    ) + 0.03
    for ax, (contrast, title) in zip(axes, metrics, strict=True):
        subset = heterogeneity_df[heterogeneity_df["contrast"] == contrast].copy()
        subset["tag_order"] = subset["primary_tension_tag"].map({tag: idx for idx, tag in enumerate(TENSION_TAGS)})
        subset = subset.sort_values(["tag_order", "model"], key=lambda s: s.map(_model_sort_key) if s.name == "model" else s)
        y_lookup = {tag: idx for idx, tag in enumerate(TENSION_TAGS)}
        offsets = {"qwen2.5:7b-instruct": -0.12, "qwen2.5:0.5b-instruct": 0.12}
        ax.axvline(0, color="#7A7A7A", linewidth=1.0)
        for row in subset.itertuples():
            y = y_lookup[row.primary_tension_tag] + offsets.get(row.model, 0.0)
            ax.errorbar(
                row.estimate,
                y,
                xerr=[[max(row.estimate - row.ci_low, 0)], [max(row.ci_high - row.estimate, 0)]],
                fmt=model_markers.get(row.model, "o"),
                color=model_colors.get(row.model, "#4E4E4E"),
                ecolor=model_colors.get(row.model, "#4E4E4E"),
                markersize=6.5,
                capsize=3,
                linewidth=1.4,
            )
        ax.set_title(title, fontsize=11)
        ax.set_yticks(np.arange(len(TENSION_TAGS)))
        ax.set_yticklabels(labels)
        ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.set_xlabel("Direct Christian - secular estimate")
        ax.set_xlim(-limit, limit)
        _style_axis(ax, grid_axis="x")
    axes[0].set_ylabel("Item category")
    handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=model_colors["qwen2.5:7b-instruct"], markeredgecolor=model_colors["qwen2.5:7b-instruct"], label="Qwen 2.5 7B", markersize=6),
        Line2D([0], [0], marker="s", color="none", markerfacecolor=model_colors["qwen2.5:0.5b-instruct"], markeredgecolor=model_colors["qwen2.5:0.5b-instruct"], label="Qwen 2.5 0.5B", markersize=6),
    ]
    fig.suptitle("Exploratory heterogeneity by item type", x=0.06, ha="left", fontweight="bold")
    fig.legend(handles=handles, frameon=False, loc="upper center", bbox_to_anchor=(0.5, 0.03), ncol=2)
    fig.tight_layout()
    fig.subplots_adjust(top=0.85, bottom=0.18)
    out = _save_release_png(fig, output_path)
    plt.close(fig)
    return out


def plot_cross_model_comparison(direct_contrasts_df: pd.DataFrame, output_path: str | Path) -> Path:
    """Render the same-family cross-model comparison for the two key matched-control contrasts."""
    if "contrast" not in direct_contrasts_df.columns:
        direct_contrasts_df = compute_causal_contrasts(direct_contrasts_df)
        direct_contrasts_df["contrast"] = direct_contrasts_df["contrast"].replace(
            {
                "christian_minus_secular_pre_j1_heart": "christian_pre_vs_secular_pre_j1_heart_shift",
                "christian_minus_secular_post_semantic_controlled": "christian_post_vs_secular_post_explanation_controlled",
            }
        )
    if "ci_low" not in direct_contrasts_df.columns:
        direct_contrasts_df["ci_low"] = direct_contrasts_df["estimate"]
    if "ci_high" not in direct_contrasts_df.columns:
        direct_contrasts_df["ci_high"] = direct_contrasts_df["estimate"]

    plot_df = direct_contrasts_df[
        direct_contrasts_df["contrast"].isin(
            [
                "christian_pre_vs_secular_pre_j1_heart_shift",
                "christian_post_vs_secular_post_explanation_controlled",
            ]
        )
    ].copy()
    if plot_df.empty:
        raise ValueError("No eligible direct-control contrasts found for cross-model comparison.")
    plot_df["panel"] = plot_df["contrast"].map(
        {
            "christian_pre_vs_secular_pre_j1_heart_shift": "A. Direct pre-framing heart contrast",
            "christian_post_vs_secular_post_explanation_controlled": "B. Direct post-framing controlled explanation contrast",
        }
    )
    panels = ["A. Direct pre-framing heart contrast", "B. Direct post-framing controlled explanation contrast"]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.2), sharey=True)
    y_limit = max(float(np.abs(plot_df["ci_low"]).max()), float(np.abs(plot_df["ci_high"]).max()), 0.05) + 0.02
    for ax, panel in zip(axes, panels, strict=True):
        subset = plot_df[plot_df["panel"] == panel].copy()
        subset = subset.sort_values("model", key=lambda s: s.map(_model_sort_key))
        x = np.arange(len(subset))
        color = FRAME_COLORS["christian"] if "heart" in subset["contrast"].iloc[0] else MEASURE_COLORS["controlled"]
        ax.axhline(0, color="#7A7A7A", linewidth=1.0)
        ax.plot(x, subset["estimate"], color=color, linewidth=2.2, zorder=1)
        ax.errorbar(
            x,
            subset["estimate"],
            yerr=np.vstack(
                [
                    np.clip(subset["estimate"] - subset["ci_low"], 0, None),
                    np.clip(subset["ci_high"] - subset["estimate"], 0, None),
                ]
            ),
            fmt="o",
            color=color,
            ecolor=color,
            markeredgecolor="#303030",
            markeredgewidth=0.8,
            markersize=7.5,
            capsize=3,
            linewidth=1.4,
            zorder=3,
        )
        for xi, row in zip(x, subset.itertuples(), strict=True):
            va = "bottom" if row.estimate >= 0 else "top"
            offset = 0.012 if row.estimate >= 0 else -0.014
            ax.text(xi, row.estimate + offset, f"{row.estimate:+.1%}", va=va, ha="center", fontsize=9, color="#333333")
        ax.set_title(panel, fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels([_model_label(model).replace("Qwen 2.5 ", "") for model in subset["model"]])
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.set_ylim(-y_limit, y_limit)
        ax.set_xlabel("Model size")
        _style_axis(ax, grid_axis="y")
    axes[0].set_ylabel("Christian - secular paired estimate")
    fig.suptitle("Same-family scale comparison highlights attenuation across Qwen size", x=0.06, ha="left", fontweight="bold")
    fig.text(
        0.06,
        0.92,
        "Each panel connects the same matched-control contrast across Qwen sizes, making attenuation and sign instability visible at a glance.",
        fontsize=9,
        color="#4E4E4E",
    )
    fig.tight_layout()
    fig.subplots_adjust(top=0.84)
    out = _save_release_png(fig, output_path)
    plt.close(fig)
    return out


def write_analysis_report(
    summary_df: pd.DataFrame,
    direct_contrasts_df: pd.DataFrame,
    sanity_df: pd.DataFrame,
    revision_df: pd.DataFrame,
    heterogeneity_df: pd.DataFrame,
    mixed_effects_df: pd.DataFrame,
    *,
    family_audit_df: pd.DataFrame | None = None,
    output_path: str | Path,
) -> Path:
    """Write the compact markdown analysis report shipped with each released analysis bundle."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Christian Framing x SIM Analysis",
        "",
        "## Condition Summary",
        "",
        summary_df.to_markdown(index=False),
        "",
        "## Direct Christian-vs-Secular Contrasts",
        "",
        direct_contrasts_df.to_markdown(index=False) if not direct_contrasts_df.empty else "No direct contrasts available.",
        "",
        "## Sanity Agreement",
        "",
        sanity_df.to_markdown(index=False) if not sanity_df.empty else "No sanity subset available.",
        "",
        "## J1 to J2 Revision Summary",
        "",
        revision_df.to_markdown(index=False) if not revision_df.empty else "No revision summary available.",
        "",
        "## Heterogeneity",
        "",
        heterogeneity_df.to_markdown(index=False) if not heterogeneity_df.empty else "No heterogeneity summary available.",
        "",
        "## Mixed Effects",
        "",
        mixed_effects_df.to_markdown(index=False) if not mixed_effects_df.empty else "No mixed-effects output available.",
        "",
    ]
    if family_audit_df is not None:
        lines.extend(
            [
                "## Paraphrase Family Audit",
                "",
                family_audit_df.to_markdown(index=False) if not family_audit_df.empty else "No family-audit rows available.",
                "",
            ]
        )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def plot_shift_figure(summary_df: pd.DataFrame, output_path: str | Path) -> Path:
    return plot_first_pass_shift(summary_df, output_path)


def plot_explanation_focus(summary_df: pd.DataFrame, output_path: str | Path) -> Path:
    return plot_explanation_layer_effect(summary_df, output_path)


def plot_judgment_flow(frame: pd.DataFrame, output_path: str | Path) -> Path:
    if "j1_heart_shift_rate" in frame.columns:
        summary_df = frame
    else:
        summary_df = compute_condition_summary(frame, bootstrap_samples=200, bootstrap_seed=42)
    return plot_judgment_explanation_dissociation(summary_df, output_path)
