from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = ROOT / "paper" / "figures" / "readme_research_advance.png"


def _box(ax, xy, width, height, text, *, fc, ec, fontsize=12, weight="normal", color="#16324F"):
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
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=color,
        wrap=True,
    )


def _arrow(ax, start, end, color="#6B7B8C"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=16,
            linewidth=1.8,
            color=color,
            connectionstyle="arc3,rad=0.0",
        )
    )


def build_readme_research_advance_figure(output_path: Path = OUTPUT_PATH) -> Path:
    fig = plt.figure(figsize=(15, 8.2), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    navy = "#16324F"
    slate = "#5C6B7A"
    light_slate = "#F4F7FB"
    border = "#D7E0EA"
    accent_blue = "#4C78A8"
    accent_teal = "#1B7F79"
    accent_red = "#D64F4F"
    accent_gold = "#F0B94B"
    light_blue = "#EAF1FB"
    light_teal = "#E8F6F4"
    light_red = "#FDEEEE"
    light_gold = "#FFF6DF"

    fig.text(
        0.055,
        0.955,
        "What this study adds over standard prompt-effect evaluations",
        ha="left",
        va="top",
        fontsize=23,
        fontweight="bold",
        color=navy,
    )
    fig.text(
        0.055,
        0.918,
        "The contribution is not just a new prompt result. It is a cleaner way to identify where prompting exerts influence.",
        ha="left",
        va="top",
        fontsize=12.5,
        color=slate,
    )

    panel_y = 0.28
    panel_h = 0.54
    panel_w = 0.285
    panel_x = [0.055, 0.357, 0.659]

    headers = [
        ("1. What standard prompt papers usually measure", accent_blue, light_blue),
        ("2. What this repository changes", accent_teal, light_teal),
        ("3. What the current evidence supports", accent_red, light_red),
    ]

    for x, (title, edge, face) in zip(panel_x, headers, strict=True):
        panel = FancyBboxPatch(
            (x, panel_y),
            panel_w,
            panel_h,
            boxstyle="round,pad=0.02,rounding_size=0.025",
            linewidth=1.6,
            facecolor="white",
            edgecolor=border,
        )
        ax.add_patch(panel)
        _box(ax, (x + 0.02, panel_y + panel_h - 0.10), panel_w - 0.04, 0.07, title, fc=face, ec=edge, fontsize=12.2, weight="bold")

    # Panel 1: old benchmark ambiguity
    x1 = panel_x[0]
    _box(ax, (x1 + 0.05, 0.60), panel_w - 0.10, 0.08, "Single prompt", fc=light_blue, ec=accent_blue, fontsize=12.5, weight="bold")
    _box(ax, (x1 + 0.05, 0.47), panel_w - 0.10, 0.10, "One bundled output:\njudgment + rationale", fc="#F7FAFE", ec=accent_blue, fontsize=12.3)
    _box(ax, (x1 + 0.05, 0.34), panel_w - 0.10, 0.09, "Observed difference", fc="#F7FAFE", ec=accent_blue, fontsize=12.3)
    _arrow(ax, (x1 + panel_w / 2, 0.60), (x1 + panel_w / 2, 0.57))
    _arrow(ax, (x1 + panel_w / 2, 0.47), (x1 + panel_w / 2, 0.43))
    _box(
        ax,
        (x1 + 0.035, 0.17),
        panel_w - 0.07,
        0.10,
        "Identification problem:\nDid the prompt change first-pass judgment,\nor only the explanation language?",
        fc=light_gold,
        ec=accent_gold,
        fontsize=11.7,
        weight="bold",
    )

    # Panel 2: this repo
    x2 = panel_x[1]
    _box(ax, (x2 + 0.04, 0.62), 0.07, 0.07, "J1", fc=light_teal, ec=accent_teal, fontsize=13, weight="bold")
    _box(ax, (x2 + 0.125, 0.62), 0.07, 0.07, "E", fc=light_teal, ec=accent_teal, fontsize=13, weight="bold")
    _box(ax, (x2 + 0.21, 0.62), 0.07, 0.07, "J2", fc=light_teal, ec=accent_teal, fontsize=13, weight="bold")
    _arrow(ax, (x2 + 0.11, 0.655), (x2 + 0.125, 0.655), color=accent_teal)
    _arrow(ax, (x2 + 0.195, 0.655), (x2 + 0.21, 0.655), color=accent_teal)

    _box(
        ax,
        (x2 + 0.04, 0.46),
        panel_w - 0.08,
        0.11,
        "Matched design:\nChristian heart-focused frame\nvs secular motive-focused control",
        fc="#F7FFFD",
        ec=accent_teal,
        fontsize=12.0,
    )
    _box(
        ax,
        (x2 + 0.04, 0.31),
        panel_w - 0.08,
        0.11,
        "Explanation analysis:\nlexical echo vs controlled semantic score",
        fc="#F7FFFD",
        ec=accent_teal,
        fontsize=12.0,
    )
    _box(
        ax,
        (x2 + 0.04, 0.17),
        panel_w - 0.08,
        0.10,
        "Mechanism readout:\nfirst-pass shift, post-hoc explanation,\nsecondary J1→J2 revision check",
        fc=light_teal,
        ec=accent_teal,
        fontsize=11.8,
        weight="bold",
    )

    # Panel 3: findings
    x3 = panel_x[2]
    _box(
        ax,
        (x3 + 0.04, 0.58),
        panel_w - 0.08,
        0.12,
        "Explanation is more prompt-sensitive\nthan first-pass exposed judgment\nrelative to baseline.",
        fc="#FFF7F7",
        ec=accent_red,
        fontsize=12.2,
        weight="bold",
    )
    _box(
        ax,
        (x3 + 0.04, 0.40),
        panel_w - 0.08,
        0.12,
        "7B shows only a modest\nChristian-minus-secular J1 heart residual.\nThe 0.5B comparison attenuates it.",
        fc="#FFF7F7",
        ec=accent_red,
        fontsize=12.0,
    )
    _box(
        ax,
        (x3 + 0.04, 0.21),
        panel_w - 0.08,
        0.12,
        "The Christian-specific explanation story\nweakens after matched control\nand lexical-echo control.",
        fc=light_red,
        ec=accent_red,
        fontsize=12.0,
        weight="bold",
    )

    footer = FancyBboxPatch(
        (0.055, 0.055),
        0.89,
        0.085,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.4,
        facecolor=light_slate,
        edgecolor=border,
    )
    ax.add_patch(footer)
    ax.text(
        0.5,
        0.082,
        "Research value: this is a reusable evaluation template for persona, value, safety,\n"
        "political, legal, and religious framing studies where explanation change can be mistaken for judgment change.",
        ha="center",
        va="center",
        fontsize=12.1,
        fontweight="bold",
        color=navy,
        wrap=True,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    return output_path


def main() -> None:
    out = build_readme_research_advance_figure()
    print(out)


if __name__ == "__main__":
    main()
