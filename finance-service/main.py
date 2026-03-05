from fastapi import FastAPI
from datetime import date
from kpi.revenue import calculate_revenue
from kpi.cost import calculate_cost
from kpi.profit import calculate_profit
from kpi.margin import calculate_margin
from services.invoices import get_invoices
from services.payments import get_payments

app = FastAPI()


@app.get("/kpi/summary")
def kpi_summary(from_date: date, to_date: date):
    return {
        "revenue": calculate_revenue(from_date, to_date).value,
        "cost": calculate_cost(from_date, to_date).value,
        "profit": calculate_profit(from_date, to_date).value,
        "margin": calculate_margin(from_date, to_date).value,
    }


@app.get("/invoices")
def invoices(from_date: date, to_date: date):
    return get_invoices(from_date, to_date)


@app.get("/payments")
def payments(from_date: date, to_date: date):
    return get_payments(from_date, to_date)
