import os, requests, json
from dotenv import load_dotenv

load_dotenv()

FRAPPE_URL = os.getenv("FRAPPE_URL")

# USE_MOCK = not FRAPPE_URL or "localhost" in FRAPPE_URL
USE_MOCK = False

MOCK_PAYMENTS = [
    {
        "name": "PE-0001",
        "party": "บริษัท A",
        "paid_amount": 50000,
        "posting_date": "2026-01-12",
        "mode_of_payment": "Bank Transfer",
        "payment_type": "Receive",
    },
]


def get_payments(from_date, to_date):
    if USE_MOCK:
        return [
            r
            for r in MOCK_PAYMENTS
            if str(from_date) <= r["posting_date"] <= str(to_date)
        ]

    HEADERS = {
        "Authorization": f"token {os.getenv('FRAPPE_API_KEY')}:{os.getenv('FRAPPE_API_SECRET')}"
    }
    res = requests.get(
        f"{FRAPPE_URL}/api/resource/Payment Entry",
        headers=HEADERS,
        params={
            "filters": json.dumps(
                [
                    ["posting_date", ">=", str(from_date)],
                    ["posting_date", "<=", str(to_date)],
                    ["docstatus", "=", 1],
                    ["payment_type", "=", "Receive"],
                ]
            ),
            "fields": json.dumps(
                [
                    "name",
                    "party",
                    "paid_amount",
                    "posting_date",
                    "mode_of_payment",
                    "payment_type",
                ]
            ),
            "limit_page_length": 1000,
        },
    )
    res.raise_for_status()
    return res.json().get("data", [])
