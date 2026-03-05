def get_invoices(from_date, to_date):
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
