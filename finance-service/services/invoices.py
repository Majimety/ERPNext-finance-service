import os, requests, json
from dotenv import load_dotenv

load_dotenv()

FRAPPE_URL = os.getenv("FRAPPE_URL")

# USE_MOCK = not FRAPPE_URL or "localhost" in FRAPPE_URL
USE_MOCK = False

MOCK_INVOICES = [
    {
        "name": "SINV-0001",
        "customer": "บริษัท A",
        "grand_total": 50000,
        "outstanding_amount": 0,
        "posting_date": "2026-01-10",
        "status": "Paid",
    },
    {
        "name": "SINV-0002",
        "customer": "บริษัท B",
        "grand_total": 30000,
        "outstanding_amount": 30000,
        "posting_date": "2026-01-20",
        "status": "Unpaid",
    },
]


def get_invoices(from_date, to_date):
    if USE_MOCK:
        return [
            r
            for r in MOCK_INVOICES
            if str(from_date) <= r["posting_date"] <= str(to_date)
        ]

    HEADERS = {
        "Authorization": f"token {os.getenv('FRAPPE_API_KEY')}:{os.getenv('FRAPPE_API_SECRET')}"
    }
    res = requests.get(
        f"{FRAPPE_URL}/api/resource/Sales Invoice",
        headers=HEADERS,
        params={
            "filters": json.dumps(
                [
                    ["posting_date", ">=", str(from_date)],
                    ["posting_date", "<=", str(to_date)],
                    ["docstatus", "=", 1],
                ]
            ),
            "fields": json.dumps(
                [
                    "name",
                    "customer",
                    "grand_total",
                    "outstanding_amount",
                    "posting_date",
                    "status",
                ]
            ),
            "limit_page_length": 1000,
        },
    )
    res.raise_for_status()
    return res.json().get("data", [])
