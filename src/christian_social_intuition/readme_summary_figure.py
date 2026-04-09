from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter


ROOT = Path(__file__).resolve().parents[2]
Q7_DIR = ROOT / "outputs" / "analysis" / "qwen2.5_7b_instruct_eval_v2"
Q05_DIR = ROOT / "outputs" / "analysis" / "qwen2.5_0.5b_instruct_eval_v2"
OUTPUT_PATH = ROOT / "paper" / "figures" / "readme_results_summary.png"


def _load_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    q7_summary = pd.read_csv(Q7_DIR / "condition_summary.csv").set_index("condition")
    q05_summary = pd.read_csv(Q05_DIR / "condition_summary.csv").set_index("condition")
    q7_direct = pd.read_csv(Q7_DIR / "main_text_direct_contrasts.csv").set_index("contrast_label")
    q05_direct = pd.read_csv(Q05_DIR / "main_text_direct_contrasts.csv").set_index("contrast_label")
    return q7_summary, q05_summary, q7_direct, q05_direct


def build_readme_results_summary(output_path: Path = OUTPUT_PATH) -> Path:
    q7_summary, q05_summary, q7_direct, q05_direct = _load_tables()

    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "figure.titlesize": 17,
        }
    )

    colors = {
        "act": "#4C78A8",
        "heart": "#D64F4F",
        "explanation": "#1B7F79",
        "revision": "#6F6F6F",
        "q7": "#8C1D40",
        "q05": "#3B6EA8",
        "title": "#16324F",
        "muted": "#4E4E4E",
    }

    fig = plt.figure(figsize=(14.4, 7.1), facecolor="white")
    gs = fig.add_gridspec(
        2,
        2,
        height_ratios=[1.0, 0.28],
        width_ratios=[1.05, 1.0],
        left=0.14,
        right=0.985,
        top=0.82,
        bottom=0.08,
        hspace=0.26,
        wspace=0.28,
    )
    ax_left = fig.add_subplot(gs[0, 0])
    ax_right = fig.add_subplot(gs[0, 1])
    ax_footer = fig.add_subplot(gs[1, :])

    fig.text(
        0.08,
        0.965,
        "Results Summary: explanation is more prompt-sensitive than first-pass judgment",
        ha="left",
        va="top",
        fontsize=17,
        fontweight="bold",
    )
    fig.text(
        0.08,
        0.922,
        "README summary of the completed Qwen runs.",
        ha="left",
        va="top",
        fontsize=11.2,
        color=colors["muted"],
    )

    stage_values_7b = [
        q7_summary.loc["christian_pre", "j1_act_shift_rate"],
        q7_summary.loc["christian_pre", "j1_heart_shift_rate"],
        q7_summary.loc["christian_post", "semantic_score_controlled_delta_vs_baseline"],
        q7_summary.loc["christian_post", "j2_heart_revision_rate"],
    ]
    stage_values_05b = [
        q05_summary.loc["christian_pre", "j1_act_shift_rate"],
        q05_summary.loc["christian_pre", "j1_heart_shift_rate"],
        q05_summary.loc["christian_post", "semantic_score_controlled_delta_vs_baseline"],
        q05_summary.loc["christian_post", "j2_heart_revision_rate"],
    ]
    stage_labels = [
        "J1 act shift",
        "J1 heart shift",
        "Explanation shift",
        "J1→J2 heart revision",
    ]
    stage_colors = [colors["act"], colors["heart"], colors["explanation"], colors["revision"]]
    y_positions = [3.2, 2.2, 1.2, 0.2]

    for value_7b, value_05b, y_value, color in zip(stage_values_7b, stage_values_05b, y_positions, stage_colors, strict=True):
        ax_left.barh(y_value + 0.17, value_7b, height=0.28, color=color, alpha=0.96)
        ax_left.barh(y_value - 0.17, value_05b, height=0.28, color=color, alpha=0.45)
        ax_left.text(value_7b + 0.0042, y_value + 0.17, f"{value_7b * 100:.1f}%", va="center", fontsize=10)
        ax_left.text(
            value_05b + 0.0042,
            y_value - 0.17,
            f"{value_05b * 100:.1f}%",
            va="center",
            fontsize=10,
            color="#555555",
        )

    ax_left.set_yticks(y_positions)
    ax_left.set_yticklabels(stage_labels)
    ax_left.tick_params(axis="y", pad=4)
    ax_left.set_xlim(0, 0.11)
    ax_left.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax_left.set_xlabel("Rate")
    ax_left.set_title("A. Christian framing vs baseline by output stage")
    ax_left.grid(axis="x", color="#DDDDDD", linewidth=0.8)
    ax_left.set_axisbelow(True)
    ax_left.legend(
        handles=[
            Line2D([0], [0], color="#444444", lw=8, alpha=0.96, label="Qwen 7B (darker)"),
            Line2D([0], [0], color="#777777", lw=8, alpha=0.45, label="Qwen 0.5B (lighter)"),
        ],
        frameon=False,
        loc="lower right",
    )
    for spine in ["top", "right"]:
        ax_left.spines[spine].set_visible(False)

    contrast_order = [
        "C-pre - S-pre on J1 heart shift",
        "C-pre - S-pre on J1 act shift",
        "C-post - S-post on controlled semantic score",
        "C-post - S-post on J1→J2 heart revision",
    ]
    contrast_labels = [
        "J1 heart shift",
        "J1 act shift",
        "Controlled explanation score",
        "J1→J2 heart revision",
    ]
    y_contrast = list(range(len(contrast_order) - 1, -1, -1))

    for idx, contrast_label in enumerate(contrast_order):
        est_7b = float(q7_direct.loc[contrast_label, "qwen_7b_estimate_pp"]) / 100.0
        lo_7b = float(q7_direct.loc[contrast_label, "qwen_7b_ci_low_pp"]) / 100.0
        hi_7b = float(q7_direct.loc[contrast_label, "qwen_7b_ci_high_pp"]) / 100.0
        est_05b = float(q05_direct.loc[contrast_label, "qwen_05b_estimate_pp"]) / 100.0
        lo_05b = float(q05_direct.loc[contrast_label, "qwen_05b_ci_low_pp"]) / 100.0
        hi_05b = float(q05_direct.loc[contrast_label, "qwen_05b_ci_high_pp"]) / 100.0
        y_value = y_contrast[idx]

        ax_right.plot([lo_7b, hi_7b], [y_value + 0.14, y_value + 0.14], color=colors["q7"], lw=2.2)
        ax_right.scatter(est_7b, y_value + 0.14, color=colors["q7"], s=50, zorder=3)
        ax_right.plot([lo_05b, hi_05b], [y_value - 0.14, y_value - 0.14], color=colors["q05"], lw=2.2)
        ax_right.scatter(est_05b, y_value - 0.14, color=colors["q05"], s=50, zorder=3)

    ax_right.axvline(0, color="#888888", lw=1)
    ax_right.set_yticks(y_contrast)
    ax_right.set_yticklabels(contrast_labels)
    ax_right.tick_params(axis="y", pad=4)
    ax_right.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax_right.set_xlim(-0.16, 0.08)
    ax_right.set_xlabel("Christian minus matched secular control")
    ax_right.set_title("B. Direct Christian-minus-secular contrasts")
    ax_right.grid(axis="x", color="#DDDDDD", linewidth=0.8)
    ax_right.set_axisbelow(True)
    ax_right.legend(
        handles=[
            Line2D([0], [0], marker="o", color=colors["q7"], lw=2.2, label="Qwen 2.5 7B"),
            Line2D([0], [0], marker="o", color=colors["q05"], lw=2.2, label="Qwen 2.5 0.5B"),
        ],
        frameon=False,
        loc="lower right",
    )
    for spine in ["top", "right"]:
        ax_right.spines[spine].set_visible(False)

    ax_footer.axis("off")
    footer_text = (
        "Takeaway: stage dissociation is the clearest supported result.\n"
        "Explanation is prompt-sensitive relative to baseline.\n"
        "Under matched control, the Christian-specific residual is weak and unstable."
    )
    ax_footer.text(
        0.5,
        0.52,
        footer_text,
        fontsize=12.0,
        fontweight="bold",
        color=colors["title"],
        va="center",
        ha="center",
        linespacing=1.35,
        bbox={
            "boxstyle": "round,pad=0.55",
            "facecolor": "#F4F7FB",
            "edgecolor": "#D5DEE8",
            "linewidth": 1.0,
        },
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def main() -> None:
    out = build_readme_results_summary()
    print(out)


if __name__ == "__main__":
    main()
