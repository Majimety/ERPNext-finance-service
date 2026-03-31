using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace FinanceDashboard.Models;

public class KpiSummary
{
    public double Revenue { get; set; }
    public double Cost { get; set; }
    public double Profit { get; set; }
    public double Margin { get; set; }
}

public class Invoice
{
    public string Name { get; set; } = "";
    public string Customer { get; set; } = "";
    public double GrandTotal { get; set; }
    public double OutstandingAmount { get; set; }
    public string PostingDate { get; set; } = "";
    public string Status { get; set; } = "";
}

public class Payment
{
    public string Name { get; set; } = "";
    public string Party { get; set; } = "";
    public double PaidAmount { get; set; }
    public string PostingDate { get; set; } = "";
    public string ModeOfPayment { get; set; } = "";
}

public class GlEntry
{
    public string PostingDate { get; set; } = "";
    public string Account { get; set; } = "";
    public string VoucherNo { get; set; } = "";
    public double Debit { get; set; }
    public double Credit { get; set; }
}

public class CostCenter
{
    [JsonPropertyName("cost_center")]
    public string Name { get; set; } = "";
    public double Debit { get; set; }
    public double Credit { get; set; }
    public double Net { get; set; }
}

public class BudgetConfig
{
    public double RevenueTarget { get; set; }
    public double CostLimit { get; set; }
    public double ProfitTarget { get; set; }
    public double MarginMin { get; set; }
}

public class BudgetAlert
{
    public string Level { get; set; } = "";
    public string Type { get; set; } = "";
    public string Message { get; set; } = "";
}

public class BudgetAlertsResponse
{
    public KpiSummary Kpi { get; set; } = new();
    public List<BudgetAlert> Alerts { get; set; } = new();
    public BudgetConfig Budget { get; set; } = new();
}