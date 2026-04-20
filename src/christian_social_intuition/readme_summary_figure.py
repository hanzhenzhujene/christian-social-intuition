from __future__ import annotations

"""Generate the README summary figure from the released analysis bundles."""

from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
from PIL import Image


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


def _save_release_png(fig: plt.Figure, output_path: Path) -> Path:
    """Save the README figure as an RGB PNG that compiles reliably in LaTeX."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".tmp.png")
    fig.savefig(tmp_path, dpi=300, bbox_inches="tight", facecolor="white")
    with Image.open(tmp_path) as image:
        image.convert("RGB").save(output_path, format="PNG")
    tmp_path.unlink(missing_ok=True)
    return output_path


def build_readme_results_summary(output_path: Path = OUTPUT_PATH) -> Path:
    q7_summary, q05_summary, q7_direct, q05_direct = _load_tables()

    colors = {
        "act": "#4C78A8",
        "heart": "#D64F4F",
        "explanation": "#1B7F79",
        "revision": "#6F6F6F",
        "q7": "#8C1D40",
        "q05": "#2A7F7A",
        "title": "#16324F",
        "muted": "#4E4E4E",
        "grid": "#D9DDE3",
    }
    plt.rcParams.update({"font.size": 10.5, "axes.titlesize": 11.5, "axes.labelsize": 10.5, "figure.titlesize": 17})

    fig = plt.figure(figsize=(14.2, 7.9), facecolor="white")
    gs = fig.add_gridspec(
        2,
        3,
        height_ratios=[1.0, 0.22],
        width_ratios=[1.06, 1.0, 0.9],
        left=0.055,
        right=0.982,
        top=0.85,
        bottom=0.075,
        hspace=0.16,
        wspace=0.30,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[0, 2])
    ax_footer = fig.add_subplot(gs[1, :])

    fig.text(
        0.05,
        0.965,
        "From prompt movement to calibrated evidence",
        ha="left",
        va="top",
        fontsize=17.2,
        fontweight="bold",
        color=colors["title"],
    )
    fig.text(
        0.05,
        0.925,
        "The staged benchmark lets us compare baseline movement, matched-control residuals, and scale attenuation in one place.",
        ha="left",
        va="top",
        fontsize=10.7,
        color=colors["muted"],
    )

    categories = ["J1 act", "J1 heart", "Controlled\nexplanation", "J1→J2 heart"]
    q7_vals = np.array(
        [
            q7_summary.loc["christian_pre", "j1_act_shift_rate"],
            q7_summary.loc["christian_pre", "j1_heart_shift_rate"],
            q7_summary.loc["christian_post", "semantic_score_controlled_delta_vs_baseline"],
            q7_summary.loc["christian_post", "j2_heart_revision_rate"],
        ]
    )
    q05_vals = np.array(
        [
            q05_summary.loc["christian_pre", "j1_act_shift_rate"],
            q05_summary.loc["christian_pre", "j1_heart_shift_rate"],
            q05_summary.loc["christian_post", "semantic_score_controlled_delta_vs_baseline"],
            q05_summary.loc["christian_post", "j2_heart_revision_rate"],
        ]
    )
    category_colors = [colors["act"], colors["heart"], colors["explanation"], colors["revision"]]
    y = np.arange(len(categories))[::-1]
    for yi, label, q7, q05, category_color in zip(y, categories, q7_vals, q05_vals, category_colors, strict=True):
        ax_a.plot([min(q7, q05), max(q7, q05)], [yi, yi], color="#D0D7E0", linewidth=2.1, zorder=1)
        ax_a.scatter(q7, yi, color=category_color, s=82, zorder=3, edgecolor="#304050", linewidth=0.8)
        ax_a.scatter(q05, yi, color=category_color, s=82, zorder=3, edgecolor="#304050", linewidth=0.8, alpha=0.35)
        ax_a.text(q7 + 0.003, yi + 0.10, f"{q7 * 100:.1f}%", ha="left", va="center", fontsize=9.1, color=colors["title"])
        ax_a.text(q05 + 0.003, yi - 0.10, f"{q05 * 100:.1f}%", ha="left", va="center", fontsize=9.1, color=colors["muted"])
    ax_a.set_title(
        "A. Relative to baseline,\nexplanation movement is largest",
        loc="left",
        color=colors["title"],
        fontweight="bold",
        fontsize=11.2,
        pad=12,
    )
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(categories)
    ax_a.set_xlim(0, 0.115)
    ax_a.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax_a.set_xlabel("Items moved vs baseline")
    ax_a.grid(axis="x", color=colors["grid"], linewidth=0.8)
    ax_a.set_axisbelow(True)
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)
    ax_a.spines["left"].set_color("#C7CED7")
    ax_a.spines["bottom"].set_color("#C7CED7")
    ax_a.legend(
        handles=[
            Line2D([0], [0], marker="o", color="#444444", lw=0, alpha=0.96, label="Qwen 7B", markersize=7),
            Line2D([0], [0], marker="o", color="#777777", lw=0, alpha=0.35, label="Qwen 0.5B", markersize=7),
        ],
        frameon=False,
        loc="lower right",
        ncol=2,
        fontsize=9.3,
    )

    contrast_order = [
        ("J1 heart shift", "C-pre - S-pre on J1 heart shift"),
        ("J1 act shift", "C-pre - S-pre on J1 act shift"),
        ("Controlled explanation", "C-post - S-post on controlled semantic score"),
        ("J1→J2 heart revision", "C-post - S-post on J1→J2 heart revision"),
    ]
    y_positions = np.arange(len(contrast_order))[::-1]
    ax_b.axvline(0, color="#7A7A7A", linewidth=1.0)
    for y, (_, label) in zip(y_positions, contrast_order, strict=True):
        est_7b = float(q7_direct.loc[label, "qwen_7b_estimate_pp"]) / 100.0
        lo_7b = float(q7_direct.loc[label, "qwen_7b_ci_low_pp"]) / 100.0
        hi_7b = float(q7_direct.loc[label, "qwen_7b_ci_high_pp"]) / 100.0
        est_05b = float(q05_direct.loc[label, "qwen_05b_estimate_pp"]) / 100.0
        lo_05b = float(q05_direct.loc[label, "qwen_05b_ci_low_pp"]) / 100.0
        hi_05b = float(q05_direct.loc[label, "qwen_05b_ci_high_pp"]) / 100.0
        ax_b.plot([lo_7b, hi_7b], [y + 0.12, y + 0.12], color=colors["q7"], lw=2.2)
        ax_b.scatter(est_7b, y + 0.12, color=colors["q7"], s=60, zorder=3, edgecolor="#4A1F30", linewidth=0.8)
        ax_b.plot([lo_05b, hi_05b], [y - 0.12, y - 0.12], color=colors["q05"], lw=2.2)
        ax_b.scatter(est_05b, y - 0.12, color=colors["q05"], s=60, zorder=3, edgecolor="#19504C", linewidth=0.8)
    ax_b.set_title(
        "B. Matched control shrinks\nthe Christian-specific residual",
        loc="left",
        color=colors["title"],
        fontweight="bold",
        fontsize=11.2,
        pad=12,
    )
    ax_b.set_yticks(y_positions)
    ax_b.set_yticklabels([name for name, _ in contrast_order])
    ax_b.set_xlim(-0.16, 0.08)
    ax_b.xaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax_b.set_xlabel("Christian minus matched secular control")
    ax_b.grid(axis="x", color=colors["grid"], linewidth=0.8)
    ax_b.set_axisbelow(True)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)
    ax_b.spines["left"].set_color("#C7CED7")
    ax_b.spines["bottom"].set_color("#C7CED7")

    slope_specs = [
        (
            "J1 heart residual",
            float(q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_estimate_pp"]) / 100.0,
            float(q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_low_pp"]) / 100.0,
            float(q7_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_7b_ci_high_pp"]) / 100.0,
            float(q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_estimate_pp"]) / 100.0,
            float(q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_ci_low_pp"]) / 100.0,
            float(q05_direct.loc["C-pre - S-pre on J1 heart shift", "qwen_05b_ci_high_pp"]) / 100.0,
            "#D07A1F",
        ),
        (
            "Controlled explanation\nresidual",
            float(q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_estimate_pp"]) / 100.0,
            float(q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_low_pp"]) / 100.0,
            float(q7_direct.loc["C-post - S-post on controlled semantic score", "qwen_7b_ci_high_pp"]) / 100.0,
            float(q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_estimate_pp"]) / 100.0,
            float(q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_ci_low_pp"]) / 100.0,
            float(q05_direct.loc["C-post - S-post on controlled semantic score", "qwen_05b_ci_high_pp"]) / 100.0,
            colors["explanation"],
        ),
    ]
    ax_c.axhline(0, color="#7A7A7A", linewidth=1.0)
    x_c = np.array([0, 1])
    for label, q7_est, q7_low, q7_high, q05_est, q05_low, q05_high, color in slope_specs:
        vals = np.array([q7_est, q05_est])
        ax_c.plot(x_c, vals, color=color, linewidth=2.4)
        ax_c.errorbar(
            x_c,
            vals,
            yerr=np.array([[max(q7_est - q7_low, 0), max(q05_est - q05_low, 0)], [max(q7_high - q7_est, 0), max(q05_high - q05_est, 0)]]),
            fmt="o",
            color=color,
            ecolor=color,
            markeredgecolor="#303030",
            markeredgewidth=0.8,
            markersize=8,
            capsize=3,
            linewidth=1.5,
        )
        ax_c.text(1.04, q05_est, label, color=color, va="center", fontsize=9.2, linespacing=1.05, clip_on=False)
    ax_c.set_title(
        "C. Same-family scale comparison\nshows attenuation",
        loc="left",
        color=colors["title"],
        fontweight="bold",
        fontsize=11.2,
        pad=12,
    )
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(["7B", "0.5B"])
    ax_c.set_ylim(-0.15, 0.08)
    ax_c.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax_c.set_xlabel("Model size")
    ax_c.grid(axis="y", color=colors["grid"], linewidth=0.8)
    ax_c.set_axisbelow(True)
    ax_c.spines["top"].set_visible(False)
    ax_c.spines["right"].set_visible(False)
    ax_c.spines["left"].set_color("#C7CED7")
    ax_c.spines["bottom"].set_color("#C7CED7")

    ax_footer.axis("off")
    ax_footer.plot([0.0, 1.0], [0.88, 0.88], transform=ax_footer.transAxes, color="#D5DEE8", linewidth=1.0)
    ax_footer.text(0.0, 0.46, "Takeaway", fontsize=11.0, fontweight="bold", color=colors["title"], va="center", ha="left", transform=ax_footer.transAxes)
    ax_footer.text(
        0.115,
        0.46,
        textwrap.fill(
            "The strongest supported insight is stage dissociation: explanation moves readily relative to baseline, while the Christian-specific residual becomes modest, unstable, or null under matched control.",
            width=122,
        ),
        fontsize=10.2,
        color=colors["muted"],
        va="center",
        ha="left",
        linespacing=1.28,
        transform=ax_footer.transAxes,
    )

    _save_release_png(fig, output_path)
    plt.close(fig)
    return output_path


def main() -> None:
    out = build_readme_results_summary()
    print(out)


if __name__ == "__main__":
    main()
