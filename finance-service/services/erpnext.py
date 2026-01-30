import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

FRAPPE_URL = os.getenv("FRAPPE_URL")
print("FRAPPE_URL =", FRAPPE_URL)

HEADERS = {
    "Authorization": f"token {os.getenv('FRAPPE_API_KEY')}:{os.getenv('FRAPPE_API_SECRET')}"
}


def get_gl_entries(from_date, to_date, accounts=None):
    filters = [
        ["posting_date", ">=", str(from_date)],
        ["posting_date", "<=", str(to_date)],
        ["docstatus", "=", 1],
        ["company", "=", "KKU"],
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

    print("STATUS:", res.status_code)
    print("RESPONSE:", res.text)

    res.raise_for_status()
    return res.json().get("data", [])
