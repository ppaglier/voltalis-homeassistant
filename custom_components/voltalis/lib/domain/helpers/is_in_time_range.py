from datetime import time

from custom_components.voltalis.lib.domain.range_model import RangeModel


def is_in_time_range(time_range: RangeModel[time], now: time) -> bool:
    """Return True if now is within the given time range, handling overnight spans."""
    start = time_range.start
    end = time_range.end
    if start <= end:
        # Normal range within the same day, e.g. 08:00-12:00
        return start <= now <= end
    # Overnight range crossing midnight, e.g. 22:00-06:00
    return now >= start or now <= end
