from christian_social_intuition.paired_stats import cohens_dz, paired_bootstrap_ci, paired_mean, sign_flip_permutation_test


def test_paired_stats_basic_behavior():
    values = [0.0, 0.0, 1.0, 1.0]
    assert paired_mean(values) == 0.5
    ci_low, ci_high = paired_bootstrap_ci(values, n_boot=50, seed=1)
    assert ci_low <= ci_high
    p_value = sign_flip_permutation_test(values, n_perm=200, seed=1)
    assert 0.0 <= p_value <= 1.0
    assert cohens_dz(values) > 0


def test_cohens_dz_handles_zero_variance():
    assert cohens_dz([0.0, 0.0, 0.0]) == 0.0
