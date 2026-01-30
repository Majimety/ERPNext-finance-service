from .models import KPIResult
from services.erpnext import get_gl_entries

INCOME_ACCOUNTS = ["Sales - KKU"]


def calculate_revenue(from_date, to_date):
    gl_entries = get_gl_entries(from_date, to_date, INCOME_ACCOUNTS)

    revenue = sum(row["credit"] for row in gl_entries)

    return KPIResult(from_date=from_date, to_date=to_date, value=revenue)
