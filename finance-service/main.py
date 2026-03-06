from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from kpi.revenue import calculate_revenue
from kpi.cost import calculate_cost
from kpi.profit import calculate_profit
from kpi.margin import calculate_margin
from services.invoices import get_invoices
from services.payments import get_payments
from services.erpnext import get_gl_entries
from budget import load_budget, save_budget, check_alerts, BudgetConfig
from pydantic import BaseModel
import csv, io, json

app = FastAPI(title="Finance Service — KKU")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── KPI Summary ───────────────────────────────────────────
@app.get("/kpi/summary")
def kpi_summary(from_date: date, to_date: date):
    return {
        "revenue": calculate_revenue(from_date, to_date).value,
        "cost": calculate_cost(from_date, to_date).value,
        "profit": calculate_profit(from_date, to_date).value,
        "margin": calculate_margin(from_date, to_date).value,
    }


# ─── Invoices & Payments ───────────────────────────────────
@app.get("/invoices")
def invoices(from_date: date, to_date: date):
    return get_invoices(from_date, to_date)


@app.get("/payments")
def payments(from_date: date, to_date: date):
    return get_payments(from_date, to_date)


# ─── GL Entries ────────────────────────────────────────────
@app.get("/gl-entries")
def gl_entries(from_date: date, to_date: date):
    return get_gl_entries(from_date, to_date)


# ─── Cost Center Breakdown ─────────────────────────────────
@app.get("/cost-center")
def cost_center(from_date: date, to_date: date):
    entries = get_gl_entries(from_date, to_date)
    breakdown = {}
    for row in entries:
        cc = row.get("cost_center") or row.get("account", "Unknown")
        if cc not in breakdown:
            breakdown[cc] = {"debit": 0, "credit": 0}
        breakdown[cc]["debit"] += row.get("debit", 0)
        breakdown[cc]["credit"] += row.get("credit", 0)
    return [
        {
            "cost_center": k,
            "debit": v["debit"],
            "credit": v["credit"],
            "net": v["credit"] - v["debit"],
        }
        for k, v in breakdown.items()
    ]


# ─── Budget Alerts ─────────────────────────────────────────
@app.get("/budget/config")
def get_budget_config():
    return load_budget().__dict__


class BudgetConfigIn(BaseModel):
    cost_limit: float = 0.0
    revenue_target: float = 0.0
    profit_target: float = 0.0
    margin_min: float = 0.0


@app.post("/budget/config")
def set_budget_config(cfg: BudgetConfigIn):
    save_budget(BudgetConfig(**cfg.dict()))
    return {"ok": True}


@app.get("/budget/alerts")
def budget_alerts(from_date: date, to_date: date):
    kpi = {
        "revenue": calculate_revenue(from_date, to_date).value,
        "cost": calculate_cost(from_date, to_date).value,
        "profit": calculate_profit(from_date, to_date).value,
        "margin": calculate_margin(from_date, to_date).value,
    }
    config = load_budget()
    return {
        "kpi": kpi,
        "alerts": check_alerts(kpi, config),
        "budget": config.__dict__,
    }


# ─── Export CSV ────────────────────────────────────────────
@app.get("/export/invoices")
def export_invoices(from_date: date, to_date: date):
    data = get_invoices(from_date, to_date)
    buf = io.StringIO()
    if data:
        writer = csv.DictWriter(buf, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=invoices_{from_date}_{to_date}.csv"
        },
    )


@app.get("/export/payments")
def export_payments(from_date: date, to_date: date):
    data = get_payments(from_date, to_date)
    buf = io.StringIO()
    if data:
        writer = csv.DictWriter(buf, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=payments_{from_date}_{to_date}.csv"
        },
    )


@app.get("/export/kpi")
def export_kpi(from_date: date, to_date: date):
    kpi = {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "revenue": calculate_revenue(from_date, to_date).value,
        "cost": calculate_cost(from_date, to_date).value,
        "profit": calculate_profit(from_date, to_date).value,
        "margin": calculate_margin(from_date, to_date).value,
    }
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=kpi.keys())
    writer.writeheader()
    writer.writerow(kpi)
    return Response(
        content=buf.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=kpi_{from_date}_{to_date}.csv"
        },
    )
