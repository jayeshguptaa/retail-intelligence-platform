# Retail Sales Intelligence Dashboard

An end-to-end data analysis project built on 2,000 retail sales transactions across 8 Indian cities (Jan 2023 – Jun 2024).

**Live demo →** [streamlit link here]

---

## Stack

| Layer | Tool |
|---|---|
| Data wrangling | Python, Pandas |
| SQL analysis | SQLite (in-memory) |
| Dashboard | Streamlit |
| Charts | Plotly |

---

## Project structure

```
retail-sales-dashboard/
├── retail_sales_data.csv   # 2,000 orders, 17 columns
├── analysis.py             # SQL queries and summary stats
├── app.py                  # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## What's in the dashboard

- **Sales over time** — monthly revenue/profit trends, quarterly breakdown, day-of-week patterns
- **Product performance** — revenue and profit by category, top 10 products, return rates
- **City analysis** — revenue, margin, and discount comparison across 8 cities
- **Customer behaviour** — gender split, payment method adoption, age group analysis, discount effectiveness
- **Insights** — data-driven findings and recommendations derived from the above

All charts are interactive and respond to sidebar filters (year, city, category).

---

## Running locally

```bash
pip install -r requirements.txt

# Optional: run SQL analysis in the terminal
python analysis.py

# Launch the dashboard
streamlit run app.py
```

---

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your account
3. Select the repo, set `app.py` as the entry point, and deploy

The app will be live at a public URL within a couple of minutes. No configuration needed beyond the `requirements.txt`.
