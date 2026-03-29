"""
seed_erpnext.py — สร้างข้อมูลทดสอบเข้า ERPNext สำหรับ Finance Dashboard
ใช้งาน:
    pip install requests python-dotenv
    python seed_erpnext.py
ตัวแปรสิ่งแวดล้อม (ใน .env หรือ export ก่อนรัน):
    FRAPPE_URL=http://localhost:8080
    FRAPPE_API_KEY=<your_api_key>
    FRAPPE_API_SECRET=<your_api_secret>
"""

import os
import json
import requests
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv("finance-service/.env")

BASE_URL = os.getenv("FRAPPE_URL", "http://localhost:8080")
API_KEY = os.getenv("FRAPPE_API_KEY")
API_SECRET = os.getenv("FRAPPE_API_SECRET")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"token {API_KEY}:{API_SECRET}",
}

COMPANY = os.getenv("COMPANY", "KKU")
DEBTORS_ACCOUNT = os.getenv("DEBTORS_ACCOUNT", "Debtors - KKU")
CASH_ACCOUNT = os.getenv("CASH_ACCOUNT", "Cash - KKU")
COST_CENTER_ROOT = os.getenv("COST_CENTER_ROOT", "KKU - K")

# ============================================================
# ข้อมูลทดสอบ
# ============================================================

CUSTOMERS = [
    "Customer A",
    "Customer B",
    "Customer C",
]

ITEMS = [
    {"item_code": "Service Fee", "rate": 50000},
    {"item_code": "Consulting Fee", "rate": 75000},
    {"item_code": "License Fee", "rate": 30000},
]

COST_CENTERS = [
    "IT Department",
    "HR Department",
    "Finance Department",
]

INVOICE_DATA = [
    # (customer, item_index, qty, วันย้อนหลัง, cost_center_index)
    ("Customer A", 0, 1, 5,  0),
    ("Customer B", 1, 2, 10, 1),
    ("Customer C", 2, 3, 15, 2),
    ("Customer A", 1, 1, 20, 0),
    ("Customer B", 0, 2, 25, 1),
    ("Customer C", 1, 1, 30, 2),
    ("Customer A", 2, 2, 35, 0),
    ("Customer B", 2, 1, 40, 1),
]

# ============================================================
# Helper functions
# ============================================================

def post(doctype: str, data: dict) -> dict:
    url = f"{BASE_URL}/api/resource/{doctype}"
    resp = requests.post(url, headers=HEADERS, json=data, timeout=30)
    if resp.status_code not in (200, 201):
        print(f"  [ERROR] POST {doctype}: {resp.status_code} {resp.text[:200]}")
        return {}
    return resp.json().get("data", {})


def submit_doc(doctype: str, name: str) -> bool:
    url = f"{BASE_URL}/api/resource/{doctype}/{name}"
    resp = requests.put(url, headers=HEADERS, json={"docstatus": 1}, timeout=30)
    if resp.status_code == 200:
        return True
    print(f"  [ERROR] Submit {doctype}/{name}: {resp.status_code} {resp.text[:200]}")
    return False


