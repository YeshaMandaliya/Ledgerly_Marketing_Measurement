# Generates the synthetic Ledgerly dataset (Jan 2024 - Dec 2025).
# Ledgerly is a made-up B2B fintech selling expense cards and bill pay to small businesses.
# The data has data-quality problems added on purpose.
# Run: python generate_data.py (writes the CSVs to a data/ folder)
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

START, END = pd.Timestamp("2024-01-01"), pd.Timestamp("2025-12-31")
N_LEADS = 176_000

CHANNELS = ["paid_search", "linkedin", "content_seo", "partner", "webinar", "review_sites", "direct"]

# ---- "True" behavior by origin (first-touch) channel ----
ORIGIN_MIX = dict(paid_search=.20, linkedin=.15, content_seo=.19, partner=.06, webinar=.08, review_sites=.25, direct=.07)
P_FUND = dict(paid_search=.16, linkedin=.23, content_seo=.15, partner=.45, webinar=.27, review_sites=.07, direct=.17)
VOL_MULT = dict(paid_search=1.0, linkedin=1.35, content_seo=.95, partner=1.6, webinar=1.15, review_sites=.70, direct=1.0)
CHURN = dict(paid_search=.035, linkedin=.022, content_seo=.033, partner=.014, webinar=.024, review_sites=.075, direct=.03)
SIZE_MIX = { # P(1-10, 11-50, 51-200) by origin
    "paid_search": [.55, .35, .10], "linkedin": [.30, .45, .25], "content_seo": [.60, .32, .08],
    "partner": [.35, .45, .20], "webinar": [.40, .42, .18], "review_sites": [.70, .25, .05], "direct": [.55, .35, .10]}
SIZES = ["1-10", "11-50", "51-200"]
SIZE_VOL = {"1-10": 4_000, "11-50": 16_000, "51-200": 55_000} # monthly card volume (USD)
SIZE_FEE = {"1-10": 0, "11-50": 49, "51-200": 199} # monthly subscription
SIZE_FUND_MULT = {"1-10": .85, "11-50": 1.1, "51-200": 1.3}

# ---- Messy UTM variants per channel: (utm_source options, utm_medium options) ----
UTM = {
    "paid_search": (["google", "Google", "google_ads", "adwords", "bing"], ["cpc", "CPC", "ppc", "paid_search"]),
    "linkedin": (["linkedin", "LinkedIn", "li", "lnkd"], ["paid_social", "paidsocial", "Paid-Social", "cpc"]),
    "content_seo": (["google", "bing", "blog", "Organic"], ["organic", "seo", "Organic", "content"]),
    "partner": (["partner", "Partner", "accountant_portal", "referral"], ["referral", "partner", "Referral"]),
    "webinar": (["webinar", "Webinar", "on24", "zoom"], ["event", "webinar", "Event"]),
    "review_sites": (["g2", "G2", "capterra", "Capterra", "getapp"], ["review", "affiliate", "cpc", "Review"]),
    "email": (["hubspot", "email", "Email"], ["email", "Email", "nurture"]),
}
CAMPAIGNS = {
    "paid_search": ["brand_ledgerly", "nonbrand_expense_cards", "nonbrand_ap_automation"],
    "linkedin": ["li_cfo_targeting", "li_lookalike_q", "li_retarget"],
    "content_seo": ["blog_expense_policy", "blog_ap_guide", "seo_comparison_pages"],
    "partner": ["accountant_program", "bookkeeper_referral"],
    "webinar": ["webinar_month_end_close", "webinar_cash_flow"],
    "review_sites": ["g2_listing", "capterra_ppl", "getapp_ppl"],
    "email": ["nurture_onboarding", "nurture_upsell"],
}


def pick(options_by_key, keys):
    """Vectorized: for each key, pick a random option from its list."""
    out = np.empty(len(keys), dtype=object)
    for k, opts in options_by_key.items():
        m = keys == k
        if m.any():
            out[m] = rng.choice(opts, m.sum())
    return out


# ---- LEADS
days = (END - START).days + 1
# growth trend + Q1/Q4 seasonality
day_idx = np.arange(days)
w = (1 + day_idx / days * 0.6) * (1 + 0.15 * np.cos(2 * np.pi * day_idx / 365))
signup_day = rng.choice(days, N_LEADS, p=w / w.sum())
signup_ts = START + pd.to_timedelta(signup_day, "D") + pd.to_timedelta(rng.integers(0, 86400, N_LEADS), "s")

