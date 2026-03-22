#!/usr/bin/env python3
"""
Meta Ads (Marketing API) handler for Hive.
Manage campaigns, ad sets, ads, insights, and audiences.
Uses Graph API v22.0 directly via HTTP requests.

Env vars:
  META_ADS_TOKEN     - Meta access token with ads_management permission
  META_AD_ACCOUNT_ID - Ad account ID (format: act_XXXXXXXXX)
"""

import os
import sys
import json
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv()

GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def get_config() -> tuple[str, str]:
    token = os.environ.get("META_ADS_TOKEN")
    account_id = os.environ.get("META_AD_ACCOUNT_ID")

    if not token:
        raise ValueError("META_ADS_TOKEN not set in environment")
    if not account_id:
        raise ValueError("META_AD_ACCOUNT_ID not set in environment")

    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"

    return token, account_id


def api_call(
    endpoint: str,
    params: Optional[dict] = None,
    data: Optional[dict] = None,
    method: str = "GET",
) -> dict:
    """Make a Graph API call."""
    token, _ = get_config()

    url = f"{GRAPH_API_BASE}/{endpoint}"

    if method == "GET" and params:
        params["access_token"] = token
        url = f"{url}?{urlencode(params)}"
        body = None
        headers = {}
    else:
        url = f"{url}?access_token={token}" if "?" not in url else url
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data).encode("utf-8") if data else None
        if not data and params:
            params["access_token"] = token
            url = f"{GRAPH_API_BASE}/{endpoint}?{urlencode(params)}"

    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return {"success": True, "data": result}
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            error_msg = error_data.get("error", {}).get("message", error_body)
        except Exception:
            error_msg = error_body
        return {"success": False, "error": f"HTTP {e.code}: {error_msg}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Campaigns ---


def campaigns_list(status: Optional[str] = None, limit: int = 25) -> dict:
    """List campaigns in the ad account."""
    _, account_id = get_config()
    params = {
        "fields": "id,name,status,objective,daily_budget,lifetime_budget,created_time,updated_time",
        "limit": str(limit),
    }
    if status:
        params["effective_status"] = json.dumps([status.upper()])
    return api_call(f"{account_id}/campaigns", params=params)


def campaign_create(
    name: str,
    objective: str,
    status: str = "PAUSED",
    daily_budget: Optional[int] = None,
    lifetime_budget: Optional[int] = None,
) -> dict:
    """Create a new campaign (PAUSED by default for safety)."""
    _, account_id = get_config()
    params = {
        "name": name,
        "objective": objective.upper(),
        "status": status.upper(),
        "special_ad_categories": "[]",
    }
    if daily_budget:
        params["daily_budget"] = str(daily_budget)
    if lifetime_budget:
        params["lifetime_budget"] = str(lifetime_budget)
    return api_call(f"{account_id}/campaigns", params=params, method="POST")


def campaign_update(campaign_id: str, **kwargs) -> dict:
    """Update a campaign field (name, status, daily_budget, etc.)."""
    params = {k: str(v) if not isinstance(v, str) else v for k, v in kwargs.items()}
    return api_call(campaign_id, params=params, method="POST")


def campaign_delete(campaign_id: str) -> dict:
    """Delete (archive) a campaign."""
    return api_call(campaign_id, method="DELETE")


# --- Ad Sets ---


def adsets_list(
    campaign_id: Optional[str] = None, status: Optional[str] = None, limit: int = 25
) -> dict:
    """List ad sets, optionally filtered by campaign."""
    _, account_id = get_config()
    parent = campaign_id or account_id
    params = {
        "fields": "id,name,status,campaign_id,daily_budget,lifetime_budget,targeting,optimization_goal,billing_event,start_time,end_time",
        "limit": str(limit),
    }
    if status:
        params["effective_status"] = json.dumps([status.upper()])
    return api_call(f"{parent}/adsets", params=params)


def adset_create(
    campaign_id: str,
    name: str,
    daily_budget: int,
    optimization_goal: str,
    billing_event: str = "IMPRESSIONS",
    targeting: Optional[str] = None,
    status: str = "PAUSED",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """Create an ad set."""
    _, account_id = get_config()
    params = {
        "campaign_id": campaign_id,
        "name": name,
        "daily_budget": str(daily_budget),
        "optimization_goal": optimization_goal.upper(),
        "billing_event": billing_event.upper(),
        "status": status.upper(),
    }
    if targeting:
        params["targeting"] = targeting
    else:
        params["targeting"] = json.dumps({"geo_locations": {"countries": ["AR"]}, "age_min": 18, "age_max": 65})
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    return api_call(f"{account_id}/adsets", params=params, method="POST")


# --- Ads ---


def ads_list(
    adset_id: Optional[str] = None, status: Optional[str] = None, limit: int = 25
) -> dict:
    """List ads, optionally filtered by ad set."""
    _, account_id = get_config()
    parent = adset_id or account_id
    params = {
        "fields": "id,name,status,adset_id,creative{id,name,title,body,image_url,thumbnail_url}",
        "limit": str(limit),
    }
    if status:
        params["effective_status"] = json.dumps([status.upper()])
    return api_call(f"{parent}/ads", params=params)


# --- Insights ---


def insights(
    object_id: Optional[str] = None,
    date_preset: str = "last_7d",
    level: str = "campaign",
    fields: Optional[str] = None,
    breakdowns: Optional[str] = None,
    limit: int = 50,
) -> dict:
    """Get performance insights for account, campaign, adset, or ad."""
    _, account_id = get_config()
    target = object_id or account_id

    default_fields = "campaign_name,impressions,clicks,spend,cpc,cpm,ctr,reach,frequency,actions,cost_per_action_type"
    params = {
        "date_preset": date_preset,
        "level": level,
        "fields": fields or default_fields,
        "limit": str(limit),
    }
    if breakdowns:
        params["breakdowns"] = breakdowns
    return api_call(f"{target}/insights", params=params)


# --- Audiences ---


def audiences_list(limit: int = 25) -> dict:
    """List custom audiences."""
    _, account_id = get_config()
    params = {
        "fields": "id,name,description,subtype,approximate_count,data_source,delivery_status",
        "limit": str(limit),
    }
    return api_call(f"{account_id}/customaudiences", params=params)


def audience_create(
    name: str,
    subtype: str = "CUSTOM",
    description: Optional[str] = None,
    customer_file_source: str = "USER_PROVIDED_ONLY",
) -> dict:
    """Create a custom audience."""
    _, account_id = get_config()
    params = {
        "name": name,
        "subtype": subtype.upper(),
        "customer_file_source": customer_file_source,
    }
    if description:
        params["description"] = description
    return api_call(f"{account_id}/customaudiences", params=params, method="POST")


# --- Ad Creatives ---


def creatives_list(limit: int = 25) -> dict:
    """List ad creatives."""
    _, account_id = get_config()
    params = {
        "fields": "id,name,title,body,image_url,thumbnail_url,object_story_spec,status",
        "limit": str(limit),
    }
    return api_call(f"{account_id}/adcreatives", params=params)


# --- Account Info ---


def account_info() -> dict:
    """Get ad account info and spending limits."""
    _, account_id = get_config()
    params = {
        "fields": "id,name,account_status,currency,timezone_name,amount_spent,balance,spend_cap,business_name,owner",
    }
    return api_call(account_id, params=params)


# --- CLI ---


def main():
    parser = argparse.ArgumentParser(description="Meta Ads (Marketing API) handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Account
    subparsers.add_parser("account", help="Account info and spending limits")

    # Campaigns
    camp_list = subparsers.add_parser("campaigns", help="List campaigns")
    camp_list.add_argument("--status", help="Filter by status (ACTIVE, PAUSED, ARCHIVED)")
    camp_list.add_argument("--limit", type=int, default=25)

    camp_create = subparsers.add_parser("campaign-create", help="Create campaign (PAUSED)")
    camp_create.add_argument("name", help="Campaign name")
    camp_create.add_argument("objective", help="Objective: OUTCOME_AWARENESS, OUTCOME_TRAFFIC, OUTCOME_ENGAGEMENT, OUTCOME_LEADS, OUTCOME_APP_PROMOTION, OUTCOME_SALES")
    camp_create.add_argument("--status", default="PAUSED")
    camp_create.add_argument("--daily-budget", type=int, help="Daily budget in cents")
    camp_create.add_argument("--lifetime-budget", type=int, help="Lifetime budget in cents")

    camp_update = subparsers.add_parser("campaign-update", help="Update campaign")
    camp_update.add_argument("id", help="Campaign ID")
    camp_update.add_argument("--name")
    camp_update.add_argument("--status")
    camp_update.add_argument("--daily-budget", type=int)

    camp_del = subparsers.add_parser("campaign-delete", help="Delete campaign")
    camp_del.add_argument("id", help="Campaign ID")

    # Ad Sets
    adset_list = subparsers.add_parser("adsets", help="List ad sets")
    adset_list.add_argument("--campaign-id", help="Filter by campaign")
    adset_list.add_argument("--status")
    adset_list.add_argument("--limit", type=int, default=25)

    adset_cr = subparsers.add_parser("adset-create", help="Create ad set (PAUSED)")
    adset_cr.add_argument("campaign_id", help="Parent campaign ID")
    adset_cr.add_argument("name", help="Ad set name")
    adset_cr.add_argument("daily_budget", type=int, help="Daily budget in cents")
    adset_cr.add_argument("optimization_goal", help="LINK_CLICKS, IMPRESSIONS, REACH, etc.")
    adset_cr.add_argument("--billing-event", default="IMPRESSIONS")
    adset_cr.add_argument("--targeting", help="JSON targeting spec")
    adset_cr.add_argument("--status", default="PAUSED")
    adset_cr.add_argument("--start-time", help="ISO 8601 start time")
    adset_cr.add_argument("--end-time", help="ISO 8601 end time")

    # Ads
    ads = subparsers.add_parser("ads", help="List ads")
    ads.add_argument("--adset-id", help="Filter by ad set")
    ads.add_argument("--status")
    ads.add_argument("--limit", type=int, default=25)

    # Insights
    ins = subparsers.add_parser("insights", help="Performance insights")
    ins.add_argument("--id", help="Campaign/AdSet/Ad ID (default: account level)")
    ins.add_argument("--date-preset", default="last_7d", help="last_7d, last_30d, today, yesterday, this_month, last_month")
    ins.add_argument("--level", default="campaign", help="campaign, adset, ad, account")
    ins.add_argument("--fields", help="Comma-separated fields")
    ins.add_argument("--breakdowns", help="age, gender, country, placement, etc.")
    ins.add_argument("--limit", type=int, default=50)

    # Audiences
    aud_list = subparsers.add_parser("audiences", help="List custom audiences")
    aud_list.add_argument("--limit", type=int, default=25)

    aud_create = subparsers.add_parser("audience-create", help="Create custom audience")
    aud_create.add_argument("name", help="Audience name")
    aud_create.add_argument("--subtype", default="CUSTOM")
    aud_create.add_argument("--description")

    # Creatives
    cre_list = subparsers.add_parser("creatives", help="List ad creatives")
    cre_list.add_argument("--limit", type=int, default=25)

    args = parser.parse_args()

    try:
        if args.command == "account":
            result = account_info()
        elif args.command == "campaigns":
            result = campaigns_list(args.status, args.limit)
        elif args.command == "campaign-create":
            result = campaign_create(args.name, args.objective, args.status, args.daily_budget, args.lifetime_budget)
        elif args.command == "campaign-update":
            updates = {}
            if args.name:
                updates["name"] = args.name
            if args.status:
                updates["status"] = args.status.upper()
            if args.daily_budget:
                updates["daily_budget"] = args.daily_budget
            result = campaign_update(args.id, **updates)
        elif args.command == "campaign-delete":
            result = campaign_delete(args.id)
        elif args.command == "adsets":
            result = adsets_list(args.campaign_id, args.status, args.limit)
        elif args.command == "adset-create":
            result = adset_create(
                args.campaign_id, args.name, args.daily_budget,
                args.optimization_goal, args.billing_event,
                args.targeting, args.status, args.start_time, args.end_time,
            )
        elif args.command == "ads":
            result = ads_list(args.adset_id, args.status, args.limit)
        elif args.command == "insights":
            result = insights(args.id, args.date_preset, args.level, args.fields, args.breakdowns, args.limit)
        elif args.command == "audiences":
            result = audiences_list(args.limit)
        elif args.command == "audience-create":
            result = audience_create(args.name, args.subtype, args.description)
        elif args.command == "creatives":
            result = creatives_list(args.limit)
        else:
            result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
