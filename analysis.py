import pandas as pd
import sqlite3
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("retail_sales_data.csv")

df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Year"]       = df["Order Date"].dt.year
df["Month"]      = df["Order Date"].dt.month
df["Month Name"] = df["Order Date"].dt.strftime("%B")
df["Quarter"]    = df["Order Date"].dt.quarter.map({
    1: "Q1 (Jan-Mar)", 2: "Q2 (Apr-Jun)",
    3: "Q3 (Jul-Sep)", 4: "Q4 (Oct-Dec)"
})

print(f"Records loaded : {len(df):,}")
print(f"Date range     : {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
print(f"Missing values : {df.isnull().sum().sum()}")
print(f"Duplicate IDs  : {df.duplicated('Order ID').sum()}")

conn = sqlite3.connect(":memory:")
df.to_sql("sales", conn, index=False, if_exists="replace")

queries = {
    "Revenue & Profit by Category": """
        SELECT
            "Product Category"                       AS Category,
            COUNT("Order ID")                        AS Orders,
            SUM("Quantity Sold")                     AS "Units Sold",
            ROUND(SUM("Total Revenue (INR)"), 0)     AS "Revenue (INR)",
            ROUND(SUM("Profit (INR)"), 0)            AS "Profit (INR)",
            ROUND(AVG("Customer Rating"), 2)         AS "Avg Rating"
        FROM sales
        GROUP BY "Product Category"
        ORDER BY "Revenue (INR)" DESC
    """,
    "Revenue by City": """
        SELECT
            City,
            COUNT("Order ID")                        AS Orders,
            ROUND(SUM("Total Revenue (INR)"), 0)     AS "Revenue (INR)",
            ROUND(AVG("Discount Percentage"), 1)     AS "Avg Discount (%)",
            ROUND(100.0 * SUM(CASE WHEN Returned='Yes' THEN 1 ELSE 0 END)
                  / COUNT(*), 1)                     AS "Return Rate (%)"
        FROM sales
        GROUP BY City
        ORDER BY "Revenue (INR)" DESC
    """,
    "Monthly Revenue Trend": """
        SELECT
            Year,
            "Month Name",
            ROUND(SUM("Total Revenue (INR)"), 0)     AS "Monthly Revenue (INR)",
            COUNT("Order ID")                        AS Orders
        FROM sales
        GROUP BY Year, Month
        ORDER BY Year, Month
    """,
    "Payment Method Usage": """
        SELECT
            "Payment Method",
            COUNT(*)                                 AS "Times Used",
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM sales), 1) AS "Usage (%)"
        FROM sales
        GROUP BY "Payment Method"
        ORDER BY "Times Used" DESC
    """,
    "Top 5 Products by Profit": """
        SELECT
            "Product Name",
            "Product Category",
            ROUND(SUM("Profit (INR)"), 0)            AS "Total Profit (INR)",
            ROUND(AVG("Discount Percentage"), 1)     AS "Avg Discount (%)",
            ROUND(AVG("Customer Rating"), 2)         AS "Avg Rating"
        FROM sales
        GROUP BY "Product Name"
        ORDER BY "Total Profit (INR)" DESC
        LIMIT 5
    """,
    "Return Rate by Category": """
        SELECT
            "Product Category",
            COUNT(*)                                 AS Orders,
            SUM(CASE WHEN Returned='Yes' THEN 1 ELSE 0 END) AS Returned,
            ROUND(100.0 * SUM(CASE WHEN Returned='Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS "Return Rate (%)"
        FROM sales
        GROUP BY "Product Category"
        ORDER BY "Return Rate (%)" DESC
    """
}

for title, sql in queries.items():
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print('─' * 60)
    print(pd.read_sql_query(sql, conn).to_string(index=False))

conn.close()

total_revenue = df["Total Revenue (INR)"].sum()
total_profit  = df["Profit (INR)"].sum()
profit_margin = (total_profit / total_revenue) * 100
top_city      = df.groupby("City")["Total Revenue (INR)"].sum().idxmax()
top_category  = df.groupby("Product Category")["Total Revenue (INR)"].sum().idxmax()
return_rate   = (df["Returned"] == "Yes").mean() * 100

print(f"\n{'═' * 60}")
print("  SUMMARY")
print('═' * 60)
print(f"  Total Revenue   : ₹{total_revenue:,.0f}")
print(f"  Total Profit    : ₹{total_profit:,.0f}")
print(f"  Profit Margin   : {profit_margin:.1f}%")
print(f"  Top City        : {top_city}")
print(f"  Top Category    : {top_category}")
print(f"  Return Rate     : {return_rate:.1f}%\n")
