from datetime import datetime


def get_consumption_for_hour(
    *,
    consumptions: list[tuple[datetime, float]],
    target_datetime: datetime,
) -> float:
    target_hour = target_datetime.replace(minute=0, second=0, microsecond=0)

    return sum(
        [
            consumption
            for (date, consumption) in consumptions
            if date.replace(minute=0, second=0, microsecond=0) <= target_hour
        ],
        0.0,
    )
