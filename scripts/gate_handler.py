#!/usr/bin/env python3
"""
Gate.io API v4 handler for Hive.
Spot + Futures (USDT perps) + Earn (UniLoan, Dual Investment).
"""

import os
import sys
import json
import time
import hmac
import hashlib
import argparse
from pathlib import Path
from typing import Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# --- Config ---

BASE_URL = "https://api.gateio.ws/api/v4"
SETTLE = "usdt"


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


def signed_call(
    path: str,
    method: str = "GET",
    query: Optional[dict] = None,
    body: Optional[dict] = None,
) -> dict:
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
            resp_body = resp.read().decode("utf-8")
            if not resp_body:
                return {"success": True, "data": None}
            return {"success": True, "data": json.loads(resp_body)}
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


# ============================================================
# SPOT - Public endpoints
# ============================================================

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


# ============================================================
# SPOT - Private endpoints
# ============================================================

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


# ============================================================
# FUTURES - Public endpoints (USDT-settled perps)
# ============================================================

def get_futures_price(contract: str) -> dict:
    """Current futures price."""
    result = public_call(f"/futures/{SETTLE}/tickers", {"contract": contract.upper()})
    if not result["success"]:
        return result
    tickers = result["data"]
    if tickers:
        t = tickers[0]
        return {"success": True, "data": {
            "contract": t["contract"],
            "last": t["last"],
            "mark_price": t.get("mark_price"),
            "index_price": t.get("index_price"),
            "funding_rate": t.get("funding_rate"),
        }}
    return {"success": False, "error": f"Contract {contract} not found"}


def get_futures_ticker(contract: str) -> dict:
    """24h futures ticker stats."""
    result = public_call(f"/futures/{SETTLE}/tickers", {"contract": contract.upper()})
    if not result["success"]:
        return result
    tickers = result["data"]
    if tickers:
        return {"success": True, "data": tickers[0]}
    return {"success": False, "error": f"Contract {contract} not found"}


def get_futures_klines(contract: str, interval: str, limit: int = 100) -> dict:
    """Futures candlestick data."""
    result = public_call(f"/futures/{SETTLE}/candlesticks", {
        "contract": contract.upper(),
        "interval": interval,
        "limit": limit,
    })
    if not result["success"]:
        return result

    candles = [
        {
            "time": c.get("t"),
            "open": c.get("o"),
            "high": c.get("h"),
            "low": c.get("l"),
            "close": c.get("c"),
            "volume": c.get("v"),
            "notional": c.get("sum"),
        }
        for c in result["data"]
    ]
    return {"success": True, "data": {"contract": contract.upper(), "interval": interval, "candles": candles}}


def get_futures_orderbook(contract: str, limit: int = 10) -> dict:
    """Futures order book depth."""
    return public_call(f"/futures/{SETTLE}/order_book", {"contract": contract.upper(), "limit": limit})


def get_funding_rate(contract: str, limit: int = 10) -> dict:
    """Historical funding rates."""
    return public_call(f"/futures/{SETTLE}/funding_rate", {"contract": contract.upper(), "limit": limit})


# ============================================================
# FUTURES - Private endpoints
# ============================================================

def get_futures_balance() -> dict:
    """Futures account balance."""
    return signed_call(f"/futures/{SETTLE}/accounts")


def get_positions() -> dict:
    """Open futures positions (non-zero only)."""
    result = signed_call(f"/futures/{SETTLE}/positions")
    if not result["success"]:
        return result

    positions = [
        {
            "contract": p["contract"],
            "size": p["size"],
            "leverage": p["leverage"],
            "entry_price": p["entry_price"],
            "mark_price": p["mark_price"],
            "liq_price": p["liq_price"],
            "unrealised_pnl": p["unrealised_pnl"],
            "margin": p["margin"],
            "mode": p.get("mode", "single"),
        }
        for p in result["data"]
        if p["size"] != 0
    ]
    return {"success": True, "data": {"count": len(positions), "positions": positions}}


def get_futures_orders(contract: Optional[str] = None) -> dict:
    """Open futures orders."""
    query = {"status": "open"}
    if contract:
        query["contract"] = contract.upper()
    return signed_call(f"/futures/{SETTLE}/orders", query=query)


def get_futures_trades(contract: str) -> dict:
    """My futures trades."""
    return signed_call(f"/futures/{SETTLE}/my_trades", query={"contract": contract.upper()})


def place_futures_order(
    contract: str, size: int, price: str = "0", tif: str = "gtc",
    reduce_only: bool = False,
) -> dict:
    """Place a futures order. size>0=long, size<0=short. price=0 for market."""
    body = {
        "contract": contract.upper(),
        "size": size,
        "price": price,
        "tif": tif,
    }
    if reduce_only:
        body["reduce_only"] = True
    if price == "0":
        body["tif"] = "ioc"
    return signed_call(f"/futures/{SETTLE}/orders", method="POST", body=body)


def cancel_futures_order(order_id: str) -> dict:
    """Cancel a futures order."""
    return signed_call(f"/futures/{SETTLE}/orders/{order_id}", method="DELETE")


