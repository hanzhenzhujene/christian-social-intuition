from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from .analysis import (
    build_annotation_sheet,
    build_condition_pairs,
    build_appendix_direct_contrasts,
    build_figure_notes,
    build_main_text_direct_contrasts,
    compute_causal_contrasts,
    compute_condition_summary,
    compute_direct_control_contrasts,
    compute_family_audit_summary,
    compute_heterogeneity_summary,
    compute_mixed_effects,
    compute_revision_summary,
    compute_sanity_agreement,
    load_annotation,
    load_results,
    plot_cross_model_comparison,
    plot_explanation_layer_effect,
    plot_first_pass_shift,
    plot_heterogeneity,
    plot_judgment_explanation_dissociation,
    plot_revision_figure,
    select_qualitative_examples,
    write_analysis_report,
)
from .build_items import apply_review_overrides, build_and_export_items
from .experiment import ExperimentRunner, load_items, select_sanity_subset
from .moral_stories import fetch_moral_stories
from .prompts import load_frames


def load_config(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def sanitize_filename(value: str) -> str:
    return value.replace(":", "_").replace("/", "_")


def _resolve_item_path(cfg: dict, results_df: pd.DataFrame, explicit_path: str | None) -> Path | None:
    if explicit_path:
        return Path(explicit_path)
    dataset_cfg = cfg["dataset"]
    split_values = sorted(value for value in results_df.get("split", pd.Series(dtype=str)).dropna().unique() if value)
    split = split_values[0] if len(split_values) == 1 else "eval"
    candidate = dataset_cfg["eval_path"] if split == "eval" else dataset_cfg["dev_path"]
    path = Path(candidate)
    return path if path.exists() else None


def _load_item_frame(item_path: Path | None) -> pd.DataFrame | None:
    if item_path is None or not item_path.exists():
        return None
    return pd.DataFrame([item.to_dict() for item in load_items(item_path)])


def cmd_fetch_moral_stories(args: argparse.Namespace) -> None:
    target = fetch_moral_stories(args.output, force=args.force)
    print(f"Downloaded Moral Stories to {target}")


def cmd_build_items(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    dataset_cfg = cfg["dataset"]
    raw_path = Path(args.raw_path or dataset_cfg["raw_path"])
    if not raw_path.exists():
        fetch_moral_stories(raw_path)
    outputs = build_and_export_items(
        raw_path,
        candidate_path=args.candidate_path or dataset_cfg["candidate_pool_path"],
        dev_path=args.dev_path or dataset_cfg["draft_dev_path"],
        eval_path=args.eval_path or dataset_cfg["draft_eval_path"],
        review_csv_path=args.review_csv_path or dataset_cfg["review_csv_path"],
        candidate_limit=args.candidate_limit or dataset_cfg["candidate_limit"],
        dev_size=args.dev_size or dataset_cfg["dev_size"],
        eval_size=args.eval_size or dataset_cfg["eval_size"],
        seed=args.seed if args.seed is not None else dataset_cfg["seed"],
    )
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2))


