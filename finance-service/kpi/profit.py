from .models import KPIResult
from .revenue import calculate_revenue
from .cost import calculate_cost


def calculate_profit(from_date, to_date):
    revenue = calculate_revenue(from_date, to_date).value
    cost = calculate_cost(from_date, to_date).value

    profit = revenue - cost

    return KPIResult(from_date=from_date, to_date=to_date, value=profit)