origin = rng.choice(list(ORIGIN_MIX), N_LEADS, p=list(ORIGIN_MIX.values()))
size = np.empty(N_LEADS, dtype=object)
for ch, p in SIZE_MIX.items():
    m = origin == ch
    size[m] = rng.choice(SIZES, m.sum(), p=p)

industries = ["construction", "professional_services", "retail", "healthcare", "tech", "restaurants", "logistics"]
lead_id = np.arange(100001, 100001 + N_LEADS)
leads = pd.DataFrame({
    "lead_id": lead_id,
    "email": [f"user{i}@company{i % 90000}.com" for i in lead_id],
    "company_name": [f"Company {i % 90000}" for i in lead_id],
    "company_size": size,
    "industry": rng.choice(industries, N_LEADS),
    "signup_ts": signup_ts,
})
truth = pd.DataFrame({"lead_id": lead_id, "origin": origin, "size": size})

# ---- TOUCHPOINTS
other_mix = np.array([.30, .16, .18, .04, .10, .17, .05]) # middle-touch channel mix (incl. direct)
n_pre = 1 + rng.poisson(np.where(np.isin(origin, ["linkedin", "webinar", "partner"]), 8.5, 7.0))
n_post = rng.poisson(1.6, N_LEADS)

# pre-signup touches
rep = np.repeat(np.arange(N_LEADS), n_pre)
pos = np.concatenate([np.arange(n) for n in n_pre])
last = pos == (n_pre[rep] - 1)
first = pos == 0
ch = rng.choice(CHANNELS, len(rep), p=other_mix)
same = rng.random(len(rep)) < 0.35
ch = np.where(same, origin[rep], ch)
ch = np.where(first, origin[rep], ch)
# last touch before signup: people google "Ledgerly" -> brand search captures credit
brand_last = last & (rng.random(len(rep)) < 0.45) & ~first
ch = np.where(brand_last, "paid_search", ch)
lookback = rng.uniform(0, 60, N_LEADS) # journey length in days
frac = np.where(n_pre[rep] > 1, pos / np.maximum(n_pre[rep] - 1, 1), 1.0)
offset_days = lookback[rep] * (1 - frac) + rng.uniform(0, 0.02, len(rep))
pre_ts = leads.signup_ts.values[rep] - pd.to_timedelta(offset_days * 86400 + 30, "s").values
camp = pick(CAMPAIGNS, ch)
camp = np.where(brand_last, "brand_ledgerly", camp)

# post-signup touches (must be excluded from attribution)
rep2 = np.repeat(np.arange(N_LEADS), n_post)
ch2 = rng.choice(["email", "paid_search", "direct", "linkedin"], len(rep2), p=[.5, .25, .15, .10])
post_ts = leads.signup_ts.values[rep2] + pd.to_timedelta(rng.uniform(0.01, 90, len(rep2)) * 86400, "s").values
camp2 = pick(CAMPAIGNS, ch2)

tp = pd.DataFrame({
    "lead_id": np.concatenate([lead_id[rep], lead_id[rep2]]),
    "event_ts": np.concatenate([pre_ts, post_ts]),
    "channel_true": np.concatenate([ch, ch2]),
    "utm_campaign": np.concatenate([camp, camp2]),
})
tp["utm_source"] = pick({k: v[0] for k, v in UTM.items()}, tp.channel_true.values)
tp["utm_medium"] = pick({k: v[1] for k, v in UTM.items()}, tp.channel_true.values)
d = tp.channel_true == "direct"
tp.loc[d, ["utm_source", "utm_medium", "utm_campaign"]] = None
# Mess: ~5% of tagged touches lost their UTMs (broken links)
lost = (~d) & (rng.random(len(tp)) < 0.05)
tp.loc[lost, ["utm_source", "utm_medium", "utm_campaign"]] = None
tp["landing_page"] = np.where(tp.channel_true == "webinar", "/webinars", rng.choice(
    ["/", "/pricing", "/expense-cards", "/bill-pay", "/blog", "/compare"], len(tp)))
