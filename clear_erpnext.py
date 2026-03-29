"""
clear_erpnext.py — ล้างข้อมูลทดสอบออกจาก ERPNext
ลำดับการลบ: Payment Entry → Sales Invoice → Customer
(GL Entry จะหายไปเองเมื่อ Cancel Invoice)

ใช้งาน:
    python clear_erpnext.py
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv("finance-service/.env")

BASE_URL = os.getenv("FRAPPE_URL", "http://localhost:8080")
API_KEY = os.getenv("FRAPPE_API_KEY")
API_SECRET = os.getenv("FRAPPE_API_SECRET")
COMPANY = os.getenv("COMPANY", "KKU")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"token {API_KEY}:{API_SECRET}",
}

CUSTOMERS_TO_DELETE = ["Customer A", "Customer B", "Customer C"]

# ============================================================
# Helper functions
# ============================================================

def get_list(doctype: str, filters: list, fields: list) -> list:
    url = f"{BASE_URL}/api/resource/{doctype}"
    resp = requests.get(
        url,
        headers=HEADERS,
        params={
            "filters": json.dumps(filters),
            "fields": json.dumps(fields),
            "limit_page_length": 500,
            "ignore_permissions": 1,
        },
        timeout=30,
    )
    if resp.status_code == 200:
        return resp.json().get("data", [])
    return []


def cancel_doc(doctype: str, name: str) -> bool:
    """Cancel document ผ่าน frappe.client.cancel"""
    url = f"{BASE_URL}/api/method/frappe.client.cancel"
    resp = requests.post(
        url,
        headers=HEADERS,
        json={"doctype": doctype, "name": name},
        timeout=30,
    )
    if resp.status_code == 200:
        return True
    print(f"  [ERROR] Cancel {doctype}/{name}: {resp.status_code} {resp.text[:200]}")
    return False


def delete_doc(doctype: str, name: str) -> bool:
    """ลบ document ผ่าน frappe.client.delete"""
    url = f"{BASE_URL}/api/method/frappe.client.delete"
    resp = requests.post(
        url,
        headers=HEADERS,
        json={"doctype": doctype, "name": name},
        timeout=30,
    )
    if resp.status_code == 200:
        return True
    print(f"  [ERROR] Delete {doctype}/{name}: {resp.status_code} {resp.text[:200]}")
    return False


def cancel_and_delete(doctype: str, filters: list):
    """Cancel แล้ว Delete ทุก document ที่ตรง filter"""
    docs = get_list(doctype, filters, ["name", "docstatus"])
    if not docs:
        print(f"  ไม่พบ {doctype} ที่ต้องลบ")
        return

    for doc in docs:
        name = doc["name"]
        docstatus = doc.get("docstatus", 0)

        # Cancel ก่อนถ้ายัง submitted อยู่
        if docstatus == 1:
            ok = cancel_doc(doctype, name)
            if not ok:
                print(f"  ⚠ ข้าม {name} (cancel ไม่สำเร็จ)")
                continue
            print(f"  ✓ cancelled | {name}")

        # Delete (ทั้ง draft=0 และ cancelled=2)
        ok = delete_doc(doctype, name)
        if ok:
            print(f"  ✓ deleted   | {name}")


# ============================================================
# Step 1: Cancel + Delete Payment Entry
# ============================================================

def clear_payments():
    print("\n[1] ล้าง Payment Entry...")
    cancel_and_delete("Payment Entry", [
        ["party_type", "=", "Customer"],
        ["company", "=", COMPANY],
    ])


# ============================================================
# Step 2: Cancel + Delete Sales Invoice
# ============================================================

def clear_invoices():
    print("\n[2] ล้าง Sales Invoice...")
    cancel_and_delete("Sales Invoice", [
        ["company", "=", COMPANY],
    ])


# ============================================================
# Step 3: Delete Customer
# ============================================================

def clear_customers():
    print("\n[3] ล้าง Customer...")
    for name in CUSTOMERS_TO_DELETE:
        existing = get_list("Customer", [["name", "=", name]], ["name"])
        if not existing:
            print(f"  ไม่พบ Customer '{name}'")
            continue
        ok = delete_doc("Customer", name)
        if ok:
            print(f"  ✓ deleted   | {name}")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  ERPNext Clear Script — Finance Dashboard KKU")
    print("=" * 60)
    print(f"\nเชื่อมต่อไปที่ : {BASE_URL}")
    print(f"Company        : {COMPANY}")
    print(f"จะลบ Customer  : {', '.join(CUSTOMERS_TO_DELETE)}")
    print("\n⚠  การลบนี้ไม่สามารถย้อนกลับได้!")
    confirm = input("พิมพ์ 'yes' เพื่อยืนยัน: ").strip().lower()
    if confirm != "yes":
        print("ยกเลิกแล้ว")
        exit(0)

    clear_payments()
    clear_invoices()
    clear_customers()

    print("\n" + "=" * 60)
    print("  ล้างข้อมูลเสร็จสิ้น! รัน seed_erpnext.py เพื่อเริ่มใหม่")
    print("=" * 60)