def set_leverage(contract: str, leverage: int) -> dict:
    """Set leverage. 0=cross, >0=isolated with that multiplier."""
    return signed_call(
        f"/futures/{SETTLE}/positions/{contract.upper()}/leverage",
        method="POST",
        query={"leverage": str(leverage)},
    )


# ============================================================
# EARN - UniLoan (Simple Earn / Flexible Lending)
# ============================================================

def get_earn_products(currency: Optional[str] = None) -> dict:
    """List available earn currencies/products."""
    if currency:
        return public_call(f"/earn/uni/currencies/{currency.upper()}")
    return public_call("/earn/uni/currencies")


def get_earn_positions(currency: Optional[str] = None) -> dict:
    """Current earn lending positions."""
    query = {}
    if currency:
        query["currency"] = currency.upper()
    return signed_call("/earn/uni/lends", query=query if query else None)


def earn_lend(currency: str, amount: str, min_rate: Optional[str] = None) -> dict:
    """Lend to earn (subscribe)."""
    body = {"currency": currency.upper(), "amount": amount, "type": "lend"}
    if min_rate:
        body["min_rate"] = min_rate
    return signed_call("/earn/uni/lends", method="POST", body=body)


def earn_redeem(currency: str, amount: str) -> dict:
    """Redeem from earn."""
    body = {"currency": currency.upper(), "amount": amount, "type": "redeem"}
    return signed_call("/earn/uni/lends", method="POST", body=body)


def get_earn_interest(currency: Optional[str] = None) -> dict:
    """Earn interest records."""
    query = {}
    if currency:
        query["currency"] = currency.upper()
    return signed_call("/earn/uni/interest_records", query=query if query else None)


def get_earn_lend_records(currency: Optional[str] = None) -> dict:
    """Earn lend/redeem transaction history."""
    query = {}
    if currency:
        query["currency"] = currency.upper()
    return signed_call("/earn/uni/lend_records", query=query if query else None)


# ============================================================
# EARN - Dual Investment
# ============================================================

def get_dual_products() -> dict:
    """List available dual investment plans."""
    return signed_call("/earn/dual/investment_plan")


def place_dual_order(plan_id: str, amount: str) -> dict:
    """Subscribe to a dual investment plan."""
    body = {"plan_id": plan_id, "amount": amount}
    return signed_call("/earn/dual/orders", method="POST", body=body)