def get_list(doctype: str, filters: list, fields: list) -> list:
    url = f"{BASE_URL}/api/resource/{doctype}"
    resp = requests.get(
        url,
        headers=HEADERS,
        params={
            "filters": json.dumps(filters),
            "fields": json.dumps(fields),
            "limit_page_length": 100,
        },
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json().get("data", [])
    return []


# ============================================================
# Step 1: ตรวจสอบ / สร้าง Customer
# ============================================================

def ensure_customers():
    print("\n[1] ตรวจสอบ Customer...")
    for name in CUSTOMERS:
        existing = get_list("Customer", [["customer_name", "=", name]], ["name"])
        if existing:
            print(f"  ✓ Customer '{name}' มีอยู่แล้ว")
            continue
        result = post("Customer", {
            "customer_name": name,
            "customer_type": "Company",
            "customer_group": "Commercial",
            "territory": "All Territories",
        })
        if result.get("name"):
            print(f"  + สร้าง Customer '{name}' สำเร็จ → {result['name']}")
        else:
            print(f"  ! สร้าง Customer '{name}' ไม่สำเร็จ")


# ============================================================
# Step 2: ตรวจสอบ / สร้าง Cost Center
# ============================================================

def ensure_cost_centers():
    print("\n[2] ตรวจสอบ Cost Center...")
    created = []
    for cc_name in COST_CENTERS:
        full_name = f"{cc_name} - K"
        existing = get_list("Cost Center", [["name", "=", full_name]], ["name"])
        if existing:
            print(f"  ✓ Cost Center '{full_name}' มีอยู่แล้ว")
            created.append(full_name)
            continue
        result = post("Cost Center", {
            "cost_center_name": cc_name,
            "parent_cost_center": COST_CENTER_ROOT,
            "company": COMPANY,
            "is_group": 0,
        })
        name = result.get("name")
        if name:
            print(f"  + สร้าง Cost Center '{name}' สำเร็จ")
            created.append(name)
        else:
            print(f"  ! สร้าง Cost Center '{cc_name}' ไม่สำเร็จ — ใช้ root แทน")
            created.append(COST_CENTER_ROOT)
    return created


# ============================================================
# Step 3: สร้าง Sales Invoice ผูกกับ Cost Center
# ============================================================

def create_invoices(cost_centers: list):
    print("\n[3] สร้าง Sales Invoice...")
    created = []
    today = date.today()
    for customer, item_idx, qty, days_ago, cc_idx in INVOICE_DATA:
        posting_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        item = ITEMS[item_idx]
        cc = cost_centers[cc_idx] if cc_idx < len(cost_centers) else COST_CENTER_ROOT
        doc = post("Sales Invoice", {
            "customer": customer,
            "company": COMPANY,
            "posting_date": posting_date,
            "due_date": today.strftime("%Y-%m-%d"),
            "cost_center": cc,
            "items": [{
                "item_code": item["item_code"],
                "qty": qty,
                "rate": item["rate"],
                "cost_center": cc,
            }],
        })
        name = doc.get("name")
        if not name:
            print(f"  ! สร้าง Invoice สำหรับ {customer} ไม่สำเร็จ")
            continue

        ok = submit_doc("Sales Invoice", name)
        status = "✓ submitted" if ok else "⚠ draft (submit failed)"
        total = item["rate"] * qty
        print(f"  {status} | {name} | {customer} | {cc} | ฿{total:,.0f}")
        if ok:
            created.append(name)
    return created


# ============================================================
# Step 4: สร้าง Payment Entry
# ============================================================

def create_payments(invoice_names: list):
    print("\n[4] สร้าง Payment Entry...")
    if not invoice_names:
        print("  ! ไม่มี invoice ที่ submit สำเร็จ — ข้าม Payment step")
        return

    for name in invoice_names[:4]:
        inv_data = get_list(
            "Sales Invoice",
            [["name", "=", name]],
            ["name", "customer", "grand_total", "posting_date", "company"],
        )
        if not inv_data:
            continue
        inv = inv_data[0]

        doc = post("Payment Entry", {
            "payment_type": "Receive",
            "party_type": "Customer",
            "party": inv["customer"],
            "company": inv["company"],
            "posting_date": inv["posting_date"],
            "paid_amount": inv["grand_total"],
            "received_amount": inv["grand_total"],
            "paid_from": DEBTORS_ACCOUNT,
            "paid_to": CASH_ACCOUNT,
            "references": [{
                "reference_doctype": "Sales Invoice",
                "reference_name": name,
                "allocated_amount": inv["grand_total"],
            }],
        })
        pe_name = doc.get("name")
        if not pe_name:
            print(f"  ! สร้าง Payment สำหรับ {name} ไม่สำเร็จ")
            continue
        ok = submit_doc("Payment Entry", pe_name)
        status = "✓ submitted" if ok else "⚠ draft"
        print(f"  {status} | {pe_name} | {inv['customer']} | ฿{inv['grand_total']:,.0f}")


# ============================================================
# Step 5: ตรวจสอบ GL Entries
# ============================================================

def verify_gl_entries():
    print("\n[5] ตรวจสอบ GL Entries...")
    today = date.today()
    from_date = (today - timedelta(days=45)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    entries = get_list(
        "GL Entry",
        [
            ["posting_date", ">=", from_date],
            ["posting_date", "<=", to_date],
            ["company", "=", COMPANY],
        ],
        ["account", "debit", "credit", "posting_date", "voucher_no", "cost_center"],
    )
    total_revenue = sum(e.get("credit", 0) for e in entries)
    total_cost = sum(e.get("debit", 0) for e in entries)

    print(f"  GL Entries ทั้งหมด : {len(entries)} รายการ")
    print(f"  Credit (revenue)   : ฿{total_revenue:,.0f}")
    print(f"  Debit  (cost/cash) : ฿{total_cost:,.0f}")

    if entries:
        print("\n  ตัวอย่าง GL Entries (5 รายการแรก):")
        for e in entries[:5]:
            cc = e.get("cost_center", "-")
            print(f"    {e['posting_date']} | {e['voucher_no'][:18]:<18} | "
                  f"debit: ฿{e['debit']:>8,.0f} | credit: ฿{e['credit']:>8,.0f} | {cc}")
    else:
        print("  ⚠ ไม่พบ GL Entries")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  ERPNext Seed Script — Finance Dashboard KKU")
    print("=" * 60)

    if not API_KEY or not API_SECRET:
        print("\n[ERROR] ไม่พบ FRAPPE_API_KEY หรือ FRAPPE_API_SECRET")
        print("  → ตรวจสอบ finance-service/.env")
        exit(1)

    print(f"\nเชื่อมต่อไปที่  : {BASE_URL}")
    print(f"Company         : {COMPANY}")
    print(f"Cost Center root: {COST_CENTER_ROOT}")

    ensure_customers()
    cost_centers = ensure_cost_centers()
    invoice_names = create_invoices(cost_centers)
    create_payments(invoice_names)
    verify_gl_entries()

    print("\n" + "=" * 60)
    print("  เสร็จสิ้น! เปิด Finance Dashboard แล้วกด Load Data")
    print("=" * 60)