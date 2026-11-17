"""Unit tests for NameBucket value object."""

import pytest

from src.domain.value_objects.name_bucket import (
    ALL_BUCKETS,
    DIGITS_BUCKET,
    SPECIAL_BUCKET,
    NameBucket,
)


@pytest.mark.parametrize(
    ("display_name", "expected"),
    [
        ("Ana Julia", "A"),
        ("artur silva", "A"),
        ("Ágata Costa", "A"),
        ("Érika Mendes", "E"),
        ("Ícaro Souza", "I"),
        ("Óscar Lima", "O"),
        ("Úrsula Dias", "U"),
        ("Çelik Kaya", "C"),
        ("  Beatriz", "B"),
        ("Zeca Pagodinho", "Z"),
        ("007 Tech", DIGITS_BUCKET),
        ("123 Milhas", DIGITS_BUCKET),
        ("99 Design", DIGITS_BUCKET),
        ("✨ Lua Nova", SPECIAL_BUCKET),
        ("_dev_carlos", SPECIAL_BUCKET),
        (".ponto", SPECIAL_BUCKET),
        ("@arroba", SPECIAL_BUCKET),
        ("", SPECIAL_BUCKET),
        ("   ", SPECIAL_BUCKET),
        (None, SPECIAL_BUCKET),
    ],
)
def test_from_display_name_classifies_correctly(display_name: str | None, expected: str) -> None:
    bucket = NameBucket.from_display_name(display_name)
    assert bucket.value == expected


def test_invalid_bucket_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Invalid NameBucket value"):
        NameBucket("INVALID")


def test_all_buckets_contains_28_entries() -> None:
    assert len(ALL_BUCKETS) == 28
    assert ALL_BUCKETS[0] == "A"
    assert ALL_BUCKETS[25] == "Z"
    assert ALL_BUCKETS[26] == DIGITS_BUCKET
    assert ALL_BUCKETS[27] == SPECIAL_BUCKET
