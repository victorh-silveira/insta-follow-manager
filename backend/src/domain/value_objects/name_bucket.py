"""Value Object for alphabetical bucketing of Instagram display names."""

from dataclasses import dataclass
import unicodedata

DIGITS_BUCKET = "0-9"
SPECIAL_BUCKET = "SPECIAL"
LETTER_BUCKETS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
ALL_BUCKETS = (*LETTER_BUCKETS, DIGITS_BUCKET, SPECIAL_BUCKET)


def normalize_for_sort(text: str) -> str:
    """Return accent-stripped, lowercase string for consistent alphabetical sorting."""
    stripped = (text or "").strip()
    decomposed = unicodedata.normalize("NFKD", stripped)
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.casefold()


@dataclass(frozen=True)
class NameBucket:
    """Categorizes a profile's display name into A-Z, 0-9, or SPECIAL."""

    value: str

    def __post_init__(self) -> None:
        if self.value not in ALL_BUCKETS:
            raise ValueError(f"Invalid NameBucket value: {self.value!r}")

    @classmethod
    def from_display_name(cls, full_name: str | None) -> "NameBucket":
        """Classify a display name by its first normalized character."""
        cleaned = (full_name or "").strip()
        if not cleaned:
            return cls(SPECIAL_BUCKET)

        first_char = cleaned[0]
        decomposed = unicodedata.normalize("NFKD", first_char)
        base_chars = "".join(ch for ch in decomposed if not unicodedata.combining(ch))

        if base_chars:
            base = base_chars[0].upper()
            if "A" <= base <= "Z":
                return cls(base)
            if "0" <= base <= "9":
                return cls(DIGITS_BUCKET)

        return cls(SPECIAL_BUCKET)
