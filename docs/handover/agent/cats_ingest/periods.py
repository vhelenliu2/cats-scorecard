"""Dynamic reporting-period helpers. No hard-coded 'current' dates.

The as-of date is always supplied by the run (BUILD_PLAN.md §4/§5).
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


def parse_as_of(s: Optional[str]) -> date:
    if not s:
        return date.today()
    return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()


def quarter_of(d: date) -> int:
    return (d.month - 1) // 3 + 1


def quarter_label(d: date) -> str:
    return "Q%d %d" % (quarter_of(d), d.year)


def quarter_start(d: date) -> date:
    q = quarter_of(d)
    return date(d.year, 3 * (q - 1) + 1, 1)


@dataclass
class PeriodContext:
    as_of: date

    @property
    def year(self) -> int:
        return self.as_of.year

    @property
    def quarter(self) -> int:
        return quarter_of(self.as_of)

    @property
    def quarter_label(self) -> str:
        return quarter_label(self.as_of)

    @property
    def month_label(self) -> str:
        return self.as_of.strftime("%Y-%m")

    @property
    def completed_months_in_quarter(self) -> int:
        """Whole months completed within the current quarter as of `as_of`.

        A month counts as completed once we are at/after its month-end. We use
        the as-of month index within the quarter minus 1 (the current month is
        only 'completed' at month end). Clamped to [0, 3].
        """
        month_in_q = (self.as_of.month - 1) % 3  # 0,1,2 for the 3 months
        # If as_of is the last day of its month, that month is complete too.
        last_day = _is_month_end(self.as_of)
        completed = month_in_q + (1 if last_day else 0)
        return max(0, min(3, completed))

    @property
    def completed_months_in_year(self) -> int:
        completed = self.as_of.month - 1
        if _is_month_end(self.as_of):
            completed += 1
        return max(0, min(12, completed))

    @property
    def fraction_of_year_elapsed(self) -> float:
        return self.completed_months_in_year / 12.0

    @property
    def fraction_of_quarter_elapsed(self) -> float:
        return self.completed_months_in_quarter / 3.0


def _is_month_end(d: date) -> bool:
    return d.day == calendar.monthrange(d.year, d.month)[1]