def cmd_apply_item_review(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    dataset_cfg = cfg["dataset"]
    outputs = apply_review_overrides(
        args.candidate_path or dataset_cfg["candidate_pool_path"],
        args.review_csv_path or dataset_cfg["review_csv_path"],
        dev_path=args.dev_path or dataset_cfg["dev_path"],
        eval_path=args.eval_path or dataset_cfg["eval_path"],
        dev_size=args.dev_size or dataset_cfg["dev_size"],
        eval_size=args.eval_size or dataset_cfg["eval_size"],
        seed=args.seed if args.seed is not None else dataset_cfg["seed"],
    )
    print(json.dumps({key: str(value) for key, value in outputs.items()}, indent=2))


def cmd_run_experiment(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    runtime = cfg["runtime"]
    dataset_cfg = cfg["dataset"]
    item_path = dataset_cfg["eval_path"] if args.split == "eval" else dataset_cfg["dev_path"]
    if not Path(item_path).exists():
        raise FileNotFoundError(
            f"Locked item split not found at {item_path}. "
            "Run `build-items`, manually complete the review sheet, then run `apply-item-review` before starting the experiment."
        )
    items = load_items(item_path)
    if args.item_ids:
        wanted = set(args.item_ids)
        items = [item for item in items if item.item_id in wanted]
    if args.max_items is not None:
        items = items[: args.max_items]
    sanity_subset = select_sanity_subset(
        items,
        size=args.sanity_subset_size or dataset_cfg["sanity_subset_size"],
        seed=args.seed if args.seed is not None else dataset_cfg["seed"],
    )

    frame_mode = args.frame_mode or runtime.get("frame_mode", "selected")
    run_id = args.run_id or ("family_audit_v2" if frame_mode == "family_audit" else "selected_v2")
    runner = ExperimentRunner(
        model=args.model,
        frames_path=args.frames_path,
        split=args.split,
        run_id=run_id,
        frame_mode=frame_mode,
        ollama_base_url=args.ollama_base_url or runtime["ollama_base_url"],
        timeout=args.timeout or runtime["timeout_seconds"],
        temperature=args.temperature if args.temperature is not None else runtime["temperature"],
        max_judgment_tokens=args.max_judgment_tokens or runtime["max_judgment_tokens"],
        max_explanation_tokens=args.max_explanation_tokens or runtime["max_explanation_tokens"],
        seed=args.seed if args.seed is not None else dataset_cfg["seed"],
    )

    default_output = Path("outputs/runs") / f"{sanitize_filename(args.model)}_{args.split}_{run_id}.jsonl"
    output_path = Path(args.output) if args.output else default_output
    runner.run_items(
        items,
        output_path=output_path,
        include_sanity_subset=sanity_subset,
        resume=runtime["resume"] if args.resume is None else args.resume,
        config_path=args.config,
    )
    print(f"Experiment run written to {output_path}")
    print(f"Run manifest written to {output_path.with_suffix('.manifest.json')}")


def cmd_analyze_results(args: argparse.Namespace) -> None:
    cfg = load_config(args.config)
    analysis_cfg = cfg["analysis"]
    dataset_cfg = cfg["dataset"]
    results_df = load_results(args.results)
    item_path = _resolve_item_path(cfg, results_df, args.items_path)
    item_df = _load_item_frame(item_path)
    frames_cfg = load_frames(args.frames_path)
    lexicons = frames_cfg.get("lexicons", {})

    annotation_df = None
    if args.annotation and Path(args.annotation).exists():
        annotation_df = load_annotation(args.annotation)

    summary_df = compute_condition_summary(
        results_df,
        item_df=item_df,
        annotation_df=annotation_df,
        lexicons=lexicons,
        bootstrap_samples=args.bootstrap_samples or analysis_cfg["bootstrap_samples"],
        bootstrap_seed=args.bootstrap_seed if args.bootstrap_seed is not None else analysis_cfg["bootstrap_seed"],
    )
    direct_df = compute_direct_control_contrasts(
        results_df,
        item_df=item_df,
        lexicons=lexicons,
        bootstrap_samples=args.bootstrap_samples or analysis_cfg["bootstrap_samples"],
        bootstrap_seed=args.bootstrap_seed if args.bootstrap_seed is not None else analysis_cfg["bootstrap_seed"],
        permutation_samples=args.permutation_samples or analysis_cfg["permutation_samples"],
    )
    sanity_df = compute_sanity_agreement(results_df)
    paired_df = build_condition_pairs(results_df, item_df=item_df, lexicons=lexicons)
    mixed_effects_df = compute_mixed_effects(paired_df)
    revision_df = compute_revision_summary(results_df, item_df=item_df, lexicons=lexicons)
    heterogeneity_df = compute_heterogeneity_summary(
        results_df,
        item_df=item_df,
        lexicons=lexicons,
        bootstrap_samples=args.bootstrap_samples or analysis_cfg["bootstrap_samples"],
        bootstrap_seed=args.bootstrap_seed if args.bootstrap_seed is not None else analysis_cfg["bootstrap_seed"],
    )
    family_audit_df = compute_family_audit_summary(
        results_df,
        item_df=item_df,
        lexicons=lexicons,
        bootstrap_samples=args.bootstrap_samples or analysis_cfg["bootstrap_samples"],
        bootstrap_seed=args.bootstrap_seed if args.bootstrap_seed is not None else analysis_cfg["bootstrap_seed"],
    )
    causal_df = compute_causal_contrasts(summary_df)
    main_text_direct_df = build_main_text_direct_contrasts(direct_df)
    appendix_direct_df = build_appendix_direct_contrasts(direct_df)
    qualitative_examples_df = select_qualitative_examples(results_df, item_df=item_df, lexicons=lexicons)

    output_dir = Path(args.output_dir or "outputs/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "condition_summary.csv"
    direct_path = output_dir / "direct_control_contrasts.csv"
    causal_path = output_dir / "causal_contrasts.csv"
    sanity_path = output_dir / "sanity_agreement.csv"
    revision_path = output_dir / "revision_summary.csv"
    heterogeneity_path = output_dir / "heterogeneity_summary.csv"
    mixed_effects_path = output_dir / "mixed_effects.csv"
    family_audit_path = output_dir / "family_audit_summary.csv"
    main_text_direct_path = output_dir / "main_text_direct_contrasts.csv"
    appendix_direct_path = output_dir / "appendix_direct_contrasts_full.csv"
    qualitative_examples_path = output_dir / "qualitative_examples.csv"
    figure_notes_path = output_dir / "figure_notes.md"

    summary_df.to_csv(summary_path, index=False)
    direct_df.to_csv(direct_path, index=False)
    causal_df.to_csv(causal_path, index=False)
    sanity_df.to_csv(sanity_path, index=False)
    revision_df.to_csv(revision_path, index=False)
    heterogeneity_df.to_csv(heterogeneity_path, index=False)
    mixed_effects_df.to_csv(mixed_effects_path, index=False)
    family_audit_df.to_csv(family_audit_path, index=False)
    main_text_direct_df.to_csv(main_text_direct_path, index=False)
    appendix_direct_df.to_csv(appendix_direct_path, index=False)
    qualitative_examples_df.to_csv(qualitative_examples_path, index=False)
    figure_notes_path.write_text(build_figure_notes(), encoding="utf-8")

    annotation_sheet = build_annotation_sheet(_filter_results_for_annotation_sheet(results_df))
    annotation_sheet_path = output_dir / Path(dataset_cfg["annotation_sheet_path"]).name
    annotation_sheet.to_csv(annotation_sheet_path, index=False)

    plot_first_pass_shift(summary_df, output_dir / "first_pass_shift.png")
    plot_explanation_layer_effect(summary_df, output_dir / "explanation_layer_effect.png")
    plot_judgment_explanation_dissociation(summary_df, output_dir / "judgment_explanation_dissociation.png")
    plot_revision_figure(revision_df, output_dir / "j1_j2_revision.png")
    if not heterogeneity_df.empty:
        plot_heterogeneity(heterogeneity_df, output_dir / "heterogeneity_effects.png")
    if results_df["model"].nunique() > 1 and not direct_df.empty:
        plot_cross_model_comparison(direct_df, output_dir / "cross_model_summary.png")

    write_analysis_report(
        summary_df,
        direct_df,
        sanity_df,
        revision_df,
        heterogeneity_df,
        mixed_effects_df,
        family_audit_df=family_audit_df,
        output_path=output_dir / "analysis_report.md",
    )

    skipped_metrics = []
    if annotation_df is None:
        skipped_metrics.append("human_consistency_annotation:no_annotation_file")
    if heterogeneity_df.empty:
        skipped_metrics.append("heterogeneity:no_item_metadata_or_no_tag_counts")
    if family_audit_df.empty:
        skipped_metrics.append("family_audit:no_family_audit_rows")
    manifest = {
        "source_result_paths": [str(Path(path)) for path in args.results],
        "model_names": sorted(results_df["model"].dropna().unique(), key=lambda value: value),
        "split_values": sorted(results_df["split"].dropna().unique().tolist()),
        "item_count": int(results_df["item_id"].nunique()),
        "bootstrap_samples": args.bootstrap_samples or analysis_cfg["bootstrap_samples"],
        "bootstrap_seed": args.bootstrap_seed if args.bootstrap_seed is not None else analysis_cfg["bootstrap_seed"],
        "permutation_samples": args.permutation_samples or analysis_cfg["permutation_samples"],
        "items_path": str(item_path) if item_path is not None else None,
        "frames_path": args.frames_path,
        "frame_modes_present": sorted(results_df["frame_mode"].dropna().unique().tolist()),
        "output_dir": str(output_dir),
        "skipped_metrics": skipped_metrics,
    }
    (output_dir / "analysis_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Saved summary to {summary_path}")
    print(f"Saved direct contrasts to {direct_path}")
    print(f"Saved sanity agreement to {sanity_path}")
    print(f"Saved revision summary to {revision_path}")
    print(f"Saved heterogeneity summary to {heterogeneity_path}")
    print(f"Saved mixed effects to {mixed_effects_path}")
    print(f"Saved annotation sheet to {annotation_sheet_path}")
    print(f"Saved main-text direct contrasts to {main_text_direct_path}")
    print(f"Saved appendix direct contrasts to {appendix_direct_path}")
    print(f"Saved qualitative examples to {qualitative_examples_path}")
    print(f"Saved figure notes to {figure_notes_path}")


def _filter_results_for_annotation_sheet(results_df: pd.DataFrame) -> pd.DataFrame:
    working = results_df.copy()
    if "frame_mode" not in working.columns:
        return working
    selected = working[working["frame_mode"].fillna("selected") == "selected"].copy()
    return selected if not selected.empty else working


def cmd_build_paper_figures(args: argparse.Namespace) -> None:
    analysis_dirs = [Path(path) for path in args.analysis_dirs]
    summary_df = pd.concat([pd.read_csv(path / "condition_summary.csv") for path in analysis_dirs], ignore_index=True)
    direct_df = pd.concat([pd.read_csv(path / "direct_control_contrasts.csv") for path in analysis_dirs], ignore_index=True)
    revision_df = pd.concat([pd.read_csv(path / "revision_summary.csv") for path in analysis_dirs], ignore_index=True)
    heterogeneity_frames = [
        pd.read_csv(path / "heterogeneity_summary.csv")
        for path in analysis_dirs
        if (path / "heterogeneity_summary.csv").exists()
    ]
    heterogeneity_df = pd.concat(heterogeneity_frames, ignore_index=True) if heterogeneity_frames else pd.DataFrame()

    output_dir = Path(args.output_dir or "paper/figures")
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_first_pass_shift(summary_df, output_dir / "first_pass_shift.png")
    plot_explanation_layer_effect(summary_df, output_dir / "explanation_layer_effect.png")
    plot_judgment_explanation_dissociation(summary_df, output_dir / "judgment_explanation_dissociation.png")
    plot_revision_figure(revision_df, output_dir / "j1_j2_revision.png")
    if not heterogeneity_df.empty:
        plot_heterogeneity(heterogeneity_df, output_dir / "heterogeneity_effects.png")
    plot_cross_model_comparison(direct_df, output_dir / "cross_model_summary.png")
    print(f"Saved paper figures to {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Christian framing x SIM experiment harness")
    parser.add_argument("--config", default="configs/experiment.yaml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch-moral-stories")
    fetch_parser.add_argument("--output", default="data/raw/moral_stories_full.jsonl")
    fetch_parser.add_argument("--force", action="store_true")
    fetch_parser.set_defaults(func=cmd_fetch_moral_stories)

    build_parser_cmd = subparsers.add_parser("build-items")
    build_parser_cmd.add_argument("--raw-path")
    build_parser_cmd.add_argument("--candidate-path")
    build_parser_cmd.add_argument("--dev-path")
    build_parser_cmd.add_argument("--eval-path")
    build_parser_cmd.add_argument("--review-csv-path")
    build_parser_cmd.add_argument("--candidate-limit", type=int)
    build_parser_cmd.add_argument("--dev-size", type=int)
    build_parser_cmd.add_argument("--eval-size", type=int)
    build_parser_cmd.add_argument("--seed", type=int)
    build_parser_cmd.set_defaults(func=cmd_build_items)

    review_parser = subparsers.add_parser("apply-item-review")
    review_parser.add_argument("--candidate-path")
    review_parser.add_argument("--review-csv-path")
    review_parser.add_argument("--dev-path")
    review_parser.add_argument("--eval-path")
    review_parser.add_argument("--dev-size", type=int)
    review_parser.add_argument("--eval-size", type=int)
    review_parser.add_argument("--seed", type=int)
    review_parser.set_defaults(func=cmd_apply_item_review)

    run_parser = subparsers.add_parser("run-experiment")
    run_parser.add_argument("--model", required=True)
    run_parser.add_argument("--split", choices=["dev", "eval"], default="eval")
    run_parser.add_argument("--frames-path", default="configs/frames.yaml")
    run_parser.add_argument("--frame-mode", choices=["selected", "family_audit"])
    run_parser.add_argument("--run-id")
    run_parser.add_argument("--ollama-base-url")
    run_parser.add_argument("--timeout", type=int)
    run_parser.add_argument("--temperature", type=float)
    run_parser.add_argument("--max-judgment-tokens", type=int)
    run_parser.add_argument("--max-explanation-tokens", type=int)
    run_parser.add_argument("--sanity-subset-size", type=int)
    run_parser.add_argument("--item-ids", nargs="*")
    run_parser.add_argument("--max-items", type=int)
    run_parser.add_argument("--output")
    run_parser.add_argument("--seed", type=int)
    run_parser.add_argument("--resume", action=argparse.BooleanOptionalAction)
    run_parser.set_defaults(func=cmd_run_experiment)

    analyze_parser = subparsers.add_parser("analyze-results")
    analyze_parser.add_argument("--results", nargs="+", required=True)
    analyze_parser.add_argument("--annotation")
    analyze_parser.add_argument("--items-path")
    analyze_parser.add_argument("--frames-path", default="configs/frames.yaml")
    analyze_parser.add_argument("--output-dir")
    analyze_parser.add_argument("--bootstrap-samples", type=int)
    analyze_parser.add_argument("--bootstrap-seed", type=int)
    analyze_parser.add_argument("--permutation-samples", type=int)
    analyze_parser.set_defaults(func=cmd_analyze_results)

    paper_figures_parser = subparsers.add_parser("build-paper-figures")
    paper_figures_parser.add_argument("--analysis-dirs", nargs="+", required=True)
    paper_figures_parser.add_argument("--output-dir")
    paper_figures_parser.set_defaults(func=cmd_build_paper_figures)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
