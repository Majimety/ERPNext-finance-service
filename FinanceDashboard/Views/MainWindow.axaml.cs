using System;
using System.Collections.Generic;
using System.Linq;
using Avalonia;
using Avalonia.Controls;
using Avalonia.VisualTree;
using Avalonia.Controls.Templates;
using Avalonia.Data;
using Avalonia.Interactivity;
using Avalonia.Layout;
using Avalonia.Media;
using FinanceDashboard.ViewModels;

namespace FinanceDashboard.Views;

public partial class MainWindow : Window
{
    private List<Button> _navButtons = new();
    private MainViewModel Vm => (MainViewModel)DataContext!;

    public MainWindow()
    {
        InitializeComponent();
        this.Loaded += (_, _) =>
        {
            _navButtons = this.GetVisualDescendants()
                .OfType<Button>()
                .Where(b => b.Tag is string s && int.TryParse(s, out _))
                .ToList();
            ShowPage(0);
        };
    }

    private void NavBtn_Click(object? sender, RoutedEventArgs e)
    {
        if (sender is Button btn && btn.Tag is string tag && int.TryParse(tag, out var idx))
            ShowPage(idx);
    }

    private static readonly string[] Titles =
        { "Dashboard","KPI Summary","Invoices","Payments","GL Entries","Cost Center","Budget Alerts","Export Report" };

    private void ShowPage(int idx)
    {
        foreach (var b in _navButtons)
        {
            b.Classes.Remove("active");
            if (b.Tag is string s && s == idx.ToString()) b.Classes.Add("active");
        }
        PageTitleText.Text = Titles[idx];
        PageHost.Content = idx switch
        {
            0 => BuildDashboard(),
            1 => BuildKpiSummary(),
            2 => BuildInvoices(),
            3 => BuildPayments(),
            4 => BuildGlEntries(),
            5 => BuildCostCenter(),
            6 => BuildAlerts(),
            7 => BuildExport(),
            _ => new TextBlock { Text = "Not found" }
        };
    }

    // ── Helpers ──────────────────────────────────────────────
    private static Border Panel(Control content, string title, string tag = "")
    {
        var hdrContent = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
        hdrContent.Children.Add(new TextBlock
        {
            Text = title.ToUpper(), FontSize = 10, LetterSpacing = 1.5,
            Foreground = new SolidColorBrush(Color.Parse("#e8ebe9")),
            VerticalAlignment = VerticalAlignment.Center
        });
        if (!string.IsNullOrEmpty(tag))
        {
            var tagEl = new Border
            {
                Padding = new Thickness(8, 3), CornerRadius = new CornerRadius(4),
                Background = new SolidColorBrush(Color.Parse("#1c1f1d")),
                BorderBrush = new SolidColorBrush(Color.Parse("#252826")), BorderThickness = new Thickness(1),
                Child = new TextBlock { Text = tag, FontSize = 10, Foreground = new SolidColorBrush(Color.Parse("#6b7068")) }
            };
            Grid.SetColumn(tagEl, 1);
            hdrContent.Children.Add(tagEl);
        }
        var dp = new DockPanel();
        var hdr = new Border
        {
            Padding = new Thickness(20, 14), BorderBrush = new SolidColorBrush(Color.Parse("#252826")),
            BorderThickness = new Thickness(0, 0, 0, 1), Child = hdrContent
        };
        DockPanel.SetDock(hdr, Dock.Top);
        dp.Children.Add(hdr);
        dp.Children.Add(new Border { Padding = new Thickness(20), Child = content });
        return new Border
        {
            Background = new SolidColorBrush(Color.Parse("#141716")),
            BorderBrush = new SolidColorBrush(Color.Parse("#252826")),
            BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(10), Child = dp
        };
    }

    private DataGrid MakeGrid(params (string H, string B)[] cols)
    {
        var dg = new DataGrid { IsReadOnly = true, AutoGenerateColumns = false, CanUserResizeColumns = true };
        foreach (var (h, b) in cols)
            dg.Columns.Add(new DataGridTextColumn
            {
                Header = h, Binding = new Binding(b),
                Width = new DataGridLength(1, DataGridLengthUnitType.Star)
            });
        return dg;
    }

    private Button Btn(string text, string cls = "accent")
    {
        var b = new Button { Content = text };
        b.Classes.Add(cls); return b;
    }

