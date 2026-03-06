# Finance Dashboard — KKU ERPNext Integration

**Team 6 — Financial Analytics**  
Stack: Avalonia (.NET 10) · FastAPI (Python 3.13) · ERPNext v16 (Docker)

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Design Concept](#2-design-concept)
3. [Project Structure](#3-project-structure)
4. [Prerequisites](#4-prerequisites)
5. [Running the System](#5-running-the-system)
6. [Environment Variables](#6-environment-variables)
7. [ERPNext DocTypes](#7-erpnext-doctypes)
8. [API Reference](#8-api-reference)
9. [KPI Engine](#9-kpi-engine)
10. [Budget Alert System](#10-budget-alert-system)
11. [Authentication](#11-authentication)
12. [Testing](#12-testing)
13. [Troubleshooting](#13-troubleshooting)
14. [Dependencies](#14-dependencies)

---

## 1. System Overview

This system is a financial analytics dashboard for KKU, built on top of ERPNext as the data source. It provides real-time KPI monitoring, invoice and payment tracking, cost center analysis, budget alerting, and CSV export.

The system has three independent layers that communicate in sequence:

```
Avalonia Desktop UI
        |
        | HTTP (JSON)
        v
FastAPI finance-service  (http://localhost:8000)
        |
        | HTTP + Token Auth
        v
ERPNext REST API  (http://localhost:8080)
        |
        v
MariaDB (via Docker)
```

| Layer | Technology | Role |
|---|---|---|
| Avalonia Desktop UI | C# / .NET 10 / Avalonia 11 | Desktop app for end users. Sends requests to FastAPI and renders data. |
| finance-service | Python 3.13 / FastAPI / uvicorn | Business logic layer. Computes KPIs, manages budget alerts, exposes REST endpoints. |
| ERPNext | Frappe Framework v16 / Docker / MariaDB | Source of truth. Stores all financial transactions. |

---

## 2. Design Concept

### 2.1 Architecture Flow

The system follows a strict unidirectional data flow. The UI layer never communicates with ERPNext directly. All data access goes through the FastAPI layer, which handles authentication, filtering, and computation.

```
User selects date range
        |
        v
Avalonia sends GET /kpi/summary?from_date=...&to_date=...
        |
        v
FastAPI calls ERPNext GET /api/resource/GL Entry (with filters)
        |
        v
ERPNext returns raw GL entries (JSON)
        |
        v
FastAPI aggregates: Revenue = sum(credit), Cost = sum(debit)
        |
        v
FastAPI returns { revenue, cost, profit, margin }
        |
        v
Avalonia renders KPI cards
```

The same pattern applies to all eight endpoints. FastAPI acts as a transformation layer: it receives raw ERPNext data, applies business logic, and returns structured responses to the UI.

### 2.2 Interface Design

The Avalonia dashboard uses a dark-themed layout with a fixed 220px sidebar and a content area that occupies the remaining width. Navigation is handled entirely in code-behind — clicking a sidebar button swaps the content of a `ContentControl` named `PageHost`.

The top bar contains a date range picker (From / To) and a Load Data button. When Load Data is clicked, the ViewModel fires all API calls concurrently using `Task.WhenAll` and updates all ObservableCollections simultaneously.

**Eight pages are available:**

| Page | Content |
|---|---|
| Dashboard | KPI cards (Revenue, Cost, Profit, Margin) with recent Invoice and Payment tables |
| KPI Summary | KPI values displayed individually with period context |
| Invoices | Full Sales Invoice table with all fields from ERPNext |
| Payments | Full Payment Entry table |
| GL Entries | General Ledger entries with debit and credit columns |
| Cost Center | Aggregated debit/credit/net breakdown by cost center |
| Budget Alerts | Budget configuration form and active alert list with severity colors |
| Export Report | Three download buttons for KPI, Invoices, and Payments as CSV files |

### 2.3 MVVM Pattern (Avalonia)

The UI follows the MVVM pattern using `CommunityToolkit.Mvvm`:

- `MainViewModel` — holds all observable properties and relay commands
- `MainWindow.axaml` — declares layout and data bindings
- `MainWindow.axaml.cs` — handles navigation and builds page controls in code
- `FinanceApiService` — HTTP client that calls FastAPI endpoints
- `Models/Models.cs` — C# classes matching FastAPI JSON response shapes

Properties decorated with `[ObservableProperty]` auto-generate `INotifyPropertyChanged` notifications. Methods decorated with `[RelayCommand]` auto-generate `ICommand` implementations. This removes all boilerplate binding code.

### 2.4 FastAPI Layer Design

Each endpoint in `main.py` follows the same pattern:

1. Accept `from_date` and `to_date` as query parameters
2. Call the appropriate service function (invoices, payments, GL entries)
3. Apply business logic or aggregation
4. Return a Pydantic model as JSON

All endpoints are synchronous functions wrapped with `run_in_threadpool` by FastAPI. CORS middleware is enabled to allow requests from any origin, which supports both the Avalonia app and the HTML dashboard.

---

## 3. Project Structure

```
ERPNext-finance-service/
├── finance-service/
│   ├── main.py                    All API endpoints and routing
│   ├── budget.py                  Budget alert logic and config persistence
│   ├── .env                       Environment variables (not committed)
│   ├── budget_config.json         Persisted budget targets (auto-created on first save)
│   ├── requirements.txt           Python dependencies
│   ├── test_kpi.py                Unit tests for KPI calculations
│   ├── kpi/
│   │   ├── models.py              KPI data models (dataclasses)
│   │   ├── revenue.py             Revenue = sum of GL credit in income accounts
│   │   ├── cost.py                Cost = sum of GL debit in expense accounts
│   │   ├── profit.py              Profit = Revenue - Cost
│   │   └── margin.py              Margin = (Profit / Revenue) * 100
│   └── services/
│       ├── erpnext.py             ERPNext HTTP client, auth headers, GL entry fetcher
│       ├── invoices.py            Sales Invoice fetcher
│       └── payments.py            Payment Entry fetcher
│
├── FinanceDashboard/
│   ├── FinanceDashboard.csproj    Project file and NuGet package references
│   ├── Program.cs                 Application entry point ([STAThread])
│   ├── App.axaml                  Application-level styles and DataGrid theme
│   ├── App.axaml.cs               App initialization, sets MainWindow DataContext
│   ├── Models/
│   │   └── Models.cs              C# models: KpiSummary, Invoice, Payment, GlEntry, etc.
│   ├── Services/
│   │   └── FinanceApiService.cs   HttpClient wrapper for all FastAPI endpoints
│   ├── ViewModels/
│   │   └── MainViewModel.cs       All observable properties and relay commands
│   └── Views/
│       ├── MainWindow.axaml       Window layout, sidebar, top bar, DatePicker, styles
│       └── MainWindow.axaml.cs    Page builder methods (BuildDashboard, BuildInvoices, etc.)
│
└── frappe_docker/
    └── pwd.yml                    Docker Compose file for ERPNext + MariaDB + Redis
```

---

## 4. Prerequisites

| Software | Minimum Version | Purpose |
|---|---|---|
| Docker Desktop | Latest | Runs ERPNext and its dependencies as containers |
| Python | 3.13 | Runs the FastAPI backend |
| .NET SDK | 10.0.103 | Builds and runs the Avalonia desktop app |

Verify installations:

```powershell
docker --version
python --version
dotnet --version
```

---

## 5. Running the System

All three components must be running simultaneously. Open three separate terminal windows.

### Terminal 1 — Start ERPNext

```powershell
cd ERPNext-finance-service\frappe_docker
docker compose -f pwd.yml up -d
```

Wait approximately 60 seconds for all services to become healthy, then verify:

```powershell
docker compose -f pwd.yml ps
```

All nine services should show status `Up`. Open `http://localhost:8080` and log in with `Administrator` / `admin`.

### Terminal 2 — Start FastAPI Backend

```powershell
cd ERPNext-finance-service\finance-service
uvicorn main:app --reload
```

The server starts at `http://127.0.0.1:8000`. Confirm by opening `http://127.0.0.1:8000/docs` in a browser, which shows the auto-generated Swagger UI for all endpoints.

### Terminal 3 — Start Avalonia Dashboard

```powershell
cd ERPNext-finance-service\FinanceDashboard
dotnet run
```

The first run downloads NuGet packages and may take 1–2 minutes. A desktop window titled **Finance Dashboard — KKU** will appear.

### Using the Dashboard

1. Set the **From** and **To** date range in the top bar
2. Click **Load Data**
3. Navigate between pages using the sidebar
4. Configure budget targets in the **Budget Alerts** page
5. Download CSV exports from the **Export Report** page

### Building a Standalone Executable

To produce a self-contained `.exe` that does not require .NET installed on the target machine:

```powershell
cd FinanceDashboard
dotnet publish -c Release -r win-x64 --self-contained true
```

Output is placed in `bin\Release\net10.0\win-x64\publish\`. The entire folder must be kept together.

---

## 6. Environment Variables

All configuration lives in `finance-service/.env`. This file is not committed to version control.

```env
FRAPPE_URL=http://localhost:8080
FRAPPE_API_KEY=your_api_key_here
FRAPPE_API_SECRET=your_api_secret_here
```

| Variable | Required | Description |
|---|---|---|
| `FRAPPE_URL` | Yes | Base URL of the ERPNext instance |
| `FRAPPE_API_KEY` | Yes | API Key generated from ERPNext user settings |
| `FRAPPE_API_SECRET` | Yes | API Secret generated from ERPNext user settings |

### Generating API Keys

1. Open `http://localhost:8080`
2. Log in as Administrator
3. Click the **Admin** user at the bottom-left corner
4. Select **My Profile**
5. Click the **Settings** tab
6. Scroll to **API Access** and click **Generate Keys**
7. Copy both values into `.env`

> The API Secret is shown only once. Store it securely immediately.

---

## 7. ERPNext DocTypes

The system reads from four ERPNext DocTypes. This section describes each DocType in full, including all fields used by this system and how to interact with them via the ERPNext REST API.

### 7.1 Sales Invoice

A Sales Invoice records a billing transaction issued to a customer. It must be **submitted** (`docstatus = 1`) for its values to appear in GL Entries and for it to affect financial reports.

**Path in ERPNext UI:** Selling > Sales Invoice

#### Fields Used

| Field | Type | Description |
|---|---|---|
| `name` | Link | Unique document ID, e.g. `SINV-0001`. Auto-generated on save. |
| `customer` | Link | Name of the Customer master record. |
| `posting_date` | Date | The date the invoice is effective. Used for date range filtering. |
| `grand_total` | Currency | Total invoice amount including taxes. |
| `outstanding_amount` | Currency | Amount remaining unpaid. Decreases as Payment Entries are applied. |
| `status` | Select | `Draft` / `Submitted` / `Paid` / `Return` / `Cancelled` |
| `docstatus` | Int | `0` = Draft, `1` = Submitted, `2` = Cancelled. Only `1` is read by this system. |
| `company` | Link | Company this invoice belongs to. Used to scope queries. |

#### Reading Sales Invoices

```
GET http://localhost:8080/api/resource/Sales Invoice
    ?filters=[
        ["posting_date",">=","2026-01-01"],
        ["posting_date","<=","2026-01-31"],
        ["docstatus","=",1]
      ]
    &fields=["name","customer","posting_date","grand_total","outstanding_amount","status"]
    &limit_page_length=1000
Authorization: token API_KEY:API_SECRET
```

#### Creating a Sales Invoice

```
POST http://localhost:8080/api/resource/Sales Invoice
Content-Type: application/json
Authorization: token API_KEY:API_SECRET

{
  "customer": "Customer Name",
  "posting_date": "2026-01-15",
  "company": "KKU",
  "items": [
    {
      "item_code": "Service Fee",
      "qty": 1,
      "rate": 50000
    }
  ]
}
```

After saving, call the Submit action:

```
POST http://localhost:8080/api/resource/Sales Invoice/SINV-0001/actions/submit
Authorization: token API_KEY:API_SECRET
```

Submitting a Sales Invoice automatically creates the corresponding GL Entries.

---

### 7.2 Payment Entry

A Payment Entry records the actual receipt of money from a customer (or disbursement to a supplier). It is linked to Sales Invoices through the Payment Entry Reference child table.

**Path in ERPNext UI:** Accounting > Payment Entry

#### Fields Used

| Field | Type | Description |
|---|---|---|
| `name` | Link | Unique document ID, e.g. `PE-0001`. |
| `party` | Dynamic Link | Name of the Customer or Supplier. |
| `party_type` | Select | `Customer` or `Supplier`. |
| `payment_type` | Select | `Receive` (from customer), `Pay` (to supplier), `Internal Transfer`. This system reads `Receive` only. |
| `posting_date` | Date | Date the payment was recorded. |
| `paid_amount` | Currency | Amount received or paid. |
| `mode_of_payment` | Link | `Cash` / `Bank Transfer` / `Cheque` etc. |
| `docstatus` | Int | `0` = Draft, `1` = Submitted. Only `1` is read. |

#### Reading Payment Entries

```
GET http://localhost:8080/api/resource/Payment Entry
    ?filters=[
        ["posting_date",">=","2026-01-01"],
        ["payment_type","=","Receive"],
        ["docstatus","=",1]
      ]
    &fields=["name","party","paid_amount","posting_date","mode_of_payment"]
    &limit_page_length=1000
Authorization: token API_KEY:API_SECRET
```

#### Creating a Payment Entry

```
POST http://localhost:8080/api/resource/Payment Entry
Content-Type: application/json
Authorization: token API_KEY:API_SECRET

{
  "payment_type": "Receive",
  "party_type": "Customer",
  "party": "Customer Name",
  "posting_date": "2026-01-20",
  "paid_amount": 50000,
  "received_amount": 50000,
  "mode_of_payment": "Bank Transfer",
  "paid_to": "Cash - KKU",
  "company": "KKU"
}
```

---

### 7.3 GL Entry

GL Entry (General Ledger Entry) is the core double-entry accounting record. Every submitted financial transaction in ERPNext — Sales Invoice, Payment Entry, Journal Entry — automatically generates one or more GL Entries. This DocType is the **primary data source for KPI calculation** in this system.

GL Entries are never created manually. They are always generated by submitting a parent document.

**Path in ERPNext UI:** Accounting > General Ledger (Report)

#### Fields Used

| Field | Type | Description |
|---|---|---|
| `name` | Link | Unique GL Entry ID. |
| `posting_date` | Date | Date of the originating transaction. |
| `account` | Link | Chart of Accounts entry, e.g. `Sales - KKU` or `Cost of Goods Sold - KKU`. |
| `debit` | Currency | Amount debited to this account. Represents outflows or expenses. |
| `credit` | Currency | Amount credited to this account. Represents inflows or income. |
| `voucher_no` | Dynamic Link | ID of the source document, e.g. `SINV-0001`. |
| `voucher_type` | Select | `Sales Invoice` / `Payment Entry` / `Journal Entry` etc. |
| `cost_center` | Link | Cost center this entry is assigned to. |
| `company` | Link | Company this entry belongs to. |
| `docstatus` | Int | GL Entries are always `1` (submitted). They cannot be drafted. |

#### Reading GL Entries (Revenue Accounts)

```
GET http://localhost:8080/api/resource/GL Entry
    ?filters=[
        ["posting_date",">=","2026-01-01"],
        ["posting_date","<=","2026-01-31"],
        ["docstatus","=",1],
        ["company","=","KKU"],
        ["account","in",["Sales - KKU"]]
      ]
    &fields=["account","debit","credit","posting_date","voucher_no","cost_center"]
    &limit_page_length=1000
Authorization: token API_KEY:API_SECRET
```

#### Reading GL Entries (Expense Accounts)

```
GET http://localhost:8080/api/resource/GL Entry
    ?filters=[
        ["posting_date",">=","2026-01-01"],
        ["posting_date","<=","2026-01-31"],
        ["docstatus","=",1],
        ["company","=","KKU"],
        ["account","in",["Cost of Goods Sold - KKU"]]
      ]
    &fields=["account","debit","credit","posting_date","voucher_no","cost_center"]
    &limit_page_length=1000
Authorization: token API_KEY:API_SECRET
```

> GL Entries cannot be created via the API directly. They are always the result of submitting a parent document (Sales Invoice, Payment Entry, etc.).

---

### 7.4 Cost Center

Cost Center is a master record that defines organizational or departmental units. GL Entries are assigned to Cost Centers at the time of transaction, enabling cost-by-department analysis.

**Path in ERPNext UI:** Accounting > Chart of Cost Centers

#### Fields Used

| Field | Type | Description |
|---|---|---|
| `cost_center_name` | Data | Human-readable display name. |
| `name` | Link | Unique ID, typically `Cost Center Name - Company`. |
| `parent_cost_center` | Link | Parent node for hierarchical reporting. |
| `is_group` | Check | `1` if this is a group node, `0` if it is a leaf (actual cost center). |
| `company` | Link | Company this cost center belongs to. |

#### Reading Cost Centers

```
GET http://localhost:8080/api/resource/Cost Center
    ?filters=[["company","=","KKU"],["is_group","=",0]]
    &fields=["cost_center_name","name","parent_cost_center","is_group"]
    &limit_page_length=500
Authorization: token API_KEY:API_SECRET
```

#### Cost Center Breakdown (from GL Entries)

The cost center analysis page in this system does not query the Cost Center DocType directly. Instead, it queries GL Entries and groups the results by `cost_center`, summing debit and credit per center:

```python
# services/erpnext.py pattern
entries = get_gl_entries(from_date, to_date)
breakdown = {}
for e in entries:
    cc = e.get("cost_center", "Unassigned")
    breakdown[cc]["debit"] += e.get("debit", 0)
    breakdown[cc]["credit"] += e.get("credit", 0)
    breakdown[cc]["net"] = breakdown[cc]["credit"] - breakdown[cc]["debit"]
```

#### Creating a Cost Center

```
POST http://localhost:8080/api/resource/Cost Center
Content-Type: application/json
Authorization: token API_KEY:API_SECRET

{
  "cost_center_name": "Research Department",
  "parent_cost_center": "Main - KKU",
  "company": "KKU",
  "is_group": 0
}
```

---

## 8. API Reference

All endpoints accept `from_date` and `to_date` as query parameters in `YYYY-MM-DD` format unless otherwise noted. All responses are JSON.

Base URL: `http://localhost:8000`

### GET /kpi/summary

Returns the four primary KPIs for the given period.

**Query parameters:** `from_date`, `to_date`

**Response:**
```json
{
  "revenue": 80000.0,
  "cost": 30000.0,
  "profit": 50000.0,
  "margin": 62.5
}
```

### GET /invoices

Returns all submitted Sales Invoices within the date range.

**Response:** Array of invoice objects with fields `name`, `customer`, `grand_total`, `outstanding_amount`, `posting_date`, `status`.

### GET /payments

Returns all submitted Payment Entries of type `Receive` within the date range.

**Response:** Array of payment objects with fields `name`, `party`, `paid_amount`, `posting_date`, `mode_of_payment`.

### GET /gl-entries

Returns all GL Entries within the date range.

**Response:** Array of GL entry objects with fields `posting_date`, `account`, `voucher_no`, `debit`, `credit`.

### GET /cost-center

Returns aggregated cost/revenue breakdown grouped by cost center.

**Response:** Array of objects with fields `cost_center_name`, `debit`, `credit`, `net`.

### GET /budget/config

Returns the current budget configuration targets.

**Response:**
```json
{
  "revenue_target": 100000.0,
  "cost_limit": 50000.0,
  "profit_target": 40000.0,
  "margin_min": 30.0
}
```

### POST /budget/config

Saves new budget targets. Persisted to `budget_config.json`.

**Request body:** Same structure as GET response.

### GET /budget/alerts

Compares actual KPIs against budget targets and returns alert list.

**Response:**
```json
{
  "kpi": { "revenue": 80000, "cost": 30000, "profit": 50000, "margin": 62.5 },
  "budget": { "revenue_target": 100000, "cost_limit": 50000, ... },
  "alerts": [
    { "level": "danger", "type": "revenue", "message": "Revenue 80,000 is below target 100,000" }
  ]
}
```

### GET /export/kpi

Downloads KPI summary as a CSV file attachment.

### GET /export/invoices

Downloads invoice list as a CSV file attachment.

### GET /export/payments

Downloads payment list as a CSV file attachment.

---

## 9. KPI Engine

The KPI engine lives in `finance-service/kpi/`. Each file contains a single calculation function.

### Revenue (`kpi/revenue.py`)

```
Revenue = sum(credit) for all GL Entries where:
  - account IN ["Sales - KKU"]
  - posting_date BETWEEN from_date AND to_date
  - docstatus = 1
  - company = "KKU"
```

### Cost (`kpi/cost.py`)

```
Cost = sum(debit) for all GL Entries where:
  - account IN ["Cost of Goods Sold - KKU"]
  - posting_date BETWEEN from_date AND to_date
  - docstatus = 1
  - company = "KKU"
```

### Profit (`kpi/profit.py`)

```
Profit = Revenue - Cost
```

### Margin (`kpi/margin.py`)

```
Margin = (Profit / Revenue) * 100   if Revenue > 0
Margin = 0.0                         if Revenue = 0
```

### Adapting for Different Account Names

If your ERPNext Chart of Accounts uses different account names, update the constants in `services/erpnext.py`:

```python
INCOME_ACCOUNTS = ["Sales - KKU"]          # Change to match your accounts
EXPENSE_ACCOUNTS = ["Cost of Goods Sold - KKU"]
COMPANY = "KKU"                             # Change to your company name
```

---

## 10. Budget Alert System

Budget configuration is stored in `finance-service/budget_config.json`. This file is created automatically when the user saves budget targets for the first time through the UI. If the file does not exist, default values of zero are used.

### Alert Logic (`budget.py`)

```python
def check_alerts(kpi: KpiSummary, budget: BudgetConfig) -> list[BudgetAlert]:
    alerts = []
    if budget.revenue_target > 0 and kpi.revenue < budget.revenue_target:
        alerts.append(BudgetAlert(level="danger", type="revenue",
            message=f"Revenue {kpi.revenue:,.0f} is below target {budget.revenue_target:,.0f}"))
    if budget.cost_limit > 0 and kpi.cost > budget.cost_limit:
        alerts.append(BudgetAlert(level="danger", type="cost",
            message=f"Cost {kpi.cost:,.0f} exceeds limit {budget.cost_limit:,.0f}"))
    if budget.profit_target > 0 and kpi.profit < budget.profit_target:
        alerts.append(BudgetAlert(level="danger", type="profit",
            message=f"Profit {kpi.profit:,.0f} is below target {budget.profit_target:,.0f}"))
    if budget.margin_min > 0 and kpi.margin < budget.margin_min:
        alerts.append(BudgetAlert(level="warning", type="margin",
            message=f"Margin {kpi.margin:.1f}% is below minimum {budget.margin_min:.1f}%"))
    return alerts
```

### Alert Levels

| Level | Color in UI | Meaning |
|---|---|---|
| `ok` | Green | All targets met |
| `warning` | Yellow | Margin below minimum |
| `danger` | Red | Revenue, cost, or profit threshold breached |

---

## 11. Authentication

All requests from `finance-service` to ERPNext use token-based authentication. The `Authorization` header format is:

```
Authorization: token API_KEY:API_SECRET
```

This is constructed in `services/erpnext.py` using values from `.env`:

```python
import os
from dotenv import load_dotenv

load_dotenv()
FRAPPE_URL = os.getenv("FRAPPE_URL")
API_KEY = os.getenv("FRAPPE_API_KEY")
API_SECRET = os.getenv("FRAPPE_API_SECRET")

HEADERS = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json"
}
```

All HTTP calls to ERPNext include `headers=HEADERS`. No session cookies or OAuth flows are used.

---

## 12. Testing

### Test FastAPI Endpoints Directly

With `uvicorn` running, open the following URLs in a browser:

```
http://localhost:8000/kpi/summary?from_date=2026-01-01&to_date=2026-01-31
http://localhost:8000/invoices?from_date=2026-01-01&to_date=2026-01-31
http://localhost:8000/payments?from_date=2026-01-01&to_date=2026-01-31
http://localhost:8000/gl-entries?from_date=2026-01-01&to_date=2026-01-31
http://localhost:8000/cost-center?from_date=2026-01-01&to_date=2026-01-31
http://localhost:8000/budget/alerts?from_date=2026-01-01&to_date=2026-01-31
```

The Swagger UI at `http://localhost:8000/docs` allows interactive testing of all endpoints.

### Create Test Data in ERPNext

To verify the full data pipeline from ERPNext to the Avalonia UI:

1. Open `http://localhost:8080` and navigate to **Selling**
2. Go to **Customer** and create a new customer if none exists
3. Go to **Sales Invoice** and click **New**
4. Select the customer, add an item with a rate (e.g., 100,000), and click **Save**
5. Click **Submit** to post the invoice and generate GL Entries
6. In the Avalonia app, set a date range that includes today and click **Load Data**
7. The invoice should appear in the Invoices page and the Revenue KPI should reflect the new amount

### Run Python Unit Tests

```powershell
cd finance-service
python test_kpi.py
```

---

## 13. Troubleshooting

| Symptom | Cause | Resolution |
|---|---|---|
| `dotnet` is not recognized | .NET SDK not installed or PATH not updated after install | Install .NET 10 SDK from microsoft.com/dotnet, close all terminals and reopen |
| `No module named 'budget'` | `budget.py` missing from `finance-service/` root | Copy `budget.py` into the `finance-service/` directory alongside `main.py` |
| `422 Unprocessable Content` on Load Data | Date format sent to API is invalid | Ensure `DateTimeOffset?` is used in `MainViewModel.cs` for `FromDate` and `ToDate` |
| `500 Connection refused` to `localhost:8080` | ERPNext Docker containers are not running | Run `docker compose -f pwd.yml up -d` and wait 60 seconds |
| All KPI values show zero | `USE_MOCK` flag is `True` in `erpnext.py` | Set `USE_MOCK = False` in `services/erpnext.py` |
| Data shows mock values (บริษัท A, บริษัท B) | `USE_MOCK` still active | Confirm `.env` has correct `FRAPPE_URL` and `USE_MOCK = False` |
| `App.axaml AVLN1001` XAML error | `App.axaml` contains wrong content (e.g., csproj was pasted) | Recreate `App.axaml` with correct Avalonia XML starting with `<?xml version="1.0"` |
| `DataGrid` type not found | Missing `Avalonia.Controls.DataGrid` NuGet package | Confirm `FinanceDashboard.csproj` includes the DataGrid package reference and `App.axaml` includes the DataGrid style |
| `GetVisualDescendants` not found | Missing `using Avalonia.VisualTree;` | Add `using Avalonia.VisualTree;` to `MainWindow.axaml.cs` |
| Not permitted on `/app/user/Administrator` | ERPNext permission restriction on Administrator record | Navigate to `/app/user/admin@example.com` instead |
| Docker `open //./pipe/dockerDesktopLinuxEngine` error | Docker Desktop is not running | Open Docker Desktop from the Start menu and wait for the status icon to turn green |

---

## 14. Dependencies

### Avalonia — `FinanceDashboard.csproj`

| Package | Version | Purpose |
|---|---|---|
| `Avalonia` | 11.2.1 | Core cross-platform UI framework |
| `Avalonia.Desktop` | 11.2.1 | Desktop application lifecycle |
| `Avalonia.Themes.Fluent` | 11.2.1 | Fluent design system theme |
| `Avalonia.Fonts.Inter` | 11.2.1 | Inter font family |
| `Avalonia.Controls.DataGrid` | 11.2.1 | DataGrid control for tabular data display |
| `Avalonia.ReactiveUI` | 11.2.1 | ReactiveUI integration |
| `CommunityToolkit.Mvvm` | 8.3.2 | Source generators for ObservableProperty and RelayCommand |

### Python — `finance-service/requirements.txt`

| Package | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `requests` | HTTP client for ERPNext REST API calls |
| `python-dotenv` | Loads `.env` configuration into `os.environ` |
| `pydantic` | Request and response data validation |

---

## Docker Services (frappe_docker/pwd.yml)

| Service | Image | Purpose |
|---|---|---|
| `frontend` | `frappe/erpnext:v16.8.1` | Nginx reverse proxy, exposed on port 8080 |
| `backend` | `frappe/erpnext:v16.8.1` | Frappe/ERPNext application server |
| `db` | `mariadb:10.6` | Database for all ERPNext data |
| `redis-cache` | `redis:6.2-alpine` | Caching layer |
| `redis-queue` | `redis:6.2-alpine` | Background job queue |
| `queue-short` | `frappe/erpnext:v16.8.1` | Short background job worker |
| `queue-long` | `frappe/erpnext:v16.8.1` | Long background job worker |
| `scheduler` | `frappe/erpnext:v16.8.1` | Scheduled task runner |
| `websocket` | `frappe/erpnext:v16.8.1` | Real-time websocket server |

---

*Finance Dashboard — Team 6 — KKU ERPNext Integration Project*