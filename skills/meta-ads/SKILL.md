---
name: meta-ads
description: Manage Meta Ads campaigns, ad sets, insights, audiences, and creatives. Use when user needs to create/monitor ad campaigns, check performance, or manage audiences on Meta (Facebook/Instagram).
allowed-tools: Bash, Read
---

# Meta Ads (Marketing API v22)

Manage ad campaigns via Meta Marketing API using Python CLI.

## Prerequisites
- `META_ADS_TOKEN` in `.env` (Meta access token with `ads_management` permission)
- `META_AD_ACCOUNT_ID` in `.env` (format: `act_XXXXXXXXX`)

## Quick Commands

```bash
# Account overview
python scripts/meta_ads_handler.py account

# List campaigns
python scripts/meta_ads_handler.py campaigns
python scripts/meta_ads_handler.py campaigns --status ACTIVE

# Create campaign (always PAUSED by default)
python scripts/meta_ads_handler.py campaign-create "Summer Sale" OUTCOME_SALES --daily-budget 50000

# Update campaign
python scripts/meta_ads_handler.py campaign-update 123456 --status ACTIVE
python scripts/meta_ads_handler.py campaign-update 123456 --name "New Name"

# Delete campaign
python scripts/meta_ads_handler.py campaign-delete 123456

# Ad Sets
python scripts/meta_ads_handler.py adsets
python scripts/meta_ads_handler.py adsets --campaign-id 123456
python scripts/meta_ads_handler.py adset-create 123456 "Target LATAM" 30000 LINK_CLICKS

# Ads
python scripts/meta_ads_handler.py ads
python scripts/meta_ads_handler.py ads --adset-id 123456

# Performance Insights
python scripts/meta_ads_handler.py insights
python scripts/meta_ads_handler.py insights --date-preset last_30d --level adset
python scripts/meta_ads_handler.py insights --id 123456 --breakdowns age,gender

# Audiences
python scripts/meta_ads_handler.py audiences
python scripts/meta_ads_handler.py audience-create "Newsletter Subscribers"

# Creatives
python scripts/meta_ads_handler.py creatives
```

## Campaign Objectives (v22)
- `OUTCOME_AWARENESS` — Brand awareness, reach
- `OUTCOME_TRAFFIC` — Website/app traffic
- `OUTCOME_ENGAGEMENT` — Post engagement, page likes
- `OUTCOME_LEADS` — Lead generation forms
- `OUTCOME_APP_PROMOTION` — App installs
- `OUTCOME_SALES` — Conversions, catalog sales

## Budgets
- Values in **cents** (e.g., 50000 = $500.00 in account currency)
- New campaigns are always created **PAUSED** for safety

## Date Presets
`today`, `yesterday`, `last_7d`, `last_30d`, `this_month`, `last_month`, `last_quarter`

## Insight Breakdowns
`age`, `gender`, `country`, `region`, `placement`, `device_platform`, `publisher_platform`

## Output Format

```json
{
  "success": true,
  "data": { ... }
}
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `190` | Invalid/expired token | Refresh META_ADS_TOKEN |
| `100` | Invalid parameter | Check field names and values |
| `2635` | Spending limit reached | Check account spend_cap |
| `1487390` | Ad account disabled | Check account_status via `account` command |
