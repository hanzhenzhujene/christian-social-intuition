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
        (0.02, 0.08),
        0.96,
        0.84,
        boxstyle="round,pad=0.016,rounding_size=0.05",
        linewidth=1.1,
        facecolor=fc,
        edgecolor=ec,
        transform=ax.transAxes,
    )
    ax.add_patch(patch)
    ax.text(0.07, 0.76, title, transform=ax.transAxes, fontsize=12.4, fontweight="bold", color=NAVY, va="top")
    ax.text(
        0.07,
        0.56,
        "\n".join(lines),
        transform=ax.transAxes,
        fontsize=10.5,
        color=NAVY,
        va="top",
        linespacing=1.48,
    )


def _soft_box(ax, xy, width, height, title, body, *, fc, ec, dashed=False) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2,
        facecolor=fc,
        edgecolor=ec,
        transform=ax.transAxes,
        linestyle=(0, (3, 2)) if dashed else "solid",
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height * 0.62,
        title,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=9.4,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        xy[0] + width / 2,
        xy[1] + height * 0.28,
        body,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=8.1,
        color=MUTED,
        linespacing=1.2,
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
    fig = plt.figure(figsize=(16.4, 9.8), facecolor="white")
    gs = fig.add_gridspec(
        4,
        12,
        height_ratios=[0.88, 1.04, 1.26, 0.18],
        left=0.045,
        right=0.985,
        top=0.90,
        bottom=0.08,
        hspace=0.46,
        wspace=0.34,
    )

    fig.text(
        0.05,
        0.955,
        "What the staged study actually separates",
        ha="left",
        va="top",
        fontsize=22,
        fontweight="bold",
        color=NAVY,
    )
    fig.text(
        0.05,
        0.918,
        "Moral Stories items, matched Christian versus secular framing, and two Qwen sizes are used to separate first-pass exposed judgment from post-hoc explanation.",
        ha="left",
        va="top",
        fontsize=11.6,
        color=MUTED,
    )
    _card(
        fig.add_subplot(gs[0, 0:4]),
        "Data",
        [
            "• 120 locked eval items + 40 sanity items",
            "• Everyday Moral Stories-derived A/B scenarios",
            "• Manually reviewed and split before analysis",
        ],
        fc=PALE_GOLD,
        ec=GOLD,
    )
    _card(
        fig.add_subplot(gs[0, 4:8]),
        "Frames",
        [
            "• Christian heart-focused frame",
            "• Matched secular motive-focused control",
            "• Frame inserted either before J1 or after J1",
        ],
        fc=PALE_BLUE,
        ec=BLUE,
    )
    _card(
        fig.add_subplot(gs[0, 8:12]),
        "Models",
        [
            "• Qwen 2.5 7B and Qwen 2.5 0.5B",
            "• Deterministic decoding in the released runs",
            "• Temperature 0.0, seed 42",
        ],
        fc=PALE_PURPLE,
        ec=PURPLE,
    )

    protocol_ax = fig.add_subplot(gs[1, 0:8])
    protocol_ax.set_axis_off()
    protocol_ax.text(0.0, 1.02, "Where prompting can act", transform=protocol_ax.transAxes, fontsize=14.2, fontweight="bold", color=NAVY)
    protocol_ax.text(
        0.0,
        0.90,
        "Christian or secular text occupies one optional frame slot per condition, which makes timing interpretable.",
        transform=protocol_ax.transAxes,
        fontsize=10.0,
        color=MUTED,
    )

    _soft_box(
        protocol_ax,
        (0.01, 0.33),
        0.12,
        0.22,
        "Pre frame",
        "*_pre only",
        fc="#FBFCFE",
        ec="#C8D4E2",
        dashed=True,
    )
    _soft_box(
        protocol_ax,
        (0.39, 0.33),
        0.12,
        0.22,
        "Post frame",
        "*_post only",
        fc="#FBFCFE",
        ec="#C8D4E2",
        dashed=True,
    )

    stage_specs = [
        (0.17, 0.22, 0.19, 0.50, PALE_BLUE, BLUE, "J1", "First-pass judgment", "Forced A/B choice\nfor act and heart"),
        (0.55, 0.22, 0.19, 0.50, PALE_TEAL, TEAL, "E", "Post-hoc explanation", "One focus label\nplus one sentence"),
        (0.77, 0.22, 0.18, 0.50, PALE_RED, RED, "J2", "Re-judgment", "Same act and heart\nchoice after E"),
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
        protocol_ax.text(x + 0.03, y + h - 0.08, stage, transform=protocol_ax.transAxes, fontsize=10.8, fontweight="bold", color=NAVY, va="top")
        protocol_ax.text(x + 0.03, y + h - 0.20, title, transform=protocol_ax.transAxes, fontsize=11.3, fontweight="bold", color=NAVY, va="top")
        protocol_ax.text(x + 0.03, y + 0.10, body, transform=protocol_ax.transAxes, fontsize=9.2, color=NAVY, va="bottom", linespacing=1.2)
    _arrow(protocol_ax, (0.14, 0.47), (0.17, 0.47))
    _arrow(protocol_ax, (0.36, 0.47), (0.39, 0.47))
    _arrow(protocol_ax, (0.52, 0.47), (0.55, 0.47))
    _arrow(protocol_ax, (0.74, 0.47), (0.77, 0.47))

    logic_ax = fig.add_subplot(gs[1, 8:12])
    logic_ax.set_axis_off()
    logic_ax.text(0.0, 1.02, "How to interpret the stages", transform=logic_ax.transAxes, fontsize=14.2, fontweight="bold", color=NAVY)
    logic_patch = FancyBboxPatch(
        (0.02, 0.15),
        0.96,
        0.67,
        boxstyle="round,pad=0.018,rounding_size=0.04",
        linewidth=1.1,
        facecolor="#FAFBFD",
        edgecolor=BORDER,
        transform=logic_ax.transAxes,
    )
    logic_ax.add_patch(logic_patch)
    logic_ax.text(0.07, 0.77, "• J1 is the exposed first-pass judgment measure.", transform=logic_ax.transAxes, fontsize=10.7, color=NAVY, va="top")
    logic_ax.text(
        0.07,
        0.58,
        "• The matched secular motive-focused control tests whether\nChristian wording adds anything beyond generic motive salience.",
        transform=logic_ax.transAxes,
        fontsize=10.0,
        color=NAVY,
        va="top",
        linespacing=1.25,
    )
    logic_ax.text(
        0.07,
        0.34,
        "• J2 is a revision check: if explanation moves while J2 stays\nstable, the effect is mostly at the explanation layer.",
        transform=logic_ax.transAxes,
        fontsize=10.0,
        color=NAVY,
        va="top",
        linespacing=1.25,
    )
    logic_ax.text(0.07, 0.08, "Sanity: baseline and judgment-only agree 1.0 / 1.0 in both models.", transform=logic_ax.transAxes, fontsize=9.3, color=MUTED, va="bottom")

    baseline_ax = fig.add_subplot(gs[2, 0:6])
    categories = values["baseline_labels"]
    q7_vals = np.array(values["baseline_q7"], dtype=float)
    q05_vals = np.array(values["baseline_q05"], dtype=float)
    y = np.arange(len(categories))[::-1]
    baseline_ax.set_title("A. Baseline-relative movement", loc="left", fontsize=11.8, fontweight="bold", color=NAVY)
    for yi, q7, q05 in zip(y, q7_vals, q05_vals, strict=True):
        baseline_ax.plot([min(q7, q05), max(q7, q05)], [yi, yi], color="#D4DDE8", linewidth=2.2, zorder=1)
        baseline_ax.scatter(q7, yi, color=BLUE, s=84, zorder=3, edgecolor="#2E5E8E", linewidth=0.8)
        baseline_ax.scatter(q05, yi, color="#B8C7D9", s=84, zorder=3, edgecolor="#94A7BD", linewidth=0.8)
        baseline_ax.text(q7 + 0.003, yi + 0.11, f"{q7 * 100:.1f}%", fontsize=9.0, color=NAVY, va="center")
        baseline_ax.text(q05 + 0.003, yi - 0.11, f"{q05 * 100:.1f}%", fontsize=9.0, color=MUTED, va="center")
    baseline_ax.set_yticks(y)
    baseline_ax.set_yticklabels(categories)
    baseline_ax.set_xlim(0, 0.118)
    baseline_ax.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    baseline_ax.set_xlabel("Items moved relative to baseline")
    baseline_ax.grid(axis="x", color="#D8DDE5", linewidth=0.8)
    baseline_ax.set_axisbelow(True)
    baseline_ax.spines["top"].set_visible(False)
    baseline_ax.spines["right"].set_visible(False)
    baseline_ax.spines["left"].set_color("#CAD2DC")
    baseline_ax.spines["bottom"].set_color("#CAD2DC")
    baseline_ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color=BLUE, lw=0, markersize=8, label="Qwen 2.5 7B"),
            Line2D([0], [0], marker="o", color="#B8C7D9", lw=0, markersize=8, label="Qwen 2.5 0.5B"),
        ],
        frameon=False,
        ncol=2,
        loc="upper center",
    )

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
    forest_ax.set_yticklabels(["Heart residual", "Explanation residual"])
    forest_ax.set_title("B. Matched-control residuals", loc="left", fontsize=11.8, fontweight="bold", color=NAVY)
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
        loc="upper right",
    )
    footer_ax = fig.add_subplot(gs[3, 0:12])
    footer_ax.set_axis_off()
    footer_ax.plot([0.0, 1.0], [0.88, 0.88], transform=footer_ax.transAxes, color=BORDER, linewidth=1.0)
    footer_ax.text(0.0, 0.32, "Takeaway", transform=footer_ax.transAxes, fontsize=11.4, fontweight="bold", color=NAVY, va="center")
    footer_ax.text(
        0.105,
        0.32,
        "The main supported pattern is stage dissociation: explanation moves more readily than first-pass judgment, while Christian-specific residuals become modest or unstable and J1→J2 revision stays rare.",
        transform=footer_ax.transAxes,
        fontsize=10.7,
        color=MUTED,
        va="center",
    )

    _save_release_png(fig, output_path)
    plt.close(fig)
    return output_path


def main() -> None:
    out = build_study_overview_figure()
    print(out)


if __name__ == "__main__":
    main()
