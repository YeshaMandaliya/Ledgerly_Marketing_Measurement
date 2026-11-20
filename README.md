# Ledgerly: Where Should the Marketing Budget Go?

**Marketing measurement case study · SQL · multi-touch attribution · channel ROI · Tableau**

> **Answer:** Move **~12% of the paid marketing budget** (≈ $2.6M at 2024 levels) out of review sites and paid search, cutting the non-brand "expense cards" campaign first, and into accountant partners, webinars and content. Expected result: **+$3.5M in 12-month revenue at the same total spend** (range +$0.5M to +$6.5M). Prove it with a 90-day regional test before moving the full amount.

| If you are… | Start here |
|---|---|
| An executive | [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md), a one-page read |
| Exploring the results | [Interactive Tableau dashboard](https://public.tableau.com/views/LedgerlyMarketingMeasurement/Dashboard1) |
| Reviewing the method | This README → [`sql/`](sql/) → [`notebooks/`](notebooks/) |

---

## Contents
1. [The business problem](#1-the-business-problem)
2. [Key findings](#2-key-findings)
3. [Recommendation](#3-recommendation)
4. [How confident are we?](#4-how-confident-are-we)
5. [Data](#5-data)
6. [Method](#6-method)
7. [Data cleaning](#7-data-cleaning)
8. [Why 2024 data for ROI and 2025 for validation](#8-why-2024-data-for-roi-and-2025-for-validation)
9. [Limitations](#9-limitations)
10. [Repo structure and how to reproduce](#10-repo-structure-and-how-to-reproduce)

---

## 1. The business problem
**Ledgerly** (fictional) is a B2B fintech that sells expense cards and bill pay to small businesses. It spent **$48.7M on paid marketing in 2024–2025** ($21.6M in 2024, $27.1M in 2025) across six channels: paid search, LinkedIn ads, content/SEO, accountant partners, webinars and review sites (G2, Capterra, GetApp).

The marketing dashboard credits each new customer to the **last click before signup**. On that view, paid search is the top channel, so budget keeps flowing to it.

**Question:** *Which channels should get more or less of next year's budget to grow revenue, not just signups, at the same total spend?*

**The question broken into three parts:**
1. **Is the data trustworthy?** Would the raw data have misled us?
2. **Who really brings customers?** Does last-click credit distort the picture?
3. **Who brings valuable customers?** Does revenue per dollar rank channels differently from signup counts?

---

## 2. Key findings

### Finding 1: Last-click credit gives paid search twice the credit it earns
Share of 30,289 funded accounts credited to each channel:

| Channel | Last-touch (today) | Linear (every touch counts) |
|---|---|---|
| Paid search | **56.2%** | **27.7%** |
| LinkedIn | 9.3% | 16.4% |
| Content/SEO | 9.2% | 15.3% |
| Review sites | 7.6% | 12.3% |
| Direct | 7.8% | 10.1% |
| Webinars | 5.4% | 9.8% |
| Partners | 4.5% | 8.4% |

**84%** of paid search's last-touch wins (14,296 of 17,037) come from the **brand campaign**: people Googling "Ledgerly" after another channel had already convinced them.

### Finding 2: Return per dollar differs 3× across channels
12-month revenue per $1 of 2024 spend (linear credit), with payback period:

| Channel | Revenue per $1 | Cost per funded account | Months to pay back |
|---|---|---|---|
| Partners | **$5.59** | $1,353 | **2.1** |
| Content/SEO | $4.08 | $1,062 | 2.9 |
| Webinars | $3.33 | $1,597 | 3.6 |
| LinkedIn | $3.10 | $2,064 | 3.9 |
| Paid search | $2.27 | $2,018 | 5.3 |
| Review sites | **$1.81** | $2,197 | **6.6** |

### Finding 3: The ranking flips only under last-touch credit
Revenue per $1 under each credit rule:

| Channel | Last-touch | First-touch | Linear |
|---|---|---|---|
| Partners | $2.70 | $11.64 | **$5.59** |
| Content/SEO | $2.76 | $2.73 | $4.08 |
| Webinars | $1.86 | $4.25 | $3.33 |
| LinkedIn | $1.65 | $4.55 | $3.10 |
| Paid search | **$5.03 (#1)** | $0.97 | $2.27 (#5) |
| Review sites | $1.21 | $0.47 | $1.81 |

Under last-touch, paid search looks like the best channel; under every other rule it ranks near the bottom. **Today's dashboard points budget toward the wrong channel.** Review sites rank last or second to last under every rule, so cutting them is safe whichever rule you trust.

### Finding 4: Within paid search, the weakest campaign is non-brand, not brand

| Campaign | 2024 spend | Revenue per $1 (linear) | Revenue per $1 (last-touch) |
|---|---|---|---|
| Brand ("Ledgerly") | $3.63M | $2.20 | **$8.93** |
| Non-brand: expense cards | $2.60M | **$1.75** | $1.00 |
| Non-brand: AP automation | $1.30M | $3.49 | $2.21 |

Last-touch over-credits the brand campaign about 4×, but under fair credit brand is middling. **The campaign to cut first is non-brand "expense cards"**, which returns about as little as review sites. Brand bidding also protects the company name from competitors' bids, which this data cannot measure, so brand cuts need their own test.

### Finding 5: Why. Customer size and retention.
2024 signups by first-touch channel:

| Channel | Leads funded | Lost within 12 months | Large customers (51–200 staff) | Avg 12-month revenue |
|---|---|---|---|---|
| Partners | **46.9%** | **16.3%** | 24.0% | $8,538 |
| LinkedIn | 24.6% | 22.9% | **29.2%** | $7,605 |
| Webinars | 28.1% | 25.7% | 21.0% | $5,450 |
| Paid search | 15.6% | 34.8% | 11.4% | $3,188 |
| Content/SEO | 13.9% | 33.1% | 10.5% | $2,998 |
| Review sites | **6.8%** | **59.8%** | 6.0% | $1,399 |

A 51–200-employee customer earns **$15,922** in its first 12 months; a 1–10-employee customer earns **$826**, about **19× less**. Partners and LinkedIn win because they bring bigger customers who stay. Content scores well on revenue per $1 because it is cheap, not because its customers are large: it is efficient rather than high-value.

### Finding 6: Clean data changed the numbers
Without cleaning, revenue would have been overstated by **$3.4M** (a month loaded twice), spend by **$546K** (Canadian dollars counted as US dollars), and leads by **3.1%** (duplicate people and test accounts).

---

## 3. Recommendation

**Shift ~12% of the paid budget, keeping total spend flat.** At 2024 levels that is $2.6M; on 2025's $27.1M budget the same 12% is about $3.3M.

| Channel | 2024 spend | Change | $ moved (2024 base) |
|---|---|---|---|
| Review sites | $3.69M | **−30%** | −$1.11M |
| Paid search (non-brand "expense cards" first) | $7.54M | **−20%** | −$1.51M |
| Partners | $1.52M | **+70%** | +$1.06M |
| Webinars | $2.14M | **+40%** | +$0.86M |
| Content/SEO | $2.17M | **+35%** | +$0.76M |
| LinkedIn | $4.56M | hold | — |

**Expected 12-month revenue change at the same total spend:**

| If new money works at… | Revenue change |
|---|---|
| 50% of today's average (pessimistic) | +$0.5M |
| **75% (expected)** | **+$3.5M** |
| 100% (optimistic) | +$6.5M |

- **Cuts** lose revenue at each channel's full average rate. This is deliberately conservative: it assumes every dollar cut was really earning.
- **Additions** earn less than today's average because channels get less efficient as they grow.
- **Upside:** if the paid search cut comes from the expense-cards campaign ($1.75 per $1) rather than the channel average ($2.27), the expected gain rises to about **+$4.3M**.

**Next steps: a 90-day test.**
1. **Test:** apply the shift in about 20% of regions and keep the rest unchanged as the comparison group.
2. **Measure:** funded accounts and early revenue per $1 against the comparison group. Target: new money working at 75% or better.
3. **Scale:** roll out the full shift if the target is met. Test brand-bid reductions separately.
4. **Answer the open question:** can the partner program absorb +70% (enough accountants to recruit)? The test shows this directly.

---

## 4. How confident are we?

| Check | Result |
|---|---|
| **Does the ranking depend on the credit rule?** | Only last-touch changes it (Finding 3) |
| **Does it hold on data the analysis never used?** | **Yes.** H1 2025 signups give the identical ranking (table below) |
| **Are credit shares stable over time?** | Yes. Paid search linear share: 27.7% (2024) vs 27.8% (2025) |
| **Is any credit lost or double-counted?** | No. Attributed revenue = cohort revenue exactly ($68,765,924) |
| **Do other variables explain the gap?** | No. Checked and ruled out below |

**Out-of-sample check:** revenue per $1 for first-half signups, 6 months of revenue, both years measured the same way:

| Channel | H1 2024 | H1 2025 |
|---|---|---|
| Partners | $2.60 | $2.79 |
| Content/SEO | $1.99 | $2.05 |
| Webinars | $1.57 | $1.67 |
| LinkedIn | $1.43 | $1.60 |
| Paid search | $1.11 | $1.14 |
| Review sites | $0.89 | $0.87 |

**Variables checked and ruled out** (no meaningful difference across groups):

| Variable | Range across groups |
|---|---|
| Industry: % of leads funded | 17.1% – 17.8% |
| Approved accounts never funded, by channel | 24.6% – 25.9% |
| Refunds as % of revenue, by channel | 0.44% – 0.52% |

---

## 5. Data
Synthetic data generated by [`data/generate_data.py`](data/generate_data.py) (seeded, so fully reproducible). **~2.3M rows** across 5 tables, with deliberate real-world data problems:

| Table | Rows | One row is… |
|---|---|---|
| touchpoints | 1,811,339 | One marketing interaction (ad click, visit, webinar) |
| leads | 181,711 | One signup |
| accounts | 40,812 | One approved business |
| account_revenue_monthly | 282,051 | One account × one month of revenue |
| marketing_spend_daily | 11,660 | One campaign × one day of spend |

Full schema: [`data/DATA_DICTIONARY.md`](data/DATA_DICTIONARY.md). Ledgerly earns ~1.8% interchange on card spend plus a monthly subscription ($0 / $49 / $199 by plan).

---

## 6. Method

**Profile → Clean → Attribute → Value → Validate → Simulate**

| Step | What | SQL |
|---|---|---|
| Profile | Row counts, date ranges, distinct values of every messy field | notebook |
| Clean | 14 issues fixed and logged | [`01_clean.sql`](sql/01_clean.sql) |
| Attribute | Last-touch, first-touch and linear credit per funded account | [`02_analysis.sql`](sql/02_analysis.sql) |
| Value | Funnel, 12-month revenue per $1, customer-size mix | [`02_analysis.sql`](sql/02_analysis.sql) |
| Simulate | Budget-neutral shift at 3 effectiveness levels | [`03_scenario.sql`](sql/03_scenario.sql) |
| Validate | Campaign split, payback, 2025 holdout, ruled-out variables | [`04_validation.sql`](sql/04_validation.sql) |

**Attribution models**
- **Last-touch:** 100% of the credit to the final touch before signup (Ledgerly's current dashboard).
- **First-touch:** 100% to the first touch.
- **Linear:** equal credit to every touch. This is the main view, because it is simple and doesn't favor any position in the journey.

**Analysis windows**
- **Attribution:** all signups Jan 2024 – Dec 2025, with a 90-day lookback before signup.
- **Channel ROI:** the 2024 signup cohort, using each account's first 12 months of revenue against 2024 spend, so every customer gets an equal earning window.
- **Validation:** H1 2025 signups, using 6 months of revenue.

**Key SQL techniques:** window functions (`ROW_NUMBER`, `COUNT OVER`, `SUM OVER`), CTEs, CASE-based channel mapping, deduplication, `FULL OUTER JOIN`, date windows, cohort analysis.

---

## 7. Data cleaning

| # | Issue | Fix |
|---|---|---|
| 1 | 20+ spellings per channel in UTM tags | Mapped to 7 channels |
| 2 | `google`/`bing` is both paid and organic | Split by medium: `cpc` → paid search, `organic` → content/SEO |
| 3 | LinkedIn and Capterra also use `cpc` | Checked the source first, then the medium |
| 4 | 11.6% of touches have no UTMs | Labeled `direct`; listed as a limitation |
| 5 | 35,340 duplicate tracking events | Deduplicated |
| 6 | 9,000 touches for leads that don't exist | Dropped |
| 7 | ~281K touches after signup | Dropped (can't cause a signup that already happened) |
| 8 | 5,111 duplicate people (same email, different casing) | Kept the first signup |
| 9 | 600 test leads and their accounts | Removed |
| 10 | Company size in 11 formats + 7,020 missing | 3 bands + `unknown` (assumption: "50+" → 51–200) |
| 11 | June 2025 revenue loaded twice (6,712 rows) | Deduplicated |
| 12 | Refunds as negative revenue | **Kept**: real money returned |
| 13 | Spend in CAD; 18 channel names for 6 channels | Converted at 0.73; standardized |
| 14 | 12 days of LinkedIn spend missing (Mar 2025) | Flagged, not imputed (~4% of 2025 LinkedIn spend; outside the ROI window) |

| Table | Raw rows | Clean rows |
|---|---|---|
| leads | 181,711 | 176,000 |
| touchpoints | 1,811,339 | 1,485,540 |
| accounts (funded) | 40,812 | 30,289 |
| revenue | 282,051 | 275,339 |
| spend | 11,660 | 11,660 |

**Not cleaned (not used in the analysis):** `device_type` (5 spellings) and `landing_page`.

---

## 8. Why 2024 data for ROI and 2025 for validation
The question is about next year's budget, so recent data matters. But the core metric, **12 months of revenue per customer**, can't be measured on most 2025 customers yet: a December 2025 signup has had zero months to earn. Cutting the window short would hide the very thing that separates channels, retention, because partner customers churn far less than review-site customers.

Each year is used for what it can support:
- **Attribution** uses 2024 and 2025, since it doesn't need revenue time.
- **The ROI ranking** uses 2024 signups, the most recent cohort with a full 12 months.
- **Validation** uses H1 2025 signups with the 6 months available. The ranking is identical (Section 4).
- **Budget sizing** is expressed as a % of budget, so it applies to 2025's larger base ($27.1M).

---

## 9. Limitations
1. **Revenue, not profit.** Credit losses, fraud and servicing costs aren't in the data.
2. **Correlation, not causation.** Attribution shows who was present in the journey, not who caused the sale, which is why the recommendation starts with a holdout test.
3. **Diminishing returns are assumed** (50% / 75% / 100%), not measured. The test measures them.
4. **Channel capacity is unknown.** Whether partners can absorb +70% depends on recruiting accountants.
5. **Brand search protects the name from competitors**, an effect this data cannot measure.
6. **Untagged touches** (11.6%) are counted as direct, slightly under-crediting every paid channel.
7. **Timing:** assumes each year's spend drove that year's signups; spillover at the year edges roughly cancels.
8. **Churn edge:** 749 cohort accounts (5.6%) funded in Jan 2025 have 11 observable months, not 12. The effect is the same for every channel.
9. **Synthetic data:** the patterns were designed to be realistic. The value shown is the method, not a discovery.

---

## 10. Repo structure and how to reproduce
```
README.md                 This file
EXECUTIVE_SUMMARY.md      One-page summary for leadership
data/
  generate_data.py        Creates the 5 raw CSVs (~2.3M rows, seeded)
  DATA_DICTIONARY.md      Schema and known data issues
sql/
  01_clean.sql            Cleaning (14 issues)
  02_analysis.sql         Attribution, funnel, ROI, segmentation
  03_scenario.sql         Budget-shift scenario
  04_validation.sql       Campaign split, payback, 2025 holdout, ruled-out variables
notebooks/
  Marketing_Project.ipynb Profiling, cleaning and analysis (Google Colab)
outputs/                  Result tables as CSV
tableau/
  prepare_tableau_data.py Reshapes outputs for the dashboard
  *.csv                   The 4 files the dashboard uses
run_all.py                Rebuilds every table from raw data
requirements.txt
```

```bash
pip install -r requirements.txt
python data/generate_data.py          # raw CSVs into data/ (~30 seconds)
python run_all.py                     # cleaning + analysis → outputs/
python tableau/prepare_tableau_data.py
```
The raw CSVs aren't committed: `touchpoints.csv` (142 MB) exceeds GitHub's file limit. The generator recreates them exactly.

**Tools:** SQL (DuckDB, Postgres-style), Python (pandas, NumPy), Google Colab, Tableau Public

**Dashboard:** [public.tableau.com/views/LedgerlyMarketingMeasurement/Dashboard1](https://public.tableau.com/views/LedgerlyMarketingMeasurement/Dashboard1)
