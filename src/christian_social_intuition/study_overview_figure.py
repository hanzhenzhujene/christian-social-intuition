from __future__ import annotations

"""Build the repository's study-overview figure from the current released artifacts."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
Q7_DIR = ROOT / "outputs" / "analysis" / "qwen2.5_7b_instruct_eval_v2"
Q05_DIR = ROOT / "outputs" / "analysis" / "qwen2.5_0.5b_instruct_eval_v2"
OUTPUT_PATH = ROOT / "paper" / "figures" / "study_overview_main.png"


def _box(ax, xy, width, height, text, *, fc, ec, fontsize=12, weight="normal", color="#17324D", align="center"):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.5,
        facecolor=fc,
        edgecolor=ec,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + (width / 2 if align == "center" else 0.018),
        xy[1] + height / 2,
        text,
        ha=align,
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=color,
        wrap=True,
    )


def _arrow(ax, start, end, color="#5B6E82"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.8,
            color=color,
        )
    )


def _fmt_pp(value: float, low: float, high: float) -> str:
    return f"{value:+.2f} pp [{low:+.2f}, {high:+.2f}]"


def _load_values() -> dict[str, str]:
    q7_summary = pd.read_csv(Q7_DIR / "condition_summary.csv").set_index("condition")
    q05_summary = pd.read_csv(Q05_DIR / "condition_summary.csv").set_index("condition")
    q7_direct = pd.read_csv(Q7_DIR / "main_text_direct_contrasts.csv").set_index("contrast_label")
    q05_direct = pd.read_csv(Q05_DIR / "main_text_direct_contrasts.csv").set_index("contrast_label")

    return {
        "q7_heart_vs_base": f"{q7_summary.loc['christian_pre', 'j1_heart_shift_rate'] * 100:.1f}%",
        "q7_expl_vs_base": f"{q7_summary.loc['christian_post', 'semantic_score_controlled_delta_vs_baseline'] * 100:.1f}%",
        "q7_heart_direct": _fmt_pp(
            q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_estimate_pp"],
            q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_low_pp"],
            q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_high_pp"],
        ),
        "q7_controlled_direct": _fmt_pp(
            q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_estimate_pp"],
            q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_low_pp"],
            q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_high_pp"],
        ),
        "q05_heart_direct": _fmt_pp(
            q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_estimate_pp"],
            q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_ci_low_pp"],
            q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_ci_high_pp"],
        ),
        "q05_controlled_direct": _fmt_pp(
            q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_estimate_pp"],
            q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_ci_low_pp"],
            q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_ci_high_pp"],
        ),
        "q05_expl_vs_base": f"{q05_summary.loc['christian_post', 'semantic_score_controlled_delta_vs_baseline'] * 100:.1f}%",
    }


def build_study_overview_figure(output_path: Path = OUTPUT_PATH) -> Path:
    values = _load_values()

    fig = plt.figure(figsize=(15.5, 8.7), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    navy = "#17324D"
    muted = "#5C6C7B"
    border = "#D7E0EA"
    blue = "#4C78A8"
    red = "#D64F4F"
    teal = "#1B7F79"
    gold = "#F0B94B"
    purple = "#6B6FB0"
    pale_blue = "#EEF4FB"
    pale_teal = "#EEF9F7"
    pale_red = "#FFF1F1"
    pale_gold = "#FFF7E6"
    pale_purple = "#F3F2FC"

    fig.text(
        0.05,
        0.955,
        "Judgment before justification: what the experiment actually tests and supports",
        ha="left",
        va="top",
        fontsize=22,
        fontweight="bold",
        color=navy,
    )
    fig.text(
        0.05,
        0.918,
        "A stage-separated, matched-control study on Moral Stories-derived everyday scenarios using Qwen 2.5 7B and 0.5B.",
        ha="left",
        va="top",
        fontsize=12.5,
        color=muted,
    )

    top_y = 0.69
    top_h = 0.17
    w = 0.27
    xs = [0.05, 0.365, 0.68]

    _box(
        ax,
        (xs[0], top_y),
        w,
        top_h,
        "Benchmark setup\n\n150-item candidate pool\nLocked 30 dev / 120 eval\n40-item judgment-only sanity subset\nEveryday Moral Stories-derived A/B vignettes",
        fc=pale_gold,
        ec=gold,
        fontsize=12.2,
        weight="bold",
    )
    _box(
        ax,
        (xs[1], top_y),
        w,
        top_h,
        "Framing conditions\n\nChristian heart-focused frame\nvs matched secular motive-focused control\nEach can appear either before J1 or after J1",
        fc=pale_blue,
        ec=blue,
        fontsize=12.0,
        weight="bold",
    )
    _box(
        ax,
        (xs[2], top_y),
        w,
        top_h,
        "Models and decoding\n\nqwen2.5:7b-instruct\nqwen2.5:0.5b-instruct\nDeterministic decoding\nTemperature 0.0, seed 42",
        fc=pale_purple,
        ec=purple,
        fontsize=12.0,
        weight="bold",
    )

    fig.text(0.05, 0.63, "Stage-separated protocol", fontsize=15, fontweight="bold", color=navy)
    stage_y = 0.48
    stage_h = 0.11
    stage_w = 0.22
    _box(ax, (0.08, stage_y), stage_w, stage_h, "Stage 1: J1\nFirst-pass exposed judgment\nJSON only: overall_problematic + heart_worse", fc=pale_blue, ec=blue, fontsize=12.0, weight="bold")
    _box(ax, (0.39, stage_y), stage_w, stage_h, "Stage E\nPost-hoc explanation\nFocus label + one sentence tied to J1", fc=pale_teal, ec=teal, fontsize=12.0, weight="bold")
    _box(ax, (0.70, stage_y), stage_w, stage_h, "Stage 2: J2\nRe-judgment after explanation\nSecondary revision check", fc=pale_red, ec=red, fontsize=12.0, weight="bold")
    _arrow(ax, (0.30, stage_y + stage_h / 2), (0.39, stage_y + stage_h / 2))
    _arrow(ax, (0.61, stage_y + stage_h / 2), (0.70, stage_y + stage_h / 2))

    _box(
        ax,
        (0.08, 0.35),
        0.36,
        0.09,
        "What the design identifies\n\nJ1 isolates first-pass exposed judgment before explanation appears.",
        fc="#F9FBFD",
        ec=border,
        fontsize=12.0,
        weight="bold",
    )
    _box(
        ax,
        (0.56, 0.35),
        0.36,
        0.09,
        "Why the matched control matters\n\nChristian-specific effects are tested against a secular motive-focused control, not just baseline.",
        fc="#F9FBFD",
        ec=border,
        fontsize=12.0,
        weight="bold",
    )

    lower_y = 0.145
    lower_h = 0.14
    _box(
        ax,
        (0.05, lower_y),
        0.28,
        lower_h,
        "What is measured\n\nJ1: act shift and heart shift\nE: coarse label, raw score,\ncontrolled semantic score\nJ2: act and heart revision",
        fc=pale_teal,
        ec=teal,
        fontsize=11.2,
        weight="bold",
    )
    _box(
        ax,
        (0.365, lower_y),
        0.27,
        lower_h,
        "Baseline-relative movement\n\n7B: Christian pre changes J1 heart on "
        + values["q7_heart_vs_base"]
        + ".\n7B: Christian post changes controlled explanation score by "
        + values["q7_expl_vs_base"]
        + " vs baseline.\n0.5B: Christian post explanation change is "
        + values["q05_expl_vs_base"]
        + ".",
        fc=pale_blue,
        ec=blue,
        fontsize=10.7,
        weight="bold",
    )
    _box(
        ax,
        (0.67, lower_y),
        0.28,
        lower_h,
        "Calibrated evidence pattern\n\n7B direct J1 heart contrast: "
        + values["q7_heart_direct"]
        + "\n7B controlled explanation contrast: "
        + values["q7_controlled_direct"]
        + "\n0.5B attenuates the story:\n"
        + values["q05_heart_direct"]
        + "\n"
        + values["q05_controlled_direct"],
        fc=pale_red,
        ec=red,
        fontsize=10.0,
        weight="bold",
    )

    footer = FancyBboxPatch(
        (0.05, 0.035),
        0.90,
        0.06,
        boxstyle="round,pad=0.02,rounding_size=0.02",
        linewidth=1.4,
        facecolor="#F4F7FB",
        edgecolor=border,
    )
    ax.add_patch(footer)
    ax.text(
        0.5,
        0.065,
        "Claim boundary: the clearest supported contribution is stage dissociation. Explanation is more prompt-sensitive than first-pass judgment, but the Christian-specific residual is modest or unstable under matched control.",
        ha="center",
        va="center",
        fontsize=12.0,
        fontweight="bold",
        color=navy,
        wrap=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def main() -> None:
    out = build_study_overview_figure()
    print(out)


if __name__ == "__main__":
    main()
