from dataclasses import dataclass
from datetime import date


@dataclass
class KPIResult:
    from_date: date
    to_date: date
    value: float
    breakdown: dict | None = None
