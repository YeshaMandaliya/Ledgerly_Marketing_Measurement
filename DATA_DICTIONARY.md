# Data Dictionary

Ledgerly is a fictional B2B fintech selling expense cards and bill pay to small businesses (1-200 employees). The data covers Jan 2024 to Dec 2025 and is synthetic. It earns about 1.8% interchange on card spend plus a monthly subscription ($0, $49 or $199 depending on plan).

The tables connect like this: touchpoints.lead_id goes to leads.lead_id, which goes to accounts.lead_id. accounts.account_id goes to account_revenue_monthly.account_id. Spend doesn't link to individual leads, only by channel and date.

## touchpoints.csv (1,811,339 rows)

One row per marketing interaction (ad click, website visit, webinar).

- touch_id - row id
- lead_id - who interacted
- event_ts - timestamp (UTC)
- utm_campaign - campaign name, blank if untagged
- utm_source - e.g. google, linkedin, g2 (inconsistent spelling and casing)
- utm_medium - e.g. cpc, organic, paid_social (also inconsistent)
- landing_page - first page viewed
- device_type - desktop, mobile or tablet (inconsistent casing)

## leads.csv (181,711 rows)

One row per signup.

- lead_id
- email - lowercase it to find duplicates
- company_name
- company_size - employee band, written several different ways, some blank
- industry
- signup_ts - when the lead signed up (UTC)

## accounts.csv (40,812 rows)

One row per approved business.

- account_id
- lead_id
- approved_date
- funded_date - blank means approved but never funded
- plan_tier - starter, growth or scale
- account_status - active, closed or approved_not_funded
- closed_date - when the account churned, if it did

## account_revenue_monthly.csv (282,051 rows)

One row per account per month.

- account_id
- revenue_month - first day of the month
- card_volume_usd - total card spend that month
- interchange_revenue_usd - Ledgerly's cut; negative values are refunds or chargebacks
- subscription_revenue_usd - plan fee

## marketing_spend_daily.csv (11,660 rows)

One row per campaign per day.

- spend_date
- channel - inconsistent names ("Google Ads", "paid_search", "Paid Search", etc.)
- campaign - matches utm_campaign in touchpoints
- spend_amount
- currency - USD or CAD

## Channels

paid_search, linkedin, content_seo, partner (accountant referrals), webinar, review_sites (G2, Capterra, GetApp), email (no spend), and direct (no UTM tags).

Watch out for: google or bing with cpc is paid search, but google or bing with organic is content/SEO. linkedin with cpc is still LinkedIn, and capterra with cpc is still review sites.

## Known data problems

1. UTM source and medium spelled many different ways
2. About 5% of tagged clicks lost their UTMs
3. About 2% of touchpoints recorded twice
4. About 9,000 touchpoints with a lead_id that isn't in leads
5. Touches after signup (can't have caused the signup)
6. About 5,100 people who signed up twice with different email casing
7. Internal test leads (@ledgerly.com emails, company "TEST - do not use") and their accounts
8. company_size in inconsistent formats, about 4% blank
9. Negative interchange rows (refunds, keep them)
10. About 40% of June 2025 revenue rows loaded twice
11. Two campaigns partly billed in CAD (use 1 CAD = 0.73 USD)
12. LinkedIn spend missing from 2025-03-03 to 2025-03-14
13. Three different names for each channel in the spend table
