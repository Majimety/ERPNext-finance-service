using System;
using System.Collections.ObjectModel;
using System.IO;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using FinanceDashboard.Models;
using FinanceDashboard.Services;

namespace FinanceDashboard.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly FinanceApiService _api = new();

    [ObservableProperty] private DateTimeOffset? _fromDate = new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero);
    [ObservableProperty] private DateTimeOffset? _toDate   = new DateTimeOffset(2026, 1, 31, 0, 0, 0, TimeSpan.Zero);
    [ObservableProperty] private string _statusText  = "กด Load Data เพื่อดึงข้อมูล";
    [ObservableProperty] private bool   _isLoading   = false;
    [ObservableProperty] private string _statusColor = "#6b7068";
    [ObservableProperty] private string _revenue = "—";
    [ObservableProperty] private string _cost    = "—";
    [ObservableProperty] private string _profit  = "—";
    [ObservableProperty] private string _margin  = "—";
    [ObservableProperty] private string _period  = "—";
    [ObservableProperty] private string _apiBase = "http://localhost:8000";
    [ObservableProperty] private double _revenueTarget;
    [ObservableProperty] private double _costLimit;
    [ObservableProperty] private double _profitTarget;
    [ObservableProperty] private double _marginMin;

    public ObservableCollection<Invoice>    Invoices    { get; } = new();
    public ObservableCollection<Payment>    Payments    { get; } = new();
    public ObservableCollection<GlEntry>    GlEntries   { get; } = new();
    public ObservableCollection<CostCenter> CostCenters { get; } = new();
    public ObservableCollection<BudgetAlertVm> Alerts   { get; } = new();

    [RelayCommand]
    private async Task LoadDataAsync()
    {
        IsLoading = true;
        StatusText  = "กำลังดึงข้อมูล…";
        StatusColor = "#f5e6a0";
        var from = FromDate?.ToString("yyyy-MM-dd") ?? "2026-01-01";
        var to   = ToDate?.ToString("yyyy-MM-dd") ?? "2026-01-31";
        _api.BaseUrl = ApiBase;

        try
        {
            var kpi     = await _api.GetKpiAsync(from, to);
            var invList = await _api.GetInvoicesAsync(from, to);
            var payList = await _api.GetPaymentsAsync(from, to);
            var glList  = await _api.GetGlEntriesAsync(from, to);
            var ccList  = await _api.GetCostCenterAsync(from, to);
            var alerts  = await _api.GetBudgetAlertsAsync(from, to);

            Revenue = kpi.Revenue.ToString("N0");
            Cost    = kpi.Cost.ToString("N0");
            Profit  = kpi.Profit.ToString("N0");
            Margin  = kpi.Margin.ToString("F1") + "%";
            Period  = $"{from}  —  {to}";

            Invoices.Clear();    foreach (var i in invList) Invoices.Add(i);
            Payments.Clear();    foreach (var p in payList) Payments.Add(p);
            GlEntries.Clear();   foreach (var g in glList)  GlEntries.Add(g);
            CostCenters.Clear(); foreach (var c in ccList)  CostCenters.Add(c);
            Alerts.Clear();
            foreach (var a in alerts.Alerts) Alerts.Add(new BudgetAlertVm(a));

            RevenueTarget = alerts.Budget.RevenueTarget;
            CostLimit     = alerts.Budget.CostLimit;
            ProfitTarget  = alerts.Budget.ProfitTarget;
            MarginMin     = alerts.Budget.MarginMin;

            StatusText  = $"โหลดสำเร็จ · {DateTime.Now:HH:mm:ss}";
            StatusColor = "#b8f5a0";
        }
        catch (Exception ex)
        {
            StatusText  = $"เชื่อมต่อไม่ได้: {ex.Message}";
            StatusColor = "#f5a0a0";
        }
        finally
        {
            IsLoading = false;
        }
    }

    [RelayCommand]
    private async Task SaveBudgetAsync()
    {
        _api.BaseUrl = ApiBase;
        try
        {
            await _api.SaveBudgetConfigAsync(new BudgetConfig
            {
                RevenueTarget = RevenueTarget,
                CostLimit     = CostLimit,
                ProfitTarget  = ProfitTarget,
                MarginMin     = MarginMin,
            });
            await LoadDataAsync();
        }
        catch (Exception ex)
        {
            StatusText  = $"บันทึกไม่สำเร็จ: {ex.Message}";
            StatusColor = "#f5a0a0";
        }
    }

    [RelayCommand]
    private async Task ExportAsync(string type)
    {
        _api.BaseUrl = ApiBase;
        var from = FromDate?.ToString("yyyy-MM-dd") ?? "2026-01-01";
        var to   = ToDate?.ToString("yyyy-MM-dd") ?? "2026-01-31";
        var path = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.Desktop),
            $"{type}_{from}_{to}.csv");
        try
        {
            await _api.ExportCsvAsync(type, from, to, path);
            StatusText  = $"Export สำเร็จ → {path}";
            StatusColor = "#b8f5a0";
        }
        catch (Exception ex)
        {
            StatusText  = $"Export ไม่สำเร็จ: {ex.Message}";
            StatusColor = "#f5a0a0";
        }
    }
}

public class BudgetAlertVm
{
    public string Message { get; }
    public string Icon    { get; }
    public string Color   { get; }

    public BudgetAlertVm(BudgetAlert a)
    {
        Message = a.Message;
        Icon    = a.Level switch { "ok" => "✓", "warning" => "⚠", _ => "✗" };
        Color   = a.Level switch { "ok" => "#b8f5a0", "warning" => "#f5e6a0", _ => "#f5a0a0" };
    }
}