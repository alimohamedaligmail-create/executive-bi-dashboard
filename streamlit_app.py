from pathlib import Path
import csv
import json
import random


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "retail_sales.csv"
OUT_FILE = BASE_DIR / "index.html"


def ensure_sample_csv(csv_path: Path) -> None:
    if csv_path.exists():
        return
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    regions = ["North", "South", "East", "West"]
    categories = ["Electronics", "Home & Kitchen", "Apparel", "Office Supplies"]
    channels = ["Online", "In-Store", "Marketplace"]
    prices = {
        "Electronics": 240.0,
        "Home & Kitchen": 85.0,
        "Apparel": 55.0,
        "Office Supplies": 32.0,
    }
    margins = {
        "Electronics": 0.22,
        "Home & Kitchen": 0.34,
        "Apparel": 0.42,
        "Office Supplies": 0.29,
    }

    rows = []
    for i in range(1, 601):
        month_num = rng.randint(1, 12)
        day_num = rng.randint(1, 28)
        order_date = f"2025-{month_num:02d}-{day_num:02d}"
        region = rng.choice(regions)
        category = rng.choice(categories)
        channel = rng.choice(channels)
        units = rng.randint(1, 10)
        unit_price = round(prices[category] * rng.uniform(0.85, 1.2), 2)
        revenue = round(units * unit_price, 2)
        margin = max(0.05, min(0.65, rng.gauss(margins[category], 0.04)))
        profit = round(revenue * margin, 2)
        target_revenue = round(revenue * rng.uniform(0.92, 1.08), 2)
        rows.append(
            {
                "order_id": f"ORD-{1000 + i}",
                "order_date": order_date,
                "region": region,
                "category": category,
                "channel": channel,
                "units_sold": units,
                "unit_price": unit_price,
                "revenue": revenue,
                "profit": profit,
                "target_revenue": target_revenue,
            }
        )

    rows.sort(key=lambda r: r["order_date"])
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_records(csv_path: Path) -> list[dict]:
    records = []
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                dt = row["order_date"].strip()
                if len(dt) < 7:
                    continue
                records.append(
                    {
                        "order_id": row["order_id"],
                        "order_date": dt,
                        "month": dt[:7],
                        "region": row["region"],
                        "category": row["category"],
                        "channel": row["channel"],
                        "units_sold": int(float(row["units_sold"])),
                        "unit_price": float(row["unit_price"]),
                        "revenue": float(row["revenue"]),
                        "profit": float(row["profit"]),
                        "target_revenue": float(row["target_revenue"]),
                    }
                )
            except (ValueError, KeyError):
                continue
    return records


