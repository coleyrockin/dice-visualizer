import pytest

from dice_visualizer import (
    count_matching_outcomes,
    probability_for_sum,
    validate_dice_target,
)


def test_validates_dice_target_range():
    assert validate_dice_target(2, 7) == (2, 7)

    with pytest.raises(ValueError):
        validate_dice_target(0, 1)

    with pytest.raises(ValueError):
        validate_dice_target(2, 13)


def test_counts_ordered_matching_outcomes():
    assert count_matching_outcomes(1, 6) == 1
    assert count_matching_outcomes(2, 7) == 6
    assert count_matching_outcomes(3, 3) == 1
    assert count_matching_outcomes(3, 18) == 1
    assert count_matching_outcomes(4, 14) == 146


def test_probability_for_sum():
    assert probability_for_sum(2, 7) == pytest.approx(6 / 36)
    assert probability_for_sum(4, 14) == pytest.approx(146 / 1296)
