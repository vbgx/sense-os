def trend_score(*, growth_7d: float, growth_30d: float, momentum: float = 0.0) -> float:
    # Pure formula stub
    return float(growth_7d) * 0.6 + float(growth_30d) * 0.4 + float(momentum)
