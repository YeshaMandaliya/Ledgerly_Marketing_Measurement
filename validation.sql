-- Extra checks on the recommendation.
-- Run these after the notebook, since they use lead_journeys, account_12m and the clean_ tables.

-- 1. Paid search by campaign: which campaign should take the cut?
CREATE OR REPLACE TABLE paid_search_campaigns AS
WITH sp AS (
 SELECT campaign, SUM(spend_usd) AS spend_2024
 FROM clean_spend
 WHERE spend_date < DATE '2025-01-01' AND channel = 'paid_search'
 GROUP BY campaign
),
rv AS (
 SELECT j.utm_campaign AS campaign,
  SUM(a.rev_12m / j.n_touches) AS rev_linear,
  SUM(CASE WHEN j.touch_n_rev = 1 THEN a.rev_12m ELSE 0 END) AS rev_last
 FROM lead_journeys j
 JOIN account_12m a ON a.lead_id = j.lead_id
 WHERE j.channel = 'paid_search'
 GROUP BY j.utm_campaign
)
SELECT sp.campaign,
 ROUND(sp.spend_2024) AS spend_2024,
 ROUND(rv.rev_linear / sp.spend_2024, 2) AS rpd_linear,
 ROUND(rv.rev_last / sp.spend_2024, 2) AS rpd_last_touch
FROM sp
JOIN rv ON rv.campaign = sp.campaign;

-- 2. Payback: how many months of revenue it takes to earn back the acquisition cost
CREATE OR REPLACE TABLE channel_payback AS
WITH rev AS (
 SELECT j.channel, SUM(1.0 / j.n_touches) AS accounts, SUM(a.rev_12m / j.n_touches) AS rev_12m
 FROM lead_journeys j
 JOIN account_12m a ON a.lead_id = j.lead_id
 GROUP BY j.channel
),
sp AS (
 SELECT channel, SUM(spend_usd) AS spend_2024
 FROM clean_spend
 WHERE spend_date < DATE '2025-01-01'
 GROUP BY channel
)
SELECT r.channel,
 ROUND(sp.spend_2024 / r.accounts) AS cac,
 ROUND(r.rev_12m / r.accounts) AS rev_12m_per_account,
 ROUND((sp.spend_2024 / r.accounts) / ((r.rev_12m / r.accounts) / 12), 1) AS payback_months
FROM rev r
JOIN sp ON sp.channel = r.channel;

-- 3. Does the ranking hold for 2025 signups?
-- Most 2025 customers don't have 12 months of revenue yet, so this compares H1 signups
-- with 6 months of revenue, measured the same way for both years.
CREATE OR REPLACE TABLE holdout_2025 AS
WITH acct AS (
 SELECT a.account_id, a.lead_id, l.signup_ts, SUM(r.total_revenue_usd) AS rev_6m
 FROM clean_accounts a
 JOIN clean_leads l ON l.lead_id = a.lead_id
 LEFT JOIN clean_revenue r
  ON r.account_id = a.account_id
 AND r.revenue_month < DATE_TRUNC('month', a.funded_date) + INTERVAL 6 MONTH
 GROUP BY a.account_id, a.lead_id, l.signup_ts
),
rev AS (
 SELECT j.channel, YEAR(c.signup_ts) AS yr, SUM(c.rev_6m / j.n_touches) AS rev_6m
 FROM lead_journeys j
 JOIN acct c ON c.lead_id = j.lead_id
 WHERE MONTH(c.signup_ts) <= 6
 GROUP BY j.channel, YEAR(c.signup_ts)
),
sp AS (
 SELECT channel, YEAR(spend_date) AS yr, SUM(spend_usd) AS spend
 FROM clean_spend
 WHERE MONTH(spend_date) <= 6
 GROUP BY channel, YEAR(spend_date)
)
SELECT r.channel,
 ROUND(MAX(CASE WHEN r.yr = 2024 THEN r.rev_6m / sp.spend END), 2) AS rpd_6m_h1_2024,
 ROUND(MAX(CASE WHEN r.yr = 2025 THEN r.rev_6m / sp.spend END), 2) AS rpd_6m_h1_2025
FROM rev r
JOIN sp ON sp.channel = r.channel AND sp.yr = r.yr
GROUP BY r.channel;

-- 4. Things I checked that turned out not to matter
-- funded % by industry
SELECT l.industry, ROUND(100.0 * COUNT(a.account_id) / COUNT(*), 1) AS funded_pct
FROM clean_leads l
LEFT JOIN clean_accounts a ON a.lead_id = l.lead_id
WHERE l.signup_ts < TIMESTAMP '2025-01-01'
GROUP BY l.industry
ORDER BY funded_pct;

-- approved but never funded, by first-touch channel
SELECT f.channel,
 ROUND(100.0 * SUM(CASE WHEN a.funded_date IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) AS never_funded_pct
FROM accounts a
JOIN lead_journeys f ON f.lead_id = a.lead_id AND f.touch_n = 1
GROUP BY f.channel
ORDER BY never_funded_pct;

-- refunds as a share of revenue, by first-touch channel
SELECT f.channel,
 ROUND(100.0 * SUM(CASE WHEN r.interchange_revenue_usd < 0 THEN -r.interchange_revenue_usd ELSE 0 END) / SUM(r.total_revenue_usd), 2) AS refund_pct
FROM clean_revenue r
JOIN clean_accounts a ON a.account_id = r.account_id
JOIN lead_journeys f ON f.lead_id = a.lead_id AND f.touch_n = 1
GROUP BY f.channel
ORDER BY refund_pct;

-- 5. Paid spend by year (the budget shift is sized as a % of this)
SELECT YEAR(spend_date) AS yr, ROUND(SUM(spend_usd)) AS paid_spend
FROM clean_spend
GROUP BY YEAR(spend_date)
ORDER BY yr;
