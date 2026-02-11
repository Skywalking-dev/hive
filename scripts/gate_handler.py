#!/usr/bin/env python3
"""
Gate.io API v4 handler for Hive.
Spot: prices, balances, orders, trades, klines.
"""

import os
import sys
import json
import time
import hmac
import hashlib
import argparse
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode


# --- Config ---

BASE_URL = "https://api.gateio.ws/api/v4"


def get_config() -> tuple[str, str]:
    api_key = os.environ.get("GATE_API_KEY")
    secret = os.environ.get("GATE_SECRET_KEY")

    if not api_key:
        raise ValueError("GATE_API_KEY not set in environment")
    if not secret:
        raise ValueError("GATE_SECRET_KEY not set in environment")

    return api_key, secret


def gen_sign(method: str, path: str, query_string: str = "", body: str = "") -> dict:
    """Generate Gate.io v4 authentication headers."""
    api_key, secret = get_config()
    t = str(time.time())
    hashed_body = hashlib.sha512(body.encode()).hexdigest()
    sign_string = f"{method}\n{path}\n{query_string}\n{hashed_body}\n{t}"
    signature = hmac.new(secret.encode(), sign_string.encode(), hashlib.sha512).hexdigest()
    return {
        "KEY": api_key,
        "SIGN": signature,
        "Timestamp": t,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# --- Core API ---

def public_call(path: str, params: Optional[dict] = None) -> dict:
    """Unauthenticated GET request."""
    url = f"{BASE_URL}{path}"
    if params:
        url += f"?{urlencode(params)}"

    req = Request(url, method="GET")
    req.add_header("Accept", "application/json")
    try:
        with urlopen(req, timeout=15) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err = json.loads(body)
            msg = f"HTTP {e.code}: {err.get('message', body)}"
        except Exception:
            msg = f"HTTP {e.code}: {body}"
        return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}


def signed_call(path: str, method: str = "GET", query: Optional[dict] = None, body: Optional[dict] = None) -> dict:
    """Authenticated request with HMAC-SHA512 signature."""
    query_string = urlencode(query) if query else ""
    body_string = json.dumps(body) if body else ""

    headers = gen_sign(method, f"/api/v4{path}", query_string, body_string)

    url = f"{BASE_URL}{path}"
    if query_string:
        url += f"?{query_string}"

    data = body_string.encode("utf-8") if body_string else None

    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err = json.loads(err_body)
            msg = f"HTTP {e.code}: [{err.get('label', '')}] {err.get('message', err_body)}"
        except Exception:
            msg = f"HTTP {e.code}: {err_body}"
        return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Public endpoints ---

def get_price(pair: str) -> dict:
    """Current price for a pair."""
    result = public_call("/spot/tickers", {"currency_pair": pair.upper()})
    if not result["success"]:
        return result
    tickers = result["data"]
    if tickers:
        t = tickers[0]
        return {"success": True, "data": {"currency_pair": t["currency_pair"], "last": t["last"]}}
    return {"success": False, "error": f"Pair {pair} not found"}


def get_prices(filter_str: Optional[str] = None) -> dict:
    """All prices, optionally filtered by substring."""
    result = public_call("/spot/tickers")
    if not result["success"]:
        return result

    prices = result["data"]
    if filter_str:
        f = filter_str.upper()
        prices = [p for p in prices if f in p["currency_pair"]]

    prices.sort(key=lambda p: p["currency_pair"])
    simplified = [{"currency_pair": p["currency_pair"], "last": p["last"]} for p in prices]
    return {"success": True, "data": {"count": len(simplified), "prices": simplified}}


def get_ticker(pair: str) -> dict:
    """24h ticker stats."""
    result = public_call("/spot/tickers", {"currency_pair": pair.upper()})
    if not result["success"]:
        return result
    tickers = result["data"]
    if tickers:
        return {"success": True, "data": tickers[0]}
    return {"success": False, "error": f"Pair {pair} not found"}


def get_klines(pair: str, interval: str, limit: int = 100) -> dict:
    """Candlestick data."""
    result = public_call("/spot/candlesticks", {
        "currency_pair": pair.upper(),
        "interval": interval,
        "limit": limit,
    })
    if not result["success"]:
        return result

    candles = [
        {
            "time": c[0],
            "volume": c[1],
            "close": c[2],
            "high": c[3],
            "low": c[4],
            "open": c[5],
            "quote_volume": c[6] if len(c) > 6 else None,
        }
        for c in result["data"]
    ]
    return {"success": True, "data": {"currency_pair": pair.upper(), "interval": interval, "candles": candles}}


