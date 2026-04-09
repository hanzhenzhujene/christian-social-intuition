import json

import pandas as pd

from christian_social_intuition.analysis import (
    build_appendix_direct_contrasts,
    build_condition_pairs,
    build_figure_notes,
    build_main_text_direct_contrasts,
    compute_condition_summary,
    compute_direct_control_contrasts,
    compute_heterogeneity_summary,
    compute_mixed_effects,
    compute_revision_summary,
    load_results,
    plot_cross_model_comparison,
    plot_explanation_layer_effect,
    plot_first_pass_shift,
    plot_heterogeneity,
    plot_judgment_explanation_dissociation,
    plot_revision_figure,
    select_qualitative_examples,
)


def _demo_results() -> pd.DataFrame:
    rows = []
    item_meta = {
        "1": {"primary_tension_tag": "motive_vs_outcome", "moral_option": "A", "scenario_context": "Case 1", "option_a": "Do A", "option_b": "Do B"},
        "2": {"primary_tension_tag": "appearance_vs_intention", "moral_option": "B", "scenario_context": "Case 2", "option_a": "Do A2", "option_b": "Do B2"},
    }
    for item_id, meta in item_meta.items():
        baseline_choice = "A" if item_id == "1" else "B"
        rows.append(
            {
                "model": "qwen2.5:7b-instruct",
                "condition": "baseline",
                "item_id": item_id,
                "j1_act": baseline_choice,
                "j1_heart": baseline_choice,
                "e_focus": "outward act/rule",
                "e_text": "Baseline explanation.",
                "j2_act": baseline_choice,
                "j2_heart": baseline_choice,
                **meta,
            }
        )
        rows.append(
            {
                "model": "qwen2.5:7b-instruct",
                "condition": "secular_pre",
                "item_id": item_id,
                "j1_act": baseline_choice,
                "j1_heart": "B",
                "e_focus": "motive/heart",
                "e_text": "The act looks more self-serving.",
                "j2_act": baseline_choice,
                "j2_heart": "B",
                **meta,
            }
        )
        rows.append(
            {
                "model": "qwen2.5:7b-instruct",
                "condition": "christian_pre",
                "item_id": item_id,
                "j1_act": baseline_choice,
                "j1_heart": "B",
                "e_focus": "motive/heart",
                "e_text": "The worse heart looks selfish and manipulative.",
                "j2_act": baseline_choice,
                "j2_heart": "B",
                **meta,
            }
        )
        rows.append(
            {
                "model": "qwen2.5:7b-instruct",
                "condition": "secular_post",
                "item_id": item_id,
                "j1_act": baseline_choice,
                "j1_heart": baseline_choice,
                "e_focus": "motive/heart",
                "e_text": "The motive seems selfish.",
                "j2_act": baseline_choice,
                "j2_heart": baseline_choice,
                **meta,
            }
        )
        rows.append(
            {
                "model": "qwen2.5:7b-instruct",
                "condition": "christian_post",
                "item_id": item_id,
                "j1_act": baseline_choice,
                "j1_heart": baseline_choice,
                "e_focus": "motive/heart",
                "e_text": "The heart behind it looks worse." if item_id == "1" else "The choice is selfish and callous.",
                "j2_act": baseline_choice,
                "j2_heart": "B",
                **meta,
            }
        )
        rows.append(
            {
                "model": "qwen2.5:7b-instruct",
                "condition": "baseline_judgment_only",
                "item_id": item_id,
                "j1_act": baseline_choice,
                "j1_heart": baseline_choice,
                "e_focus": None,
                "e_text": None,
                "j2_act": None,
                "j2_heart": None,
                **meta,
            }
        )
    return pd.DataFrame(rows)


def _lexicons() -> dict:
    return {
        "strict_echo_terms": ["heart behind it", "heart", "motive", "intention"],
        "non_echo_semantic_terms": ["selfish", "manipulative", "callous", "greedy"],
    }


def test_compute_condition_summary_has_expected_columns():
    summary = compute_condition_summary(_demo_results(), lexicons=_lexicons(), bootstrap_samples=50, bootstrap_seed=1)
    expected = {
        "j1_act_shift_rate",
        "j1_heart_shift_rate",
        "semantic_raw_delta_vs_baseline",
        "semantic_controlled_delta_vs_baseline",
        "posthoc_controlled_semantic_index",
    }
    assert expected.issubset(summary.columns)
    assert {"baseline", "secular_pre", "christian_pre", "secular_post", "christian_post"} == set(summary["condition"])


def test_direct_control_contrasts_include_primary_mechanism_checks():
    contrasts = compute_direct_control_contrasts(
        _demo_results(),
        lexicons=_lexicons(),
        bootstrap_samples=50,
        bootstrap_seed=1,
        permutation_samples=200,
    )
    assert not contrasts.empty
    assert {
        "christian_pre_vs_secular_pre_j1_act_shift",
        "christian_pre_vs_secular_pre_j1_heart_shift",
        "christian_post_vs_secular_post_explanation_controlled",
        "christian_post_vs_secular_post_j2_heart_revision",
    }.issubset(set(contrasts["contrast"]))

    main_text = build_main_text_direct_contrasts(contrasts)
    appendix = build_appendix_direct_contrasts(contrasts)
    assert not main_text.empty
    assert not appendix.empty
    assert "contrast_label" in main_text.columns
    assert "estimate_with_ci" in appendix.columns


def test_build_condition_pairs_and_mixed_effects():
    paired = build_condition_pairs(_demo_results(), lexicons=_lexicons())
    assert not paired.empty
    assert {"j1_act_shift", "j1_heart_shift", "semantic_controlled_present", "dissociated_explanation_shift"}.issubset(
        paired.columns
    )
    mixed = compute_mixed_effects(paired)
    assert not mixed.empty
    assert {"model", "metric", "term", "converged"}.issubset(mixed.columns)


def test_revision_and_heterogeneity_outputs_exist():
    results = _demo_results()
    item_df = results[["item_id", "primary_tension_tag", "moral_option"]].drop_duplicates()
    revision = compute_revision_summary(results, item_df=item_df, lexicons=_lexicons())
    heterogeneity = compute_heterogeneity_summary(results, item_df=item_df, lexicons=_lexicons(), bootstrap_samples=20, bootstrap_seed=1)
    assert not revision.empty
    assert {"j2_act_revision_rate", "j2_heart_revision_rate", "toward_moral_option_rate"}.issubset(revision.columns)
    assert not heterogeneity.empty
    assert {"primary_tension_tag", "contrast", "estimate"}.issubset(heterogeneity.columns)


def test_plot_functions_write_files(tmp_path):
    results = pd.concat(
        [
            _demo_results(),
            _demo_results().assign(model="qwen2.5:0.5b-instruct"),
        ],
        ignore_index=True,
    )
    item_df = results[["item_id", "primary_tension_tag", "moral_option"]].drop_duplicates()
    summary = compute_condition_summary(results, item_df=item_df, lexicons=_lexicons(), bootstrap_samples=20, bootstrap_seed=1)
    direct = compute_direct_control_contrasts(results, item_df=item_df, lexicons=_lexicons(), bootstrap_samples=20, bootstrap_seed=1, permutation_samples=200)
    revision = compute_revision_summary(results, item_df=item_df, lexicons=_lexicons())
    heterogeneity = compute_heterogeneity_summary(results, item_df=item_df, lexicons=_lexicons(), bootstrap_samples=20, bootstrap_seed=1)

    first_pass = tmp_path / "first_pass.png"
    explanation = tmp_path / "explanation.png"
    dissociation = tmp_path / "dissociation.png"
    revision_path = tmp_path / "revision.png"
    heterogeneity_path = tmp_path / "heterogeneity.png"
    comparison_path = tmp_path / "comparison.png"

    plot_first_pass_shift(summary, first_pass)
    plot_explanation_layer_effect(summary, explanation)
    plot_judgment_explanation_dissociation(summary, dissociation)
    plot_revision_figure(revision, revision_path)
    plot_heterogeneity(heterogeneity, heterogeneity_path)
    plot_cross_model_comparison(direct, comparison_path)

    for path in [first_pass, explanation, dissociation, revision_path, heterogeneity_path, comparison_path]:
        assert path.exists() and path.stat().st_size > 0


def test_select_qualitative_examples_and_figure_notes():
    results = _demo_results()
    item_df = results[["item_id", "primary_tension_tag", "moral_option", "scenario_context", "option_a", "option_b"]].drop_duplicates()
    examples = select_qualitative_examples(results, item_df=item_df, lexicons=_lexicons())
    notes = build_figure_notes()
    assert not examples.empty
    assert {"rule_id", "item_id", "matched_strict_echo_terms", "scenario_context"}.issubset(examples.columns)
    assert "Figure 1" in notes


def test_load_results_backfills_from_raw_trace(tmp_path):
    payload = {
        "model": "qwen2.5:0.5b-instruct",
        "condition": "christian_pre",
        "item_id": "1",
        "j1_act": None,
        "j1_heart": "A",
        "e_focus": None,
        "e_text": None,
        "j2_act": None,
        "j2_heart": None,
        "raw_trace": {
            "j1": {"raw_text": '{"overall_problematic":"Option A","heart_worse":"A"}'},
            "explanation": {"raw_text": '{"focus":"heart_worse","text":"Option A reflects a selfish motive."}'},
            "j2": {"raw_text": '{"overall_problematic":"Option A","heart_worse":"Option B"}'},
        },
    }
    path = tmp_path / "results.jsonl"
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")

    results = load_results(path)
    row = results.iloc[0]
    assert row["j1_act"] == "A"
    assert row["e_focus"] == "motive/heart"
    assert row["j2_act"] == "A"
    assert row["j2_heart"] == "B"
