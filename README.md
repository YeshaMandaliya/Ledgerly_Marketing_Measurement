# Ledgerly Marketing Measurement

I built this project to practice marketing measurement on a realistic, messy dataset. Ledgerly is a made-up B2B fintech that sells expense cards and bill pay to small businesses. It spent about $48.7M on paid marketing across 2024 and 2025, and its dashboard gives all the credit for a new customer to the last click before signup. On that view, paid search looks like the best channel.

The question I wanted to answer: which channels should get more or less of next year's budget if the goal is revenue, not just signups, and total spend stays the same?

Dashboard: https://public.tableau.com/views/LedgerlyMarketingMeasurement/Dashboard1

Short version for leadership: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)

## What I found

Last-click credit gives paid search far more credit than it earns. Under last-click, paid search gets 56% of the 30,289 funded accounts. When every touch in the journey gets an equal share (linear attribution), it drops to 28%. Most of its last-click wins (14,296 of 17,037) come from the brand campaign, which is mostly people Googling "Ledgerly" after another channel already convinced them.

Revenue per dollar varies a lot by channel. Using 2024 signups and their first 12 months of revenue:

| Channel | Revenue per $1 | Months to pay back acquisition cost |
|---|---|---|
| Partners | $5.59 | 2.1 |
| Content/SEO | $4.08 | 2.9 |
| Webinars | $3.33 | 3.6 |
| LinkedIn | $3.10 | 3.9 |
| Paid search | $2.27 | 5.3 |
| Review sites | $1.81 | 6.6 |

The ranking only flips under last-click. Paid search comes out on top under last-click ($5.03 per $1) but near the bottom under first-touch and linear. Review sites are near the bottom under all three.

Inside paid search, the weakest campaign is not brand. It's the non-brand "expense cards" campaign at $1.75 per $1 (brand is $2.20, AP automation is $3.49). So if paid search gets cut, that campaign should go first. I left brand alone because brand bidding also protects the company name from competitors, and this data can't measure that.

The difference comes down to customer quality. Partners convert 46.9% of their leads and only 16% of those customers leave within a year. Review sites convert 6.8% and lose 60%. A company with 51-200 employees brings in about $15,900 in its first year, compared with about $830 for a company with 1-10 employees. Partners and LinkedIn bring in the most of the bigger companies.

## Recommendation

Move roughly 12% of the paid budget, keeping total spend flat. At 2024 levels that's about $2.6M; on the 2025 budget it would be about $3.3M.

- Review sites: -30%
- Paid search: -20%, starting with the non-brand expense cards campaign
- Partners: +70%
- Webinars: +40%
- Content/SEO: +35%
- LinkedIn: no change

If new money works at 75% of each channel's current average (channels usually get less efficient as you spend more), this adds about $3.5M in 12-month revenue. The range is +$0.5M at 50% and +$6.5M at 100%. I assumed the cuts lose revenue at each channel's full average rate, so the estimate leans conservative. If the paid search cut comes from the expense cards campaign specifically, the gain is closer to $4.3M.

I'd test this before committing the full amount: run the shift in about 20% of regions for 90 days, keep the rest as a comparison group, and scale up if the new money performs at 75% or better.

## How I know it holds up

- The 2025 signups, which I didn't use for the main analysis, give the same channel ranking (using 6 months of revenue, since most 2025 customers don't have a full year yet).
- Linear credit shares barely move between years (paid search: 27.7% in 2024, 27.8% in 2025).
- Every funded account gets exactly one unit of credit in each model, and the revenue I attributed to channels adds up to the cohort total.
- I checked whether industry, approval drop-off or refund rates could explain the gap. They don't; they're nearly flat across groups.

## Why I used 2024 for the main numbers

The budget question is about next year, so recent data matters. But the main metric is 12 months of revenue per customer, and most 2025 customers haven't been around that long. A customer who signed up in December 2025 has had no time to earn anything. Cutting the window short would hide retention, which is a big part of why partners do so well. So I used 2024 signups for the ranking and the 2025 signups to check it.

## The data

The data is synthetic. I generated it with [generate_data.py](generate_data.py) and deliberately made it messy. It has about 2.3M rows across five tables: touchpoints (1.8M), leads, accounts, monthly revenue and daily spend. The raw CSVs are in the [data](data/) folder, zipped one table per file to stay under GitHub's upload limit. The columns are described in [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

## Cleaning

Most of the work in [Marketing_Project.ipynb](Marketing_Project.ipynb) is cleaning. The main issues I found and fixed:

- UTM tags spelled 20+ different ways per channel. "google" can be paid or organic depending on the medium, and LinkedIn and Capterra also use "cpc", so I mapped by source first, then by medium.
- 35,340 duplicate tracking events and 9,000 touches for leads that don't exist.
- About 281K touches that happened after signup. They can't have caused the signup, so I dropped them.
- 5,111 people who signed up twice with different email casing, plus 600 internal test leads.
- Company size written 11 different ways. I grouped it into three bands and assumed "50+" means 51-200.
- June 2025 revenue loaded twice.
- Some spend billed in CAD (converted at 0.73) and 18 different names for 6 channels.
- 12 days of missing LinkedIn spend in March 2025. I flagged it rather than filling it in; it falls outside the 2024 window used for ROI.

I kept refunds in, since they're real money going back out. Without cleaning, revenue would have been overstated by $3.4M and spend by $546K.

## Limitations

- This is revenue, not profit. Credit losses, fraud and servicing costs aren't in the data.
- Attribution shows which channels were part of the journey, not which ones caused the sale. That's why I'd test before moving the full budget.
- The 50/75/100% effectiveness levels are assumptions.
- I don't know if the partner program can actually absorb 70% more budget. That depends on recruiting more accountants.
- 11.6% of touches had no UTM tags, so they count as direct.
- The data is synthetic, so the patterns were designed. The point of the project is the method.

## Files

- `README.md` - this file
- `EXECUTIVE_SUMMARY.md` - one-page version
- `Marketing_Project.ipynb` - profiling, cleaning and analysis in SQL (DuckDB in Google Colab)
- `validation.sql` - the extra checks (campaign split, payback, 2025 holdout), run after the notebook
- `generate_data.py` - creates the raw data
- `DATA_DICTIONARY.md` - table and column descriptions
- `data/` - the raw CSVs, one zip per table

Tools: SQL (DuckDB), Python, Google Colab, Tableau Public
