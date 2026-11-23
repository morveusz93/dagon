import pytest

from cogs.rpg import format_rolls, parse_dice


@pytest.mark.parametrize(
    "text, expected",
    [
        ("3d6", (3, 6)),
        ("2k10", (2, 10)),
        ("D20", (1, 20)),
        ("k100", (1, 100)),
        (" 100d100 ", (100, 100)),
    ],
)
def test_parse_dice_valid(text, expected):
    assert parse_dice(text) == expected


@pytest.mark.parametrize(
    "text", ["", "abc", "0d6", "1d0", "101d6", "1d101", "1d", "d", "2x6", "-1d6"]
)
def test_parse_dice_invalid(text):
    with pytest.raises(ValueError):
        parse_dice(text)


def test_format_single_roll_has_no_sum():
    assert format_rolls([4], 6) == "4"


def test_format_marks_min_and_max_and_sums():
    assert format_rolls([1, 6, 3], 6) == "*1* **6** 3 = 10"
