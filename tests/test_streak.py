import pytest
from streak import longest_positive_streak

def test_empty_list():
    assert longest_positive_streak([]) == 0

def test_no_positive_numbers():
    assert longest_positive_streak([-1, -2, -3, 0]) == 0

def test_all_positive_numbers():
    assert longest_positive_streak([1, 2, 3, 4, 5]) == 5

def test_single_streak():
    assert longest_positive_streak([2, 3, -1, 5, 6, 7, 0, 4]) == 3

def test_multiple_streaks():
    assert longest_positive_streak([1, 2, 0, 4, 5, 6, -1, 8, 9]) == 3

def test_streaks_of_equal_length():
    assert longest_positive_streak([1, 2, 0, 4, 5, 0, 8, 9]) == 2

def test_streak_at_the_end():
    assert longest_positive_streak([-1, 0, 1, 2, 3, 4, 5]) == 5
