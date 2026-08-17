from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Sequence

WHITE_MAX = 69
POWERBALL_MAX = 26
CURRENT_FORMAT_START = date(2015, 10, 7)
NY_OPEN_DATA_START = date(2010, 2, 3)


@dataclass(frozen=True)
class Draw:
    draw_date: date
    white: tuple[int, int, int, int, int]
    powerball: int
    multiplier: int | None = None

    @property
    def is_current_format(self) -> bool:
        return self.draw_date >= CURRENT_FORMAT_START

    @property
    def white_sum(self) -> int:
        return sum(self.white)

    @property
    def odd_count(self) -> int:
        return sum(n % 2 for n in self.white)

    @property
    def high_count(self) -> int:
        return sum(n >= 36 for n in self.white)

    @property
    def has_consecutive(self) -> bool:
        return any(self.white[i] + 1 == self.white[i + 1] for i in range(4))


@dataclass(frozen=True)
class TicketSet:
    key: str
    name: str
    summary: str
    white: tuple[int, int, int, int, int]
    powerball: int


@dataclass
class Analysis:
    total_draws: int
    current_format_draws: int
    first_draw: date
    last_draw: date
    white_freq_current: list[tuple[int, int]]
    white_freq_all: list[tuple[int, int]]
    powerball_freq_current: list[tuple[int, int]]
    powerball_freq_all: list[tuple[int, int]]
    overdue_white: list[tuple[int, int]]
    overdue_powerball: list[tuple[int, int]]
    recent_draws: list[Draw] = field(default_factory=list)
    typical_odd: tuple[int, int] = (2, 3)
    typical_high: tuple[int, int] = (2, 3)
    typical_sum: tuple[int, int, float] = (120, 232, 177.0)
    consecutive_rate: float = 0.0


def parse_white(values: Sequence[int]) -> tuple[int, int, int, int, int]:
    balls = tuple(sorted(int(v) for v in values))
    if len(balls) != 5:
        raise ValueError(f"expected 5 white balls, got {len(balls)}")
    return balls  # type: ignore[return-value]
