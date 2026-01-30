from datetime import date
from kpi.revenue import calculate_revenue
from kpi.cost import calculate_cost
from kpi.profit import calculate_profit
from kpi.margin import calculate_margin

FROM = date(2026, 1, 1)
TO = date(2026, 1, 31)

print("Revenue:", calculate_revenue(FROM, TO))
print("Cost:", calculate_cost(FROM, TO))
print("Profit:", calculate_profit(FROM, TO))
print("Margin:", calculate_margin(FROM, TO))
