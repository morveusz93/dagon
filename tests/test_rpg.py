import pytest

from cogs.rpg import (
    DiceGroup,
    RollSpec,
    format_rolls,
    parse_roll,
    roll_dice,
    roll_embed,
    total,
)


@pytest.mark.parametrize(
    "text, groups, modifier",
    [
        ("3d6", [(3, 6, 1)], 0),
        ("2k10", [(2, 10, 1)], 0),
        ("D20", [(1, 20, 1)], 0),
        (" 100d100 ", [(100, 100, 1)], 0),
        ("d20+5", [(1, 20, 1)], 5),
        ("1d20 - 2", [(1, 20, 1)], -2),
        ("2d6+1d4-1", [(2, 6, 1), (1, 4, 1)], -1),
        ("1d20-1d4", [(1, 20, 1), (1, 4, -1)], 0),
        ("5+1d8+3", [(1, 8, 1)], 8),
        ("50d6+50d6", [(50, 6, 1), (50, 6, 1)], 0),
    ],
)
def test_parse_roll_valid(text, groups, modifier):
    spec = parse_roll(text)
    assert [(g.count, g.sides, g.sign) for g in spec.groups] == groups
    assert spec.modifier == modifier


@pytest.mark.parametrize(
    "text",
    [
        "",
        "abc",
        "5",  # brak kości
        "0d6",
        "1d0",
        "101d6",
        "1d101",
        "51d6+50d6",  # łącznie > 100 kości
        "1d",
        "d",
        "2x6",
        "-1d6",  # pierwszy wyraz ze znakiem
        "+1d6",
        "1d6+",
        "1d6++2",
        "1d6 2",  # brak znaku między wyrazami
        "1 d6",
        "1d20+1001",
        "+".join(["1d6"] * 11),  # za dużo wyrazów
    ],
)
def test_parse_roll_invalid(text):
    with pytest.raises(ValueError):
        parse_roll(text)


@pytest.mark.parametrize(
    "text, expected",
    [
        ("3d6", "3d6"),
        ("d20+5", "1d20 + 5"),
        ("2d6+1d4-1", "2d6 + 1d4 − 1"),
        ("1d20-1d4", "1d20 − 1d4"),
        ("3+1d6", "1d6 + 3"),
    ],
)
def test_spec_is_shown_normalized(text, expected):
    assert str(parse_roll(text)) == expected


def test_roll_dice_respects_counts_and_sides():
    spec = parse_roll("3d6+2d4")
    results = roll_dice(spec)
    assert [len(r) for r in results] == [3, 2]
    assert all(1 <= r <= 6 for r in results[0])
    assert all(1 <= r <= 4 for r in results[1])


def test_total_applies_signs_and_modifier():
    spec = RollSpec((DiceGroup(2, 6), DiceGroup(1, 4, -1)), modifier=3)
    assert total(spec, [[5, 6], [2]]) == 12


def test_format_rolls_as_tiles_marking_min_and_max():
    assert format_rolls([1, 6, 3], 6) == "`1`💀  `6`⭐  `3`"


def test_format_single_sided_die_counts_as_max():
    assert format_rolls([1], 1) == "`1`⭐"


def test_embed_single_die_has_no_sum():
    embed = roll_embed("@tester", parse_roll("d20"), [[7]])
    assert "@tester rzuca **1d20**" in embed.description
    assert "Suma" not in embed.description


def test_embed_single_group_sums():
    embed = roll_embed("@tester", parse_roll("3d6"), [[1, 6, 3]])
    assert "`1`💀  `6`⭐  `3`" in embed.description
    assert embed.description.endswith("Suma: **10**")


def test_embed_modifier_on_single_die_shows_sum():
    embed = roll_embed("@tester", parse_roll("d20+5"), [[12]])
    assert "Modyfikator: **+5**" in embed.description
    assert embed.description.endswith("Suma: **17**")


def test_embed_multiple_groups_get_labelled_lines():
    embed = roll_embed("@tester", parse_roll("2d6-1d4-1"), [[3, 6], [4]])
    assert "**2d6:** `3`  `6`⭐" in embed.description
    assert "**−1d4:** `4`⭐" in embed.description
    assert "Modyfikator: **−1**" in embed.description
    assert embed.description.endswith("Suma: **4**")