def build_html(records: list[dict]) -> str:
    data_json = json.dumps(records)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Executive BI Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --bg: #0b1120;
      --card: #111827;
      --border: #1f2937;
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 20px;
    }}
    .container {{ max-width: 1280px; margin: 0 auto; }}
    .filters {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      background: var(--card);
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 10px;
      margin-bottom: 16px;
    }}
    select, button {{
      width: 100%;
      padding: 8px 10px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: #0f172a;
      color: var(--text);
    }}
    button {{ background: var(--accent); cursor: pointer; font-weight: bold; }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .kpi {{
      background: var(--card);
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 10px;
    }}
    .kpi .label {{ color: var(--muted); font-size: 13px; }}
    .kpi .val {{ font-size: 22px; font-weight: bold; margin-top: 6px; }}
    .insight {{
      background: #172554;
      border: 1px solid #1d4ed8;
      padding: 12px 14px;
      border-radius: 10px;
      margin-bottom: 16px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 14px;
      margin-bottom: 16px;
    }}
    .box {{
      background: var(--card);
      border: 1px solid var(--border);
      padding: 14px;
      border-radius: 10px;
    }}
    .empty {{
      display: none;
      background: #451a03;
      border: 1px solid #b45309;
      padding: 14px;
      border-radius: 10px;
      margin-bottom: 16px;
    }}
    .actions {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }}
    .actions button {{ width: auto; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Executive BI Dashboard</h1>
    <div class="filters">
      <div>
        <label>Region</label>
        <select id="regionFilter"><option value="ALL">All Regions</option></select>
      </div>
      <div>
        <label>Category</label>
        <select id="categoryFilter"><option value="ALL">All Categories</option></select>
      </div>
      <div>
        <label>Channel</label>
        <select id="channelFilter"><option value="ALL">All Channels</option></select>
      </div>
      <div style="display:flex;align-items:flex-end;">
        <button id="resetBtn" type="button">Reset Filters</button>
      </div>
    </div>

    <div id="emptyBox" class="empty">No records match the selected filters. Click Reset Filters.</div>

    <div id="dashboardContent">
      <div class="kpis">
        <div class="kpi"><div class="label">Total Revenue</div><div id="kpiRev" class="val">$0</div></div>
        <div class="kpi"><div class="label">Net Profit</div><div id="kpiProfit" class="val">$0</div></div>
        <div class="kpi"><div class="label">Target Variance</div><div id="kpiVar" class="val">$0</div></div>
        <div class="kpi"><div class="label">Units Sold</div><div id="kpiUnits" class="val">0</div></div>
        <div class="kpi"><div class="label">Avg Order Value</div><div id="kpiAov" class="val">$0</div></div>
      </div>

      <div id="insightBox" class="insight"></div>

      <div class="actions">
        <button id="exportCsvBtn" type="button">Download Filtered CSV</button>
      </div>

      <div class="box" style="margin-bottom:14px;">
        <canvas id="trendChart" height="90"></canvas>
      </div>

      <div class="grid">
        <div class="box"><canvas id="catChart" height="150"></canvas></div>
        <div class="box"><canvas id="scatterChart" height="150"></canvas></div>
      </div>
    </div>
  </div>

  <script>
    const RAW_DATA = {data_json};
    let trendChart = null;
    let catChart = null;
    let scatterChart = null;
    let currentFiltered = [];

    function populateSelect(id, key) {{
      const el = document.getElementById(id);
      const vals = [...new Set(RAW_DATA.map(r => r[key]))].sort();
      vals.forEach(v => {{
        const opt = document.createElement("option");
        opt.value = v;
        opt.textContent = v;
        el.appendChild(opt);
      }});
    }}

    function renderAll() {{
      const reg = document.getElementById("regionFilter").value;
      const cat = document.getElementById("categoryFilter").value;
      const ch = document.getElementById("channelFilter").value;

      currentFiltered = RAW_DATA.filter(r =>
        (reg === "ALL" || r.region === reg) &&
        (cat === "ALL" || r.category === cat) &&
        (ch === "ALL" || r.channel === ch)
      );

      const emptyBox = document.getElementById("emptyBox");
      const content = document.getElementById("dashboardContent");
      if (!currentFiltered.length) {{
        emptyBox.style.display = "block";
        content.style.display = "none";
        return;
      }}
      emptyBox.style.display = "none";
      content.style.display = "block";

      const rev = currentFiltered.reduce((s, r) => s + r.revenue, 0);
      const profit = currentFiltered.reduce((s, r) => s + r.profit, 0);
      const target = currentFiltered.reduce((s, r) => s + r.target_revenue, 0);
      const units = currentFiltered.reduce((s, r) => s + r.units_sold, 0);
      const aov = rev / currentFiltered.length;
      const variance = rev - target;

      document.getElementById("kpiRev").textContent = "$" + Math.round(rev).toLocaleString();
      document.getElementById("kpiProfit").textContent = "$" + Math.round(profit).toLocaleString();
      document.getElementById("kpiVar").textContent = (variance >= 0 ? "+$" : "-$") + Math.abs(Math.round(variance)).toLocaleString();
      document.getElementById("kpiUnits").textContent = units.toLocaleString();
      document.getElementById("kpiAov").textContent = "$" + aov.toFixed(2);

      const byCat = {{}};
      currentFiltered.forEach(r => {{
        byCat[r.category] = (byCat[r.category] || 0) + r.revenue;
      }});
      const sortedCats = Object.entries(byCat).sort((a, b) => b[1] - a[1]);
      const topCat = sortedCats.length ? sortedCats[0][0] : "N/A";
      document.getElementById("insightBox").textContent =
        "Automated Insight: Top revenue category is " + topCat + " across " + currentFiltered.length + " filtered orders.";

      const months = [...new Set(currentFiltered.map(r => r.month))].sort();
      const monthRev = months.map(m =>
        currentFiltered.filter(r => r.month === m).reduce((s, r) => s + r.revenue, 0)
      );
      const monthTarget = months.map(m =>
        currentFiltered.filter(r => r.month === m).reduce((s, r) => s + r.target_revenue, 0)
      );

      if (trendChart) trendChart.destroy();
      trendChart = new Chart(document.getElementById("trendChart"), {{
        type: "line",
        data: {{
          labels: months,
          datasets: [
            {{ label: "Actual Revenue", data: monthRev, borderColor: "#38bdf8", tension: 0.25 }},
            {{ label: "Target Revenue", data: monthTarget, borderColor: "#f59e0b", borderDash: [5, 5], tension: 0.25 }}
          ]
        }},
        options: {{
          responsive: true,
          plugins: {{ title: {{ display: true, text: "Monthly Revenue vs Target", color: "#f8fafc" }} }}
        }}
      }});

      const cats = sortedCats.map(item => item[0]);
      if (catChart) catChart.destroy();
      catChart = new Chart(document.getElementById("catChart"), {{
        type: "bar",
        data: {{
          labels: cats,
          datasets: [{{ label: "Revenue ($)", data: cats.map(c => byCat[c]), backgroundColor: "#2563eb" }}]
        }},
        options: {{
          responsive: true,
          plugins: {{ title: {{ display: true, text: "Revenue by Category", color: "#f8fafc" }} }}
        }}
      }});

      if (scatterChart) scatterChart.destroy();
      scatterChart = new Chart(document.getElementById("scatterChart"), {{
        type: "scatter",
        data: {{
          datasets: [{{
            label: "Orders (Revenue vs Profit)",
            data: currentFiltered.slice(0, 300).map(r => ({{ x: r.revenue, y: r.profit }})),
            backgroundColor: "#22c55e"
          }}]
        }},
        options: {{
          responsive: true,
          plugins: {{ title: {{ display: true, text: "Profit vs Revenue", color: "#f8fafc" }} }}
        }}
      }});
    }}

    function downloadCsv() {{
      if (!currentFiltered.length) return;
      const cols = Object.keys(currentFiltered[0]);
      const lines = [cols.join(",")].concat(
        currentFiltered.map(r => cols.map(c => JSON.stringify(r[c] ?? "")).join(","))
      );
      const blob = new Blob([lines.join("\\n")], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "filtered_data.csv";
      a.click();
      URL.revokeObjectURL(url);
    }}

    populateSelect("regionFilter", "region");
    populateSelect("categoryFilter", "category");
    populateSelect("channelFilter", "channel");

    ["regionFilter", "categoryFilter", "channelFilter"].forEach(id =>
      document.getElementById(id).addEventListener("change", renderAll)
    );
    document.getElementById("resetBtn").addEventListener("click", () => {{
      document.getElementById("regionFilter").value = "ALL";
      document.getElementById("categoryFilter").value = "ALL";
      document.getElementById("channelFilter").value = "ALL";
      renderAll();
    }});
    document.getElementById("exportCsvBtn").addEventListener("click", downloadCsv);

    renderAll();
  </script>
</body>
</html>
"""


def main() -> None:
    ensure_sample_csv(DATA_FILE)
    records = load_records(DATA_FILE)
    OUT_FILE.write_text(build_html(records), encoding="utf-8")
    print(f"Generated {OUT_FILE} from {len(records)} rows.")


if __name__ == "__main__":
    main()