tp["device_type"] = rng.choice(["desktop", "mobile", "tablet", "Desktop", "MOBILE"], len(tp), p=[.55, .33, .04, .05, .03])
# Mess: ~2% exact duplicate events (tracking fired twice)
dups = tp.sample(frac=0.02, random_state=1)
# Mess: orphan touches whose lead_id does not exist in leads
orph = tp.sample(n=9000, random_state=2).copy()
orph["lead_id"] = rng.integers(900001, 999999, len(orph))
tp = pd.concat([tp, dups, orph]).sort_values("event_ts").reset_index(drop=True)
tp.insert(0, "touch_id", np.arange(1, len(tp) + 1))
tp["event_ts"] = pd.to_datetime(tp.event_ts).dt.strftime("%Y-%m-%d %H:%M:%S")
tp = tp[(tp.event_ts >= "2023-11-01") & (tp.event_ts <= "2026-03-31 23:59:59")]

# ---- ACCOUNTS
pf = np.array([P_FUND[o] for o in origin]) * np.array([SIZE_FUND_MULT[s] for s in size])
approved = rng.random(N_LEADS) < np.minimum(pf / 0.75, 0.95)
funded = approved & (rng.random(N_LEADS) < 0.75)
approved_date = leads.signup_ts + pd.to_timedelta(rng.integers(1, 10, N_LEADS), "D")
funded_date = approved_date + pd.to_timedelta(rng.integers(1, 21, N_LEADS), "D")
acc = pd.DataFrame({
    "lead_id": lead_id, "approved_date": approved_date.dt.date,
    "funded_date": np.where(funded, funded_date.dt.date, None),
    "plan_tier": [{"1-10": "starter", "11-50": "growth", "51-200": "scale"}[s] for s in size],
})[approved].reset_index(drop=True)
acc = acc[pd.to_datetime(acc.approved_date) <= END].reset_index(drop=True)
acc.insert(0, "account_id", np.arange(500001, 500001 + len(acc)))

# ---- REVENUE (monthly)
fa = acc.dropna(subset=["funded_date"]).merge(truth, on="lead_id")
rows = []
end_m = pd.Period("2025-12", "M")
closed = {}
for r in fa.itertuples(index=False):
    m = pd.Period(r.funded_date, "M")
    base = SIZE_VOL[r.size] * VOL_MULT[r.origin] * rng.lognormal(0, 0.6)
    hz = CHURN[r.origin]
    k = 0
    while m <= end_m:
        ramp = min(1.0, 0.4 + 0.2 * k)
        vol = base * ramp * rng.lognormal(0, 0.25)
        rows.append((r.account_id, m.start_time.date(), round(vol, 2), round(vol * 0.018, 2), SIZE_FEE[r.size]))
        if rng.random() < hz:
            closed[r.account_id] = m.end_time.date()
            break
        m += 1
        k += 1
rev = pd.DataFrame(rows, columns=["account_id", "revenue_month", "card_volume_usd",
                                  "interchange_revenue_usd", "subscription_revenue_usd"])
# Mess: chargebacks/refunds -> ~1.5% rows negative interchange
neg = rng.random(len(rev)) < 0.015
rev.loc[neg, "interchange_revenue_usd"] = -(rev.loc[neg, "interchange_revenue_usd"] * rng.uniform(.1, .6, neg.sum())).round(2)
# Mess: June 2025 partially loaded twice (ETL re-run)
jun = rev[(rev.revenue_month == pd.Timestamp("2025-06-01").date())].sample(frac=0.4, random_state=3)
rev = pd.concat([rev, jun]).sort_values(["account_id", "revenue_month"]).reset_index(drop=True)

acc["account_status"] = np.where(acc.account_id.isin(closed), "closed",
                                 np.where(acc.funded_date.isna(), "approved_not_funded", "active"))
acc["closed_date"] = acc.account_id.map(closed)

# ---- LEAD MESS
# company_size formats vary + some missing
fmt = {"1-10": ["1-10", "1 to 10", "1-10 employees", "<10"],
       "11-50": ["11-50", "11 to 50", "11-50 employees"],
       "51-200": ["51-200", "51 to 200", "51-200 employees", "50+"]}
