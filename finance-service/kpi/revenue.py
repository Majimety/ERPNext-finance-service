import os
from dotenv import load_dotenv
from .models import KPIResult
from services.erpnext import get_gl_entries

load_dotenv()

INCOME_ACCOUNTS = [os.getenv("INCOME_ACCOUNT", "Sales - KKU")]


def calculate_revenue(from_date, to_date):
    gl_entries = get_gl_entries(from_date, to_date, INCOME_ACCOUNTS)

    revenue = sum(row["credit"] for row in gl_entries)

    return KPIResult(from_date=from_date, to_date=to_date, value=revenue)