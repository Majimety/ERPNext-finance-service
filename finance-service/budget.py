from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import json, os

BUDGET_FILE = "budget_config.json"


@dataclass
class BudgetConfig:
    cost_limit: float = 0.0
    revenue_target: float = 0.0
    profit_target: float = 0.0
    margin_min: float = 0.0


def load_budget() -> BudgetConfig:
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE) as f:
            data = json.load(f)
        return BudgetConfig(**data)
    return BudgetConfig()


def save_budget(config: BudgetConfig):
    with open(BUDGET_FILE, "w") as f:
        json.dump(config.__dict__, f)


def check_alerts(kpi: dict, config: BudgetConfig) -> list[dict]:
    alerts = []
    if config.cost_limit and kpi["cost"] > config.cost_limit:
        alerts.append(
            {
                "level": "danger",
                "type": "cost_exceeded",
                "message": f"ต้นทุนเกินงบ: {kpi['cost']:,.0f} > {config.cost_limit:,.0f}",
                "value": kpi["cost"],
                "limit": config.cost_limit,
            }
        )
    if config.revenue_target and kpi["revenue"] < config.revenue_target:
        pct = kpi["revenue"] / config.revenue_target * 100
        alerts.append(
            {
                "level": "warning" if pct >= 80 else "danger",
                "type": "revenue_below_target",
                "message": f"รายรับต่ำกว่าเป้า: {kpi['revenue']:,.0f} / {config.revenue_target:,.0f} ({pct:.1f}%)",
                "value": kpi["revenue"],
                "target": config.revenue_target,
                "pct": round(pct, 1),
            }
        )
    if config.profit_target and kpi["profit"] < config.profit_target:
        alerts.append(
            {
                "level": "warning",
                "type": "profit_below_target",
                "message": f"กำไรต่ำกว่าเป้า: {kpi['profit']:,.0f} / {config.profit_target:,.0f}",
                "value": kpi["profit"],
                "target": config.profit_target,
            }
        )
    if config.margin_min and kpi["margin"] < config.margin_min:
        alerts.append(
            {
                "level": "danger",
                "type": "margin_too_low",
                "message": f"Margin ต่ำกว่าเกณฑ์: {kpi['margin']:.1f}% < {config.margin_min:.1f}%",
                "value": kpi["margin"],
                "min": config.margin_min,
            }
        )
    if not alerts:
        alerts.append(
            {
                "level": "ok",
                "type": "all_clear",
                "message": "KPI ทุกรายการอยู่ในเกณฑ์ที่กำหนด ✓",
            }
        )
    return alerts