leads["company_size"] = [rng.choice(fmt[s]) for s in leads.company_size]
leads.loc[rng.random(N_LEADS) < 0.04, "company_size"] = None
# duplicate leads: same person signs up twice, email casing differs, new lead_id, later timestamp
dl = leads.sample(n=5200, random_state=4).copy()
dl["email"] = dl.email.str.upper().where(rng.random(len(dl)) < .5, dl.email.str.title())
dl["signup_ts"] = dl.signup_ts + pd.to_timedelta(rng.integers(1, 20, len(dl)), "D")
dl["lead_id"] = np.arange(300001, 300001 + len(dl))
# test leads created by internal QA
tl = leads.sample(n=600, random_state=5).copy()
tl["lead_id"] = np.arange(400001, 400001 + len(tl))
tl["email"] = [f"qa+{i}@ledgerly.com" for i in range(len(tl))]
tl["company_name"] = "TEST - do not use"
leads = pd.concat([leads, dl, tl]).sort_values("signup_ts").reset_index(drop=True)
leads = leads[leads.signup_ts <= END + pd.Timedelta("23:59:59")]
leads["signup_ts"] = leads.signup_ts.dt.strftime("%Y-%m-%d %H:%M:%S")
# test accounts
ta = pd.DataFrame({"account_id": np.arange(800001, 800301), "lead_id": tl.lead_id.values[:300],
                   "approved_date": pd.to_datetime(tl.signup_ts.values[:300]).date, "funded_date": pd.to_datetime(tl.signup_ts.values[:300]).date,
                   "plan_tier": "scale", "account_status": "active", "closed_date": None})
acc = pd.concat([acc, ta]).reset_index(drop=True)

# ---- SPEND (daily by campaign)
SPEND_SHARE = dict(paid_search=.35, linkedin=.21, review_sites=.17, webinar=.10, partner=.07, content_seo=.10)
TOTAL = 48_000_000
SPEND_NAME = {"paid_search": ["Paid Search", "paid_search", "Google Ads"],
              "linkedin": ["LinkedIn", "linkedin_ads", "LinkedIn Ads"],
              "review_sites": ["Review Sites", "review_sites", "G2/Capterra"],
              "webinar": ["Webinars", "webinar", "Events & Webinars"],
              "partner": ["Partner Program", "partner", "Accountant Partners"],
              "content_seo": ["Content/SEO", "content", "SEO"]}
dates = pd.date_range(START, END)
sp = []
for chn, share in SPEND_SHARE.items():
    camps = [c for c in CAMPAIGNS[chn]]
    cw = rng.dirichlet(np.ones(len(camps)) * 3)
    daily = TOTAL * share / len(dates) * (w / w.mean())
    for c, cwi in zip(camps, cw):
        amt = daily * cwi * rng.lognormal(0, 0.2, len(dates))
        for dt, a in zip(dates, amt):
            sp.append((dt.date(), rng.choice(SPEND_NAME[chn]), c, round(a, 2)))
spend = pd.DataFrame(sp, columns=["spend_date", "channel", "campaign", "spend_amount"])
spend["currency"] = "USD"
# Mess: Canadian LinkedIn/search campaigns billed in CAD (~10% of those rows)
cad = spend.campaign.isin(["li_lookalike_q", "nonbrand_ap_automation"]) & (rng.random(len(spend)) < .35)
spend.loc[cad, "spend_amount"] = (spend.loc[cad, "spend_amount"] / 0.73).round(2)
spend.loc[cad, "currency"] = "CAD"
# Mess: 12 missing days of LinkedIn spend (connector outage, Mar 2025)
gap = spend.campaign.str.startswith("li_") & (pd.to_datetime(spend.spend_date).between("2025-03-03", "2025-03-14"))
spend = spend[~gap].reset_index(drop=True)

# ---- WRITE
tp.drop(columns="channel_true").to_csv(OUT / "touchpoints.csv", index=False)
leads.to_csv(OUT / "leads.csv", index=False)
acc.to_csv(OUT / "accounts.csv", index=False)
rev.to_csv(OUT / "account_revenue_monthly.csv", index=False)
spend.to_csv(OUT / "marketing_spend_daily.csv", index=False)
for n, df in [("touchpoints", tp), ("leads", leads), ("accounts", acc), ("revenue", rev), ("spend", spend)]:
    print(f"{n:12s} {len(df):>10,} rows")