def get_orderbook(pair: str, limit: int = 10) -> dict:
    """Order book depth."""
    return public_call("/spot/order_book", {"currency_pair": pair.upper(), "limit": limit})


# --- Private endpoints ---

def get_balance() -> dict:
    """Spot account balances (non-zero only)."""
    result = signed_call("/spot/accounts")
    if not result["success"]:
        return result

    balances = [
        {"currency": b["currency"], "available": b["available"], "locked": b["locked"]}
        for b in result["data"]
        if float(b["available"]) > 0 or float(b["locked"]) > 0
    ]
    return {"success": True, "data": {"balances": balances}}


def get_open_orders(pair: Optional[str] = None) -> dict:
    """Open spot orders."""
    query = {"status": "open"}
    if pair:
        query["currency_pair"] = pair.upper()
    else:
        query["currency_pair"] = ""
    return signed_call("/spot/orders", query=query)


def get_my_trades(pair: str) -> dict:
    """Recent trades for a pair."""
    return signed_call("/spot/my_trades", query={"currency_pair": pair.upper()})


def place_order(pair: str, side: str, order_type: str, amount: str, price: Optional[str] = None) -> dict:
    """Place a spot order."""
    body = {
        "currency_pair": pair.upper(),
        "side": side.lower(),
        "type": order_type.lower(),
        "amount": amount,
    }
    if order_type.lower() == "limit":
        if not price:
            return {"success": False, "error": "LIMIT orders require --price"}
        body["price"] = price
    elif order_type.lower() == "market":
        body["time_in_force"] = "ioc"

    return signed_call("/spot/orders", method="POST", body=body)


def cancel_order(pair: str, order_id: str) -> dict:
    """Cancel a spot order."""
    return signed_call(f"/spot/orders/{order_id}", method="DELETE", query={"currency_pair": pair.upper()})


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Gate.io API v4 handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Price
    price_p = subparsers.add_parser("price", help="Get current price")
    price_p.add_argument("pair", help="Trading pair (e.g. BTC_USDT)")

    # Prices
    prices_p = subparsers.add_parser("prices", help="List all prices")
    prices_p.add_argument("--filter", help="Filter by substring (e.g. BTC)")

    # Ticker
    ticker_p = subparsers.add_parser("ticker", help="24h ticker stats")
    ticker_p.add_argument("pair", help="Trading pair")

    # Klines
    klines_p = subparsers.add_parser("klines", help="Candlestick data")
    klines_p.add_argument("pair", help="Trading pair")
    klines_p.add_argument("interval", help="Interval (10s,1m,5m,15m,30m,1h,4h,8h,1d,7d,30d)")
    klines_p.add_argument("--limit", type=int, default=100, help="Number of candles")

    # Orderbook
    book_p = subparsers.add_parser("orderbook", help="Order book depth")
    book_p.add_argument("pair", help="Trading pair")
    book_p.add_argument("--limit", type=int, default=10, help="Depth levels")

    # Balance
    subparsers.add_parser("balance", help="Spot balances")

    # Open orders
    orders_p = subparsers.add_parser("orders", help="Open spot orders")
    orders_p.add_argument("--pair", help="Filter by pair")

    # My trades
    trades_p = subparsers.add_parser("trades", help="Recent trades")
    trades_p.add_argument("pair", help="Trading pair")

    # Place order
    spot_order_p = subparsers.add_parser("spot-order", help="Place spot order")
    spot_order_p.add_argument("pair", help="Trading pair")
    spot_order_p.add_argument("side", choices=["buy", "sell"], help="Order side")
    spot_order_p.add_argument("type", choices=["market", "limit"], help="Order type")
    spot_order_p.add_argument("amount", help="Order amount")
    spot_order_p.add_argument("--price", help="Limit price")

    # Cancel order
    cancel_p = subparsers.add_parser("cancel", help="Cancel spot order")
    cancel_p.add_argument("pair", help="Trading pair")
    cancel_p.add_argument("order_id", help="Order ID")

    args = parser.parse_args()

    try:
        match args.command:
            # Public
            case "price":
                result = get_price(args.pair)
            case "prices":
                result = get_prices(args.filter)
            case "ticker":
                result = get_ticker(args.pair)
            case "klines":
                result = get_klines(args.pair, args.interval, args.limit)
            case "orderbook":
                result = get_orderbook(args.pair, args.limit)
            # Private
            case "balance":
                result = get_balance()
            case "orders":
                result = get_open_orders(args.pair)
            case "trades":
                result = get_my_trades(args.pair)
            case "spot-order":
                result = place_order(args.pair, args.side, args.type, args.amount, args.price)
            case "cancel":
                result = cancel_order(args.pair, args.order_id)
            case _:
                result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
