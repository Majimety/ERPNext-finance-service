def get_payments(from_date, to_date):
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
                ["name", "party", "paid_amount", "posting_date", "mode_of_payment"]
            ),
            "limit_page_length": 1000,
        },
    )
    res.raise_for_status()
    return res.json().get("data", [])
