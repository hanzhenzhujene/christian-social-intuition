from __future__ import annotations

import math
from typing import Iterable

import numpy as np


def paired_mean(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        return math.nan
    return float(array.mean())


def paired_bootstrap_ci(
    values: Iterable[float],
    *,
    n_boot: int = 1000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float]:
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(seed)
    draws = rng.choice(array, size=(n_boot, array.size), replace=True)
    means = draws.mean(axis=1)
    lower = np.quantile(means, alpha / 2)
    upper = np.quantile(means, 1 - alpha / 2)
    return float(lower), float(upper)


def sign_flip_permutation_test(
    values: Iterable[float],
    *,
    n_perm: int = 5000,
    seed: int = 42,
) -> float:
    array = np.asarray(list(values), dtype=float)
    array = array[~np.isnan(array)]
    if array.size == 0:
        return math.nan
    observed = abs(array.mean())
    if observed == 0:
        return 1.0
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=(n_perm, array.size))
    permuted = np.abs((signs * array).mean(axis=1))
    extreme = int(np.count_nonzero(permuted >= observed))
    return float((extreme + 1) / (n_perm + 1))


def cohens_dz(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=float)
    array = array[~np.isnan(array)]
    if array.size < 2:
        return math.nan
    std = float(array.std(ddof=1))
    if std == 0:
        return 0.0
    return float(array.mean() / std)
