
import numpy as np

from app.recommendation import pearson_correlation


def test_pearson_basic_positive():
    vec_a = np.array([1, 2, 3, 4], dtype=float)
    vec_b = np.array([2, 4, 6, 8], dtype=float)
    score = pearson_correlation(vec_a, vec_b)
    assert np.isclose(score, 1.0)