    // ── Page 0: Dashboard ────────────────────────────────────
    private Control BuildDashboard()
    {
        var kpiRow = new Grid { ColumnDefinitions = new ColumnDefinitions("*,12,*,12,*,12,*"), Margin = new Thickness(0, 0, 0, 20) };
        var defs = new[] { ("REVENUE","Revenue","#a0c8f5"), ("COST","Cost","#f5a0a0"), ("PROFIT","Profit","#b8f5a0"), ("MARGIN","Margin","#f5e6a0") };
        int[] gcols = { 0, 2, 4, 6 };
        for (int i = 0; i < defs.Length; i++)
        {
            var (lbl, prop, clr) = defs[i];
            var card = new Border
            {
                Background = new SolidColorBrush(Color.Parse("#141716")),
                BorderBrush = new SolidColorBrush(Color.Parse("#252826")),
                BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(10), Padding = new Thickness(22),
                Child = new StackPanel { Children = {
                    new TextBlock { Text = lbl, FontSize = 10, Foreground = new SolidColorBrush(Color.Parse("#6b7068")), LetterSpacing = 2, Margin = new Thickness(0,0,0,8) },
                    new TextBlock { [!TextBlock.TextProperty] = new Binding(prop) { Source = DataContext }, FontSize = 26, FontWeight = FontWeight.Bold, Foreground = new SolidColorBrush(Color.Parse(clr)) },
                    new TextBlock { [!TextBlock.TextProperty] = new Binding("Period") { Source = DataContext }, FontSize = 11, Foreground = new SolidColorBrush(Color.Parse("#6b7068")), Margin = new Thickness(0,6,0,0) }
                }}
            };
            Grid.SetColumn(card, gcols[i]); kpiRow.Children.Add(card);
        }

        var invDg = MakeGrid(("No.", "Name"), ("Customer", "Customer"), ("Total", "GrandTotal"), ("Status", "Status"));
        invDg.ItemsSource = Vm.Invoices;
        var payDg = MakeGrid(("No.", "Name"), ("Party", "Party"), ("Amount", "PaidAmount"), ("Method", "ModeOfPayment"));
        payDg.ItemsSource = Vm.Payments;

        var bottom = new Grid { ColumnDefinitions = new ColumnDefinitions("*,16,*") };
        var ip = Panel(invDg, "Recent Invoices", "Sales Invoice");
        var pp = Panel(payDg, "Recent Payments", "Payment Entry");
        Grid.SetColumn(ip, 0); Grid.SetColumn(pp, 2);
        bottom.Children.Add(ip); bottom.Children.Add(pp);

        return new StackPanel { Children = { kpiRow, bottom } };
    }

    // ── Page 1: KPI Summary ──────────────────────────────────
    private Control BuildKpiSummary()
    {
        var sp = new StackPanel { Spacing = 12 };
        foreach (var (lbl, prop, clr) in new[] { ("Revenue","Revenue","#a0c8f5"),("Cost","Cost","#f5a0a0"),("Profit","Profit","#b8f5a0"),("Margin","Margin","#f5e6a0") })
        {
            var g = new Grid { ColumnDefinitions = new ColumnDefinitions("*,Auto") };
            g.Children.Add(new TextBlock { Text = lbl, FontSize = 14, Foreground = new SolidColorBrush(Color.Parse("#e8ebe9")), VerticalAlignment = VerticalAlignment.Center });
            var val = new TextBlock { [!TextBlock.TextProperty] = new Binding(prop) { Source = DataContext }, FontSize = 22, FontWeight = FontWeight.Bold, Foreground = new SolidColorBrush(Color.Parse(clr)), VerticalAlignment = VerticalAlignment.Center };
            Grid.SetColumn(val, 1); g.Children.Add(val);
            sp.Children.Add(new Border { Background = new SolidColorBrush(Color.Parse("#141716")), BorderBrush = new SolidColorBrush(Color.Parse("#252826")), BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(8), Padding = new Thickness(24, 18), Child = g });
        }
        return Panel(sp, "KPI Summary");
    }

    // ── Page 2-5: Tables ─────────────────────────────────────
    private Control BuildInvoices()
    {
        var dg = MakeGrid(("No.","Name"),("Customer","Customer"),("Total","GrandTotal"),("Outstanding","OutstandingAmount"),("Date","PostingDate"),("Status","Status"));
        dg.ItemsSource = Vm.Invoices; return Panel(dg, "All Invoices", "Sales Invoice");
    }
    private Control BuildPayments()
    {
        var dg = MakeGrid(("No.","Name"),("Party","Party"),("Amount","PaidAmount"),("Date","PostingDate"),("Method","ModeOfPayment"));
        dg.ItemsSource = Vm.Payments; return Panel(dg, "All Payments", "Payment Entry");
    }
    private Control BuildGlEntries()
    {
        var dg = MakeGrid(("Date","PostingDate"),("Account","Account"),("Voucher","VoucherNo"),("Debit","Debit"),("Credit","Credit"));
        dg.ItemsSource = Vm.GlEntries; return Panel(dg, "GL Entries", "General Ledger");
    }
    private Control BuildCostCenter()
    {
        var dg = MakeGrid(("Cost Center","CostCenterName"),("Debit","Debit"),("Credit","Credit"),("Net","Net"));
        dg.ItemsSource = Vm.CostCenters; return Panel(dg, "Cost Center Breakdown", "GL Entry");
    }

