import os
from dotenv import load_dotenv

load_dotenv()

FRAPPE_URL = os.getenv("FRAPPE_URL")
COMPANY = os.getenv("COMPANY", "KKU")
INCOME_ACCOUNT = os.getenv("INCOME_ACCOUNT", "Sales - KKU")
COST_ACCOUNT = os.getenv("COST_ACCOUNT", "Cost of Goods Sold - KKU")

# USE_MOCK = not FRAPPE_URL or "localhost" in FRAPPE_URL
USE_MOCK = False

MOCK_DATA = [
    {
        "account": INCOME_ACCOUNT,
        "debit": 0,
        "credit": 50000,
        "posting_date": "2026-01-10",
        "voucher_no": "SINV-0001",
    },
    {
        "account": INCOME_ACCOUNT,
        "debit": 0,
        "credit": 30000,
        "posting_date": "2026-01-20",
        "voucher_no": "SINV-0002",
    },
    {
        "account": COST_ACCOUNT,
        "debit": 20000,
        "credit": 0,
        "posting_date": "2026-01-10",
        "voucher_no": "COGS-0001",
    },
    {
        "account": "Expenses - KKU",
        "debit": 10000,
        "credit": 0,
        "posting_date": "2026-01-15",
        "voucher_no": "EXP-0001",
    },
]


def get_gl_entries(from_date, to_date, accounts=None):
    if USE_MOCK:
        print("⚠️  Using MOCK data (ERPNext not connected)")
        result = []
        for row in MOCK_DATA:
            if accounts and row["account"] not in accounts:
                continue
            if str(from_date) <= row["posting_date"] <= str(to_date):
                result.append(row)
        return result

    import requests, json

    HEADERS = {
        "Authorization": f"token {os.getenv('FRAPPE_API_KEY')}:{os.getenv('FRAPPE_API_SECRET')}"
    }
    filters = [
        ["posting_date", ">=", str(from_date)],
        ["posting_date", "<=", str(to_date)],
        ["docstatus", "=", 1],
        ["company", "=", COMPANY],
    ]
    if accounts:
        filters.append(["account", "in", accounts])

    res = requests.get(
        f"{FRAPPE_URL}/api/resource/GL Entry",
        headers=HEADERS,
        params={
            "filters": json.dumps(filters),
            "fields": json.dumps(
                ["account", "debit", "credit", "posting_date", "voucher_no"]
            ),
            "limit_page_length": 1000,
        },
    )
    res.raise_for_status()
    return res.json().get("data", [])