def get_dual_orders() -> dict:
    """List dual investment orders (active + history)."""
    return signed_call("/earn/dual/orders")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Gate.io API v4 handler — Spot + Futures + Earn")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Spot public ---
    price_p = subparsers.add_parser("price", help="Spot price")
    price_p.add_argument("pair", help="Trading pair (e.g. BTC_USDT)")

    prices_p = subparsers.add_parser("prices", help="List all spot prices")
    prices_p.add_argument("--filter", help="Filter by substring")

    ticker_p = subparsers.add_parser("ticker", help="24h spot ticker")
    ticker_p.add_argument("pair", help="Trading pair")

    klines_p = subparsers.add_parser("klines", help="Spot candlesticks")
    klines_p.add_argument("pair", help="Trading pair")
    klines_p.add_argument("interval", help="10s,1m,5m,15m,30m,1h,4h,8h,1d,7d,30d")
    klines_p.add_argument("--limit", type=int, default=100)

    book_p = subparsers.add_parser("orderbook", help="Spot order book")
    book_p.add_argument("pair", help="Trading pair")
    book_p.add_argument("--limit", type=int, default=10)

    # --- Spot private ---
    subparsers.add_parser("balance", help="Spot balances")

    orders_p = subparsers.add_parser("orders", help="Open spot orders")
    orders_p.add_argument("--pair", help="Filter by pair")

    trades_p = subparsers.add_parser("trades", help="Recent spot trades")
    trades_p.add_argument("pair", help="Trading pair")

    spot_order_p = subparsers.add_parser("spot-order", help="Place spot order")
    spot_order_p.add_argument("pair", help="Trading pair")
    spot_order_p.add_argument("side", choices=["buy", "sell"])
    spot_order_p.add_argument("type", choices=["market", "limit"])
    spot_order_p.add_argument("amount", help="Order amount")
    spot_order_p.add_argument("--price", help="Limit price")

    cancel_p = subparsers.add_parser("cancel", help="Cancel spot order")
    cancel_p.add_argument("pair", help="Trading pair")
    cancel_p.add_argument("order_id", help="Order ID")

    # --- Futures public ---
    fp_p = subparsers.add_parser("futures-price", help="Futures price")
    fp_p.add_argument("contract", help="Contract (e.g. BTC_USDT)")

    ft_p = subparsers.add_parser("futures-ticker", help="24h futures ticker")
    ft_p.add_argument("contract", help="Contract")

    fk_p = subparsers.add_parser("futures-klines", help="Futures candlesticks")
    fk_p.add_argument("contract", help="Contract")
    fk_p.add_argument("interval", help="10s,1m,5m,15m,30m,1h,4h,8h,1d,7d")
    fk_p.add_argument("--limit", type=int, default=100)

    fob_p = subparsers.add_parser("futures-orderbook", help="Futures order book")
    fob_p.add_argument("contract", help="Contract")
    fob_p.add_argument("--limit", type=int, default=10)

    fr_p = subparsers.add_parser("funding-rate", help="Funding rate history")
    fr_p.add_argument("contract", help="Contract")
    fr_p.add_argument("--limit", type=int, default=10)

    # --- Futures private ---
    subparsers.add_parser("futures-balance", help="Futures account balance")
    subparsers.add_parser("positions", help="Open futures positions")

    fo_p = subparsers.add_parser("futures-orders", help="Open futures orders")
    fo_p.add_argument("--contract", help="Filter by contract")

    ftr_p = subparsers.add_parser("futures-trades", help="My futures trades")
    ftr_p.add_argument("contract", help="Contract")

    forder_p = subparsers.add_parser("futures-order", help="Place futures order")
    forder_p.add_argument("contract", help="Contract")
    forder_p.add_argument("size", type=int, help="Contracts: >0 long, <0 short")
    forder_p.add_argument("--price", default="0", help="Price (0=market)")
    forder_p.add_argument("--tif", default="gtc", choices=["gtc", "ioc", "poc"])
    forder_p.add_argument("--reduce-only", action="store_true")

    fcancel_p = subparsers.add_parser("futures-cancel", help="Cancel futures order")
    fcancel_p.add_argument("order_id", help="Order ID")

    lev_p = subparsers.add_parser("set-leverage", help="Set futures leverage")
    lev_p.add_argument("contract", help="Contract")
    lev_p.add_argument("leverage", type=int, help="0=cross, >0=isolated")

    # --- Earn: UniLoan ---
    ep_p = subparsers.add_parser("earn-products", help="Earn available currencies")
    ep_p.add_argument("--currency", help="Filter by currency")

    epos_p = subparsers.add_parser("earn-positions", help="Current earn positions")
    epos_p.add_argument("--currency", help="Filter by currency")

    elend_p = subparsers.add_parser("earn-lend", help="Lend to earn")
    elend_p.add_argument("currency", help="Currency (e.g. USDT)")
    elend_p.add_argument("amount", help="Amount to lend")
    elend_p.add_argument("--min-rate", help="Min hourly rate")

    eredeem_p = subparsers.add_parser("earn-redeem", help="Redeem from earn")
    eredeem_p.add_argument("currency", help="Currency")
    eredeem_p.add_argument("amount", help="Amount to redeem")

    ei_p = subparsers.add_parser("earn-interest", help="Earn interest records")
    ei_p.add_argument("--currency", help="Filter by currency")

    ehr_p = subparsers.add_parser("earn-history", help="Earn lend/redeem history")
    ehr_p.add_argument("--currency", help="Filter by currency")

    # --- Earn: Dual Investment ---
    subparsers.add_parser("dual-products", help="Dual investment plans")

    do_p = subparsers.add_parser("dual-order", help="Subscribe to dual plan")
    do_p.add_argument("plan_id", help="Plan ID")
    do_p.add_argument("amount", help="Amount")

    subparsers.add_parser("dual-orders", help="Dual investment orders")

    args = parser.parse_args()

    try:
        match args.command:
            # Spot public
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
            # Spot private
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
            # Futures public
            case "futures-price":
                result = get_futures_price(args.contract)
            case "futures-ticker":
                result = get_futures_ticker(args.contract)
            case "futures-klines":
                result = get_futures_klines(args.contract, args.interval, args.limit)
            case "futures-orderbook":
                result = get_futures_orderbook(args.contract, args.limit)
            case "funding-rate":
                result = get_funding_rate(args.contract, args.limit)
            # Futures private
            case "futures-balance":
                result = get_futures_balance()
            case "positions":
                result = get_positions()
            case "futures-orders":
                result = get_futures_orders(args.contract)
            case "futures-trades":
                result = get_futures_trades(args.contract)
            case "futures-order":
                result = place_futures_order(
                    args.contract, args.size, args.price, args.tif, args.reduce_only,
                )
            case "futures-cancel":
                result = cancel_futures_order(args.order_id)
            case "set-leverage":
                result = set_leverage(args.contract, args.leverage)
            # Earn: UniLoan
            case "earn-products":
                result = get_earn_products(args.currency)
            case "earn-positions":
                result = get_earn_positions(args.currency)
            case "earn-lend":
                result = earn_lend(args.currency, args.amount, args.min_rate)
            case "earn-redeem":
                result = earn_redeem(args.currency, args.amount)
            case "earn-interest":
                result = get_earn_interest(args.currency)
            case "earn-history":
                result = get_earn_lend_records(args.currency)
            # Earn: Dual Investment
            case "dual-products":
                result = get_dual_products()
            case "dual-order":
                result = place_dual_order(args.plan_id, args.amount)
            case "dual-orders":
                result = get_dual_orders()
            case _:
                result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
