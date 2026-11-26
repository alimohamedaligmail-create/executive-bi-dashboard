# Executive BI Dashboard
Interactive Business Intelligence dashboard built on the retail sales dataset (`9,800` records from `2015-01-03` to `2018-12-30`, totaling `$2,261,536.78` in sales) to explore performance across regions, categories, and shipping modes.


## Key Features
- **Dataset & Relative Loading:** Uses `data/retail_sales.csv` loaded via relative path (`Path(__file__).resolve().parent / "data" / "retail_sales.csv"`).
- **Interactive Filtering & Empty-State Handling:** Filter records by date range, region, category, and shipping mode, with a clear fallback message when no records match.
- **Executive KPI Cards:** Tracks Total Sales, Estimated Profit, Target Variance, Order Count, and Average Order Value.
- **Interactive Visualizations:**
  - **Trend:** Monthly sales performance over time.
  - **Comparison:** Sales breakdown across categories (`Technology`, `Furniture`, `Office Supplies`) and shipping modes (`Standard Class`, `Second Class`, `First Class`, `Same Day`).
  - **Relationship / Drilldown:** Order-level exploration across regions (`West`, `East`, `Central`, `South`) and sales value.
- **Automated Insight Callout & Filtered CSV Export:** Summarizes top-performing segments dynamically and exports the filtered rows to CSV.

## Project Structure
executive-bi-dashboard/
├── .streamlit/
│   └── config.toml
├── assets/
│   ├── ![Desktop Dashboard](assets/desktop-dashboard.png)
│   └── ![Mobile Dashboard](assets/mobile-dashboard.png)
├── data/
│   └── retail_sales.csv
├── .gitignore
├── build_dashboard.py
├── index.html
├── README.md
└── requirements.txt