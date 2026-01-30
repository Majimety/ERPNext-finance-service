from .models import KPIResult
from .revenue import calculate_revenue
from .profit import calculate_profit


def calculate_margin(from_date, to_date):
    revenue = calculate_revenue(from_date, to_date).value
    profit = calculate_profit(from_date, to_date).value

    margin = (profit / revenue * 100) if revenue else 0

    return KPIResult(from_date=from_date, to_date=to_date, value=round(margin, 2))
