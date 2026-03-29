import os
from dotenv import load_dotenv
from .models import KPIResult
from services.erpnext import get_gl_entries

load_dotenv()

COST_ACCOUNTS = [os.getenv("COST_ACCOUNT")]


def calculate_cost(from_date, to_date):
    gl_entries = get_gl_entries(from_date, to_date, COST_ACCOUNTS)

    cost = sum(row["debit"] for row in gl_entries)

    return KPIResult(from_date=from_date, to_date=to_date, value=cost)