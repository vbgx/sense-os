from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Sequence


@dataclass(frozen=True)
class DailyVolume:
    day: date
    volume: int


@dataclass(frozen=True)
class TimelinePoint:
    day: date
    volume: int
    growth_rate: float   # day-over-day growth ratio
    velocity: float      # delta volume
    breakout_flag: bool  # simple heuristic v1


def compute_timeline(points: Sequence[DailyVolume]) -> list[TimelinePoint]:
    """
    Deterministic timeline derivation from daily volumes.

    v1 definitions:
      velocity = volume_t - volume_{t-1}
      growth_rate = (volume_t - volume_{t-1}) / max(volume_{t-1}, 1)

      breakout_flag heuristic (v1):
        breakout if:
          - velocity >= 5
          - growth_rate >= 0.50
          - volume_t >= 10
    """
    if not points:
        return []

    ordered = sorted(points, key=lambda p: p.day)
    out: list[TimelinePoint] = []

    prev = ordered[0]
    # first day has no previous context
    out.append(
        TimelinePoint(
            day=prev.day,
            volume=int(prev.volume),
            growth_rate=0.0,
            velocity=0.0,
            breakout_flag=False,
        )
    )

    for cur in ordered[1:]:
        v_prev = int(prev.volume)
        v_cur = int(cur.volume)
        velocity = float(v_cur - v_prev)
        growth = float(v_cur - v_prev) / float(max(v_prev, 1))

        breakout = (velocity >= 5.0) and (growth >= 0.50) and (v_cur >= 10)

        out.append(
            TimelinePoint(
                day=cur.day,
                volume=v_cur,
                growth_rate=growth,
                velocity=velocity,
                breakout_flag=breakout,
            )
        )
        prev = cur

    return out
