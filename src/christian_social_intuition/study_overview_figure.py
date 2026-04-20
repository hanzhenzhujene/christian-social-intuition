from __future__ import annotations

"""Build the repository's study-overview figure from the current released artifacts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import PercentFormatter
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
Q7_DIR = ROOT / "outputs" / "analysis" / "qwen2.5_7b_instruct_eval_v2"
Q05_DIR = ROOT / "outputs" / "analysis" / "qwen2.5_0.5b_instruct_eval_v2"
OUTPUT_PATH = ROOT / "paper" / "figures" / "study_overview_main.png"

NAVY = "#17324D"
MUTED = "#5C6C7B"
BORDER = "#D7E0EA"
BLUE = "#4C78A8"
RED = "#D64F4F"
TEAL = "#1B7F79"
GOLD = "#E5A93C"
PURPLE = "#6B6FB0"
PALE_BLUE = "#EEF4FB"
PALE_TEAL = "#EEF9F7"
PALE_RED = "#FFF1F1"
PALE_GOLD = "#FFF7E8"
PALE_PURPLE = "#F3F2FC"


def _save_release_png(fig: plt.Figure, output_path: Path) -> Path:
    """Save the overview figure as an RGB PNG for reliable downstream paper builds."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    with Image.open(output_path) as image:
        if image.mode != "RGB":
            image.convert("RGB").save(output_path)
    return output_path


def _card(ax, title: str, lines: list[str], *, fc: str, ec: str) -> None:
    ax.set_axis_off()
    patch = FancyBboxPatch(
        (0.01, 0.05),
        0.98,
        0.90,
        boxstyle="round,pad=0.016,rounding_size=0.05",
        linewidth=1.5,
        facecolor=fc,
        edgecolor=ec,
        transform=ax.transAxes,
    )
    ax.add_patch(patch)
    ax.text(0.05, 0.77, title, transform=ax.transAxes, fontsize=13, fontweight="bold", color=NAVY, va="top")
    ax.text(
        0.05,
        0.60,
        "\n".join(lines),
        transform=ax.transAxes,
        fontsize=11.1,
        color=NAVY,
        va="top",
        linespacing=1.35,
    )


def _mini_badge(ax, xy, width, text, *, fc, ec, color=NAVY) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        0.11,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        facecolor=fc,
        edgecolor=ec,
        transform=ax.transAxes,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + 0.055,
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10.2,
        fontweight="bold",
        color=color,
    )


def _arrow(ax, start, end, color="#5B6E82") -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.8,
            color=color,
            transform=ax.transAxes,
        )
    )


def _fmt_pp(value: float, low: float, high: float) -> str:
    return f"{value:+.2f} pp [{low:+.2f}, {high:+.2f}]"