    // ── Page 6: Budget Alerts ────────────────────────────────
    private Control BuildAlerts()
    {
        var form = new Grid { ColumnDefinitions = new ColumnDefinitions("*,16,*"), RowDefinitions = new RowDefinitions("Auto,16,Auto") };
        var fields = new[] { ("Revenue Target (฿)","RevenueTarget",0,0), ("Cost Limit (฿)","CostLimit",0,2), ("Profit Target (฿)","ProfitTarget",2,0), ("Margin Min (%)","MarginMin",2,2) };
        foreach (var (lbl, prop, row, col) in fields)
        {
            var sp = new StackPanel { Spacing = 6 };
            sp.Children.Add(new TextBlock { Text = lbl.ToUpper(), FontSize = 10, Foreground = new SolidColorBrush(Color.Parse("#6b7068")), LetterSpacing = 1.5 });
            sp.Children.Add(new NumericUpDown { [!NumericUpDown.ValueProperty] = new Binding(prop) { Source = DataContext, Mode = BindingMode.TwoWay }, Minimum = 0, FormatString = "N0" });
            Grid.SetRow(sp, row); Grid.SetColumn(sp, col); form.Children.Add(sp);
        }
        var saveBtn = Btn("Save Budget Config");
        saveBtn.Command = Vm.SaveBudgetCommand;
        var configCard = Panel(new StackPanel { Children = { form, saveBtn }, Spacing = 16 }, "Budget Configuration");

        var alertList = new ItemsControl
        {
            ItemsSource = Vm.Alerts,
            ItemTemplate = new FuncDataTemplate<BudgetAlertVm>((a, _) => new Border
            {
                Background = new SolidColorBrush(Color.Parse("#1c1f1d")),
                BorderBrush = new SolidColorBrush(Color.Parse(a?.Color ?? "#252826")),
                BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(8),
                Padding = new Thickness(16, 12), Margin = new Thickness(0, 0, 0, 8),
                Child = new StackPanel { Orientation = Orientation.Horizontal, Spacing = 12, Children = {
                    new TextBlock { Text = a?.Icon, FontSize = 16, Foreground = new SolidColorBrush(Color.Parse(a?.Color ?? "#6b7068")), VerticalAlignment = VerticalAlignment.Center },
                    new TextBlock { Text = a?.Message, FontSize = 13, Foreground = new SolidColorBrush(Color.Parse("#e8ebe9")), TextWrapping = TextWrapping.Wrap }
                }}
            })
        };

        return new StackPanel { Spacing = 20, Children = { configCard, Panel(alertList, "Alerts") } };
    }

    // ── Page 7: Export ───────────────────────────────────────
    private Control BuildExport()
    {
        var g = new Grid { ColumnDefinitions = new ColumnDefinitions("*,16,*,16,*") };
        var exports = new[] { ("KPI Summary","Revenue, Cost, Profit, Margin","kpi",0), ("Invoices","รายการใบแจ้งหนี้ทั้งหมด","invoices",2), ("Payments","รายการชำระเงินทั้งหมด","payments",4) };
        foreach (var (title, desc, type, col) in exports)
        {
            var btn = Btn("Download CSV");
            btn.Command = Vm.ExportCommand;
            btn.CommandParameter = type;
            var card = new Border
            {
                Background = new SolidColorBrush(Color.Parse("#1c1f1d")),
                BorderBrush = new SolidColorBrush(Color.Parse("#252826")),
                BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(10), Padding = new Thickness(24),
                Child = new StackPanel { Spacing = 10, Children = {
                    new TextBlock { Text = title.ToUpper(), FontSize = 11, Foreground = new SolidColorBrush(Color.Parse("#e8ebe9")), LetterSpacing = 1.5 },
                    new TextBlock { Text = desc, FontSize = 12, Foreground = new SolidColorBrush(Color.Parse("#6b7068")), TextWrapping = TextWrapping.Wrap },
                    btn
                }}
            };
            Grid.SetColumn(card, col); g.Children.Add(card);
        }
        return Panel(g, "Export Reports", "CSV Download");
    }
}