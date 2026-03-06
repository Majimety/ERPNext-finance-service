using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using FinanceDashboard.Models;

namespace FinanceDashboard.Services;

public class FinanceApiService
{
    private readonly HttpClient _http;
    private static readonly JsonSerializerOptions _json = new()
    {
        PropertyNameCaseInsensitive = true,
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    };

    public string BaseUrl { get; set; } = "http://localhost:8000";

    public FinanceApiService()
    {
        _http = new HttpClient();
    }

    private string Q(string from, string to) => $"from_date={from}&to_date={to}";

    public async Task<KpiSummary> GetKpiAsync(string from, string to)
    {
        var r = await _http.GetAsync($"{BaseUrl}/kpi/summary?{Q(from, to)}");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<KpiSummary>(_json) ?? new();
    }

    public async Task<List<Invoice>> GetInvoicesAsync(string from, string to)
    {
        var r = await _http.GetAsync($"{BaseUrl}/invoices?{Q(from, to)}");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<List<Invoice>>(_json) ?? new();
    }

    public async Task<List<Payment>> GetPaymentsAsync(string from, string to)
    {
        var r = await _http.GetAsync($"{BaseUrl}/payments?{Q(from, to)}");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<List<Payment>>(_json) ?? new();
    }

    public async Task<List<GlEntry>> GetGlEntriesAsync(string from, string to)
    {
        var r = await _http.GetAsync($"{BaseUrl}/gl-entries?{Q(from, to)}");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<List<GlEntry>>(_json) ?? new();
    }

    public async Task<List<CostCenter>> GetCostCenterAsync(string from, string to)
    {
        var r = await _http.GetAsync($"{BaseUrl}/cost-center?{Q(from, to)}");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<List<CostCenter>>(_json) ?? new();
    }

    public async Task<BudgetAlertsResponse> GetBudgetAlertsAsync(string from, string to)
    {
        var r = await _http.GetAsync($"{BaseUrl}/budget/alerts?{Q(from, to)}");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<BudgetAlertsResponse>(_json) ?? new();
    }

    public async Task<BudgetConfig> GetBudgetConfigAsync()
    {
        var r = await _http.GetAsync($"{BaseUrl}/budget/config");
        r.EnsureSuccessStatusCode();
        return await r.Content.ReadFromJsonAsync<BudgetConfig>(_json) ?? new();
    }

    public async Task SaveBudgetConfigAsync(BudgetConfig config)
    {
        var r = await _http.PostAsJsonAsync($"{BaseUrl}/budget/config", config, _json);
        r.EnsureSuccessStatusCode();
    }

    public async Task ExportCsvAsync(string type, string from, string to, string savePath)
    {
        var url = $"{BaseUrl}/export/{type}?{Q(from, to)}";
        var bytes = await _http.GetByteArrayAsync(url);
        await File.WriteAllBytesAsync(savePath, bytes);
    }
}