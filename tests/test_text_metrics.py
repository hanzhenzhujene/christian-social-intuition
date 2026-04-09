from christian_social_intuition.text_metrics import compute_explanation_metrics, matched_terms


def test_compute_explanation_metrics_separates_echo_and_controlled_semantics():
    metrics = compute_explanation_metrics(
        "The heart behind it looks selfish and callous.",
        strict_echo_terms=["heart behind it", "heart"],
        non_echo_semantic_terms=["selfish", "callous", "greedy"],
    )
    assert metrics["frame_echo_score"] >= 1
    assert metrics["semantic_score_raw"] >= metrics["frame_echo_score"]
    assert metrics["semantic_score_controlled"] >= 1


def test_restructure_beyond_echo_only_fires_without_direct_echo():
    metrics = compute_explanation_metrics(
        "The choice is selfish and manipulative.",
        strict_echo_terms=["heart", "motive"],
        non_echo_semantic_terms=["selfish", "manipulative"],
    )
    assert metrics["frame_echo_score"] == 0
    assert metrics["restructure_beyond_echo"] == 1


def test_matched_terms_returns_unique_phrase_hits():
    matches = matched_terms(
        "The heart behind it still looks selfish and callous.",
        ["heart behind it", "heart", "selfish", "greedy"],
    )
    assert "heart behind it" in matches
    assert "selfish" in matches
    assert "greedy" not in matches