def _load_values() -> dict[str, object]:
    q7_summary = pd.read_csv(Q7_DIR / "condition_summary.csv").set_index("condition")
    q05_summary = pd.read_csv(Q05_DIR / "condition_summary.csv").set_index("condition")
    q7_direct = pd.read_csv(Q7_DIR / "main_text_direct_contrasts.csv").set_index("contrast_label")
    q05_direct = pd.read_csv(Q05_DIR / "main_text_direct_contrasts.csv").set_index("contrast_label")

    return {
        "baseline_labels": ["J1 act", "J1 heart", "Explanation", "J1→J2 heart"],
        "baseline_q7": [
            float(q7_summary.loc["christian_pre", "j1_act_shift_rate"]),
            float(q7_summary.loc["christian_pre", "j1_heart_shift_rate"]),
            float(q7_summary.loc["christian_post", "semantic_score_controlled_delta_vs_baseline"]),
            float(q7_summary.loc["christian_post", "j2_heart_revision_rate"]),
        ],
        "baseline_q05": [
            float(q05_summary.loc["christian_pre", "j1_act_shift_rate"]),
            float(q05_summary.loc["christian_pre", "j1_heart_shift_rate"]),
            float(q05_summary.loc["christian_post", "semantic_score_controlled_delta_vs_baseline"]),
            float(q05_summary.loc["christian_post", "j2_heart_revision_rate"]),
        ],
        "direct_rows": [
            {
                "label": "J1 heart\nC-pre - S-pre",
                "q7_est": float(q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_estimate_pp"]) / 100.0,
                "q7_low": float(q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_low_pp"]) / 100.0,
                "q7_high": float(q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_high_pp"]) / 100.0,
                "q05_est": float(q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_estimate_pp"]) / 100.0,
                "q05_low": float(q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_ci_low_pp"]) / 100.0,
                "q05_high": float(q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_ci_high_pp"]) / 100.0,
            },
            {
                "label": "Controlled explanation\nC-post - S-post",
                "q7_est": float(q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_estimate_pp"]) / 100.0,
                "q7_low": float(q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_low_pp"]) / 100.0,
                "q7_high": float(q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_high_pp"]) / 100.0,
                "q05_est": float(q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_estimate_pp"]) / 100.0,
                "q05_low": float(q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_ci_low_pp"]) / 100.0,
                "q05_high": float(q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_ci_high_pp"]) / 100.0,
            },
        ],
        "q7_heart_direct_text": _fmt_pp(
            q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_estimate_pp"],
            q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_low_pp"],
            q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_high_pp"],
        ),
        "q7_controlled_direct_text": _fmt_pp(
            q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_estimate_pp"],
            q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_low_pp"],
            q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_high_pp"],
        ),
    }


def build_study_overview_figure(output_path: Path = OUTPUT_PATH) -> Path:
    values = _load_values()

    plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "axes.labelsize": 11})
    fig = plt.figure(figsize=(15.8, 8.9), facecolor="white")
    gs = fig.add_gridspec(
        3,
        12,
        height_ratios=[0.95, 1.0, 1.25],
        left=0.045,
        right=0.985,
        top=0.89,
        bottom=0.11,
        hspace=0.34,
        wspace=0.26,
    )

    fig.text(
        0.05,
        0.955,
        "Judgment before justification: a cleaner view of what the study tests",
        ha="left",
        va="top",
        fontsize=23,
        fontweight="bold",
        color=NAVY,
    )
    fig.text(
        0.05,
        0.918,
        "The release uses a staged Moral Stories design, a matched secular control, and two Qwen sizes to separate first-pass judgment from post-hoc explanation.",
        ha="left",
        va="top",
        fontsize=12.5,
        color=MUTED,
    )

    _card(
        fig.add_subplot(gs[0, 0:4]),
        "Benchmark",
        [
            "150-item candidate pool",
            "Locked 30 dev / 120 eval",
            "40-item judgment-only sanity subset",
            "Everyday Moral Stories-derived A/B items",
        ],
        fc=PALE_GOLD,
        ec=GOLD,
    )
    _card(
        fig.add_subplot(gs[0, 4:8]),
        "Matched framing design",
        [
            "Christian heart-focused frame",
            "vs secular motive-focused control",
            "Frame can appear before J1 or after J1",
            "Baseline remains unframed",
        ],
        fc=PALE_BLUE,
        ec=BLUE,
    )
    _card(
        fig.add_subplot(gs[0, 8:12]),
        "Models and decoding",
        [
            "qwen2.5:7b-instruct",
            "qwen2.5:0.5b-instruct",
            "Deterministic decoding",
            "Temperature 0.0, seed 42",
        ],
        fc=PALE_PURPLE,
        ec=PURPLE,
    )

    protocol_ax = fig.add_subplot(gs[1, 0:8])
    protocol_ax.set_axis_off()
    protocol_ax.text(0.0, 1.05, "Stage-separated protocol", transform=protocol_ax.transAxes, fontsize=15, fontweight="bold", color=NAVY)
    protocol_ax.text(0.0, 0.93, "The frame enters either before J1 or in the gap between J1 and explanation.", transform=protocol_ax.transAxes, fontsize=10.4, color=MUTED)

    stage_specs = [
        (0.02, 0.18, 0.25, 0.58, PALE_BLUE, BLUE, "J1", "First-pass judgment", "Two forced A/B judgments"),
        (0.37, 0.18, 0.25, 0.58, PALE_TEAL, TEAL, "E", "Explanation", "Focus label plus one sentence"),
        (0.72, 0.18, 0.25, 0.58, PALE_RED, RED, "J2", "Re-judgment", "Act and heart after explanation"),
    ]
    for x, y, w, h, fc, ec, stage, title, body in stage_specs:
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.015,rounding_size=0.04",
            linewidth=1.6,
            facecolor=fc,
            edgecolor=ec,
            transform=protocol_ax.transAxes,
        )
        protocol_ax.add_patch(patch)
        protocol_ax.text(x + 0.035, y + h - 0.09, stage, transform=protocol_ax.transAxes, fontsize=11.4, fontweight="bold", color=NAVY, va="top")
        protocol_ax.text(x + 0.035, y + h - 0.26, title, transform=protocol_ax.transAxes, fontsize=11.5, fontweight="bold", color=NAVY, va="top")
        protocol_ax.text(x + 0.035, y + 0.14, body, transform=protocol_ax.transAxes, fontsize=9.6, color=NAVY, va="bottom")
    _arrow(protocol_ax, (0.27, 0.47), (0.37, 0.47))
    _arrow(protocol_ax, (0.62, 0.47), (0.72, 0.47))
    _mini_badge(protocol_ax, (0.255, 0.80), 0.17, "Pre conditions insert the frame here", fc="#F7FAFE", ec=BORDER)
    _mini_badge(protocol_ax, (0.605, 0.80), 0.19, "Post conditions insert the frame here", fc="#FFF9F2", ec=BORDER)

    logic_ax = fig.add_subplot(gs[1, 8:12])
    logic_ax.set_axis_off()
    logic_ax.text(0.0, 1.05, "Why the design is identifiable", transform=logic_ax.transAxes, fontsize=15, fontweight="bold", color=NAVY)
    logic_cards = [
        (0.02, 0.67, "J1 isolates exposed judgment", "The first judgment is collected before any explanation is requested."),
        (0.02, 0.36, "Matched control calibrates the claim", "Christian effects are tested against a secular motive-focused frame, not just baseline."),
        (0.02, 0.05, "J2 checks downstream revision pressure", "If explanation changes but J2 stays stable, the effect is not a broad judgment rewrite."),
    ]
    for x, y, title, body in logic_cards:
        patch = FancyBboxPatch(
            (x, y),
            0.96,
            0.23,
            boxstyle="round,pad=0.015,rounding_size=0.04",
            linewidth=1.2,
            facecolor="#FAFBFD",
            edgecolor=BORDER,
            transform=logic_ax.transAxes,
        )
        logic_ax.add_patch(patch)
        logic_ax.text(x + 0.04, y + 0.16, title, transform=logic_ax.transAxes, fontsize=11.4, fontweight="bold", color=NAVY, va="top")
        logic_ax.text(x + 0.04, y + 0.08, body, transform=logic_ax.transAxes, fontsize=9.6, color=MUTED, va="top", linespacing=1.20)

    bar_ax = fig.add_subplot(gs[2, 0:6])
    categories = values["baseline_labels"]
    x = np.arange(len(categories))
    width = 0.34
    q7_vals = np.array(values["baseline_q7"], dtype=float)
    q05_vals = np.array(values["baseline_q05"], dtype=float)
    bar_ax.bar(x - width / 2, q7_vals, width=width, color=BLUE, alpha=0.96, label="Qwen 2.5 7B")
    bar_ax.bar(x + width / 2, q05_vals, width=width, color=BLUE, alpha=0.35, label="Qwen 2.5 0.5B")
    for xi, q7, q05 in zip(x, q7_vals, q05_vals, strict=True):
        bar_ax.text(xi - width / 2, q7 + 0.003, f"{q7 * 100:.1f}%", ha="center", va="bottom", fontsize=9.4, color=NAVY)
        bar_ax.text(xi + width / 2, q05 + 0.003, f"{q05 * 100:.1f}%", ha="center", va="bottom", fontsize=9.4, color=MUTED)
    bar_ax.set_title("Relative to baseline, explanation moves more than act-level judgment", loc="left", fontsize=11.8, fontweight="bold", color=NAVY)
    bar_ax.set_xticks(x)
    bar_ax.set_xticklabels(categories)
    bar_ax.set_ylim(0, 0.115)
    bar_ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    bar_ax.set_ylabel("Items moved vs baseline")
    bar_ax.grid(axis="y", color="#D8DDE5", linewidth=0.8)
    bar_ax.set_axisbelow(True)
    bar_ax.spines["top"].set_visible(False)
    bar_ax.spines["right"].set_visible(False)
    bar_ax.spines["left"].set_color("#CAD2DC")
    bar_ax.spines["bottom"].set_color("#CAD2DC")
    bar_ax.legend(frameon=False, ncol=2, loc="upper left")

    forest_ax = fig.add_subplot(gs[2, 6:12])
    rows = values["direct_rows"]
    ypos = np.arange(len(rows))[::-1]
    forest_ax.axvline(0, color="#808080", linewidth=1.0)
    for y, row in zip(ypos, rows, strict=True):
        forest_ax.plot([row["q7_low"], row["q7_high"]], [y + 0.10, y + 0.10], color=RED, linewidth=2.2)
        forest_ax.scatter(row["q7_est"], y + 0.10, color=RED, edgecolor="#4F2525", linewidth=0.8, s=76, zorder=3)
        forest_ax.plot([row["q05_low"], row["q05_high"]], [y - 0.10, y - 0.10], color=TEAL, linewidth=2.2)
        forest_ax.scatter(row["q05_est"], y - 0.10, color=TEAL, edgecolor="#175954", linewidth=0.8, s=76, zorder=3)
    forest_ax.set_yticks(ypos)
    forest_ax.set_yticklabels([row["label"] for row in rows])
    forest_ax.set_title("What survives matched control is much more modest", loc="left", fontsize=11.8, fontweight="bold", color=NAVY)
    forest_ax.set_xlim(-0.15, 0.08)
    forest_ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    forest_ax.set_xlabel("Christian minus matched secular control")
    forest_ax.grid(axis="x", color="#D8DDE5", linewidth=0.8)
    forest_ax.set_axisbelow(True)
    forest_ax.spines["top"].set_visible(False)
    forest_ax.spines["right"].set_visible(False)
    forest_ax.spines["left"].set_color("#CAD2DC")
    forest_ax.spines["bottom"].set_color("#CAD2DC")
    forest_ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color=RED, lw=2.0, markersize=7, label="Qwen 2.5 7B"),
            Line2D([0], [0], marker="o", color=TEAL, lw=2.0, markersize=7, label="Qwen 2.5 0.5B"),
        ],
        frameon=False,
        loc="lower right",
    )
    fig.text(
        0.5,
        0.04,
        "Main supported claim: stage dissociation. Explanation moves more than first-pass judgment relative to baseline, but the uniquely Christian-specific residual is modest or unstable under matched control.",
        ha="center",
        va="center",
        fontsize=12.4,
        fontweight="bold",
        color=NAVY,
        bbox={"boxstyle": "round,pad=0.55", "facecolor": "#F5F8FC", "edgecolor": BORDER, "linewidth": 1.2},
    )

    _save_release_png(fig, output_path)
    plt.close(fig)
    return output_path


def main() -> None:
    out = build_study_overview_figure()
    print(out)


if __name__ == "__main__":
    main()
