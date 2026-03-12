#!/usr/bin/env python3
"""
Binance API handler for Hive.
Spot + Futures: prices, balances, positions, orders, klines.
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

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# --- Config ---

SPOT_BASE = "https://api.binance.com"
FUTURES_BASE = "https://fapi.binance.com"
SPOT_TESTNET = "https://testnet.binance.vision"
FUTURES_TESTNET = "https://testnet.binancefuture.com"


def get_config() -> tuple[str, str, bool]:
    api_key = os.environ.get("BINANCE_API_KEY")
    secret = os.environ.get("BINANCE_SECRET_KEY")
    testnet = os.environ.get("BINANCE_TESTNET", "").lower() in ("1", "true", "yes")

    if not api_key:
        raise ValueError("BINANCE_API_KEY not set in environment")
    if not secret:
        raise ValueError("BINANCE_SECRET_KEY not set in environment")

    return api_key, secret, testnet


def get_base_url(futures: bool = False) -> str:
    _, _, testnet = get_config()
    if futures:
        return FUTURES_TESTNET if testnet else FUTURES_BASE
    return SPOT_TESTNET if testnet else SPOT_BASE


def sign(params: dict, secret: str) -> str:
    query = urlencode(params)
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()


# --- Core API ---

def public_call(endpoint: str, params: Optional[dict] = None, futures: bool = False) -> dict:
    """Unauthenticated GET request."""
    base = get_base_url(futures)
    url = f"{base}{endpoint}"
    if params:
        url += f"?{urlencode(params)}"

    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=15) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            err = json.loads(body)
            msg = f"HTTP {e.code}: {err.get('msg', body)}"
        except Exception:
            msg = f"HTTP {e.code}: {body}"
        return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}


def signed_call(
    endpoint: str,
    params: Optional[dict] = None,
    method: str = "GET",
    futures: bool = False,
) -> dict:
    """Authenticated request with HMAC signature."""
    api_key, secret, _ = get_config()
    base = get_base_url(futures)

    params = params or {}
    params["timestamp"] = int(time.time() * 1000)
    params["recvWindow"] = 5000
    params["signature"] = sign(params, secret)

    url = f"{base}{endpoint}"
    headers = {"X-MBX-APIKEY": api_key}

    if method == "GET":
        url += f"?{urlencode(params)}"
        body = None
    else:
        body = urlencode(params).encode("utf-8")
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return {"success": True, "data": json.loads(resp.read().decode("utf-8"))}
    except HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            err = json.loads(err_body)
            msg = f"HTTP {e.code}: [{err.get('code')}] {err.get('msg', err_body)}"
        except Exception:
            msg = f"HTTP {e.code}: {err_body}"
        return {"success": False, "error": msg}
    except Exception as e:
        return {"success": False, "error": str(e)}


# --- Public endpoints ---

def get_price(symbol: str) -> dict:
    """Current price for a symbol."""
    return public_call("/api/v3/ticker/price", {"symbol": symbol.upper()})


def get_prices(filter_str: Optional[str] = None) -> dict:
    """All prices, optionally filtered by substring."""
    result = public_call("/api/v3/ticker/price")
    if not result["success"]:
        return result

    prices = result["data"]
    if filter_str:
        f = filter_str.upper()
        prices = [p for p in prices if f in p["symbol"]]

    # Sort by symbol
    prices.sort(key=lambda p: p["symbol"])
    return {"success": True, "data": {"count": len(prices), "prices": prices}}


def get_ticker(symbol: str) -> dict:
    """24h ticker stats."""
    return public_call("/api/v3/ticker/24hr", {"symbol": symbol.upper()})


def get_klines(symbol: str, interval: str, limit: int = 100) -> dict:
    """Candlestick data."""
    result = public_call("/api/v3/klines", {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit,
    })
    if not result["success"]:
        return result

    candles = [
        {
            "time": c[0],
            "open": c[1],
            "high": c[2],
            "low": c[3],
            "close": c[4],
            "volume": c[5],
            "close_time": c[6],
            "quote_volume": c[7],
            "trades": c[8],
        }
        for c in result["data"]
    ]
    return {"success": True, "data": {"symbol": symbol.upper(), "interval": interval, "candles": candles}}


def get_orderbook(symbol: str, limit: int = 10) -> dict:
    """Order book depth."""
    return public_call("/api/v3/depth", {"symbol": symbol.upper(), "limit": limit})


# --- Spot private endpoints ---

def get_balance() -> dict:
    """Spot account balances (non-zero only)."""
    result = signed_call("/api/v3/account")
    if not result["success"]:
        return result

    balances = [
        {"asset": b["asset"], "free": b["free"], "locked": b["locked"]}
        for b in result["data"].get("balances", [])
        if float(b["free"]) > 0 or float(b["locked"]) > 0
    ]
    return {"success": True, "data": {"balances": balances}}


def get_open_orders(symbol: Optional[str] = None) -> dict:
    """Open spot orders."""
    params = {}
    if symbol:
        params["symbol"] = symbol.upper()
    return signed_call("/api/v3/openOrders", params)


# --- Futures private endpoints ---

def get_futures_balance() -> dict:
    """Futures account balances (non-zero only)."""
    result = signed_call("/fapi/v3/balance", futures=True)
    if not result["success"]:
        return result

    balances = [
        {
            "asset": b["asset"],
            "balance": b["balance"],
            "available": b["availableBalance"],
            "unrealizedPnL": b.get("crossUnPnl", "0"),
        }
        for b in result["data"]
        if float(b["balance"]) != 0
    ]
    return {"success": True, "data": {"balances": balances}}


def get_positions() -> dict:
    """Open futures positions (non-zero only)."""
    result = signed_call("/fapi/v3/positionRisk", futures=True)
    if not result["success"]:
        return result

    positions = [
        {
            "symbol": p["symbol"],
            "side": "LONG" if float(p["positionAmt"]) > 0 else "SHORT",
            "size": p["positionAmt"],
            "entryPrice": p["entryPrice"],
            "markPrice": p["markPrice"],
            "unrealizedPnL": p["unRealizedProfit"],
            "leverage": p["leverage"],
            "marginType": p.get("marginType", ""),
            "liquidationPrice": p.get("liquidationPrice", "0"),
        }
        for p in result["data"]
        if float(p["positionAmt"]) != 0
    ]
    return {"success": True, "data": {"count": len(positions), "positions": positions}}


def get_futures_orders(symbol: Optional[str] = None) -> dict:
    """Open futures orders."""
    params = {}
    if symbol:
        params["symbol"] = symbol.upper()
    return signed_call("/fapi/v1/openOrders", params, futures=True)


# --- Order management ---

def place_spot_order(
    symbol: str, side: str, order_type: str, quantity: str, price: Optional[str] = None
) -> dict:
    """Place a spot order."""
    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type.upper(),
        "quantity": quantity,
    }
    if order_type.upper() == "LIMIT":
        if not price:
            return {"success": False, "error": "LIMIT orders require --price"}
        params["price"] = price
        params["timeInForce"] = "GTC"

    return signed_call("/api/v3/order", params, method="POST")


def place_futures_order(
    symbol: str, side: str, order_type: str, quantity: str, price: Optional[str] = None
) -> dict:
    """Place a futures order."""
    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type.upper(),
        "quantity": quantity,
    }
    if order_type.upper() == "LIMIT":
        if not price:
            return {"success": False, "error": "LIMIT orders require --price"}
        params["price"] = price
        params["timeInForce"] = "GTC"

    return signed_call("/fapi/v1/order", params, method="POST", futures=True)


def cancel_spot_order(symbol: str, order_id: str) -> dict:
    """Cancel a spot order."""
    return signed_call("/api/v3/order", {"symbol": symbol.upper(), "orderId": order_id}, method="DELETE")


def cancel_futures_order(symbol: str, order_id: str) -> dict:
    """Cancel a futures order."""
    return signed_call(
        "/fapi/v1/order",
        {"symbol": symbol.upper(), "orderId": order_id},
        method="DELETE",
        futures=True,
    )


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Binance API handler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Price
    price_p = subparsers.add_parser("price", help="Get current price")
    price_p.add_argument("symbol", help="Trading pair (e.g. BTCUSDT)")

    # Prices
    prices_p = subparsers.add_parser("prices", help="List all prices")
    prices_p.add_argument("--filter", help="Filter by substring (e.g. BTC)")

    # Ticker
    ticker_p = subparsers.add_parser("ticker", help="24h ticker stats")
    ticker_p.add_argument("symbol", help="Trading pair")

    # Klines
    klines_p = subparsers.add_parser("klines", help="Candlestick data")
    klines_p.add_argument("symbol", help="Trading pair")
    klines_p.add_argument("interval", help="Interval (1m,5m,15m,1h,4h,1d,1w)")
    klines_p.add_argument("--limit", type=int, default=100, help="Number of candles")

    # Orderbook
    book_p = subparsers.add_parser("orderbook", help="Order book depth")
    book_p.add_argument("symbol", help="Trading pair")
    book_p.add_argument("--limit", type=int, default=10, help="Depth levels")

    # Balance
    subparsers.add_parser("balance", help="Spot balances")

    # Futures balance
    subparsers.add_parser("futures-balance", help="Futures balances")

    # Positions
    subparsers.add_parser("positions", help="Open futures positions")

    # Open orders
    orders_p = subparsers.add_parser("orders", help="Open spot orders")
    orders_p.add_argument("--symbol", help="Filter by symbol")

    # Futures orders
    forders_p = subparsers.add_parser("futures-orders", help="Open futures orders")
    forders_p.add_argument("--symbol", help="Filter by symbol")

    # Place spot order
    spot_order_p = subparsers.add_parser("spot-order", help="Place spot order")
    spot_order_p.add_argument("symbol", help="Trading pair")
    spot_order_p.add_argument("side", choices=["buy", "sell"], help="Order side")
    spot_order_p.add_argument("type", choices=["market", "limit"], help="Order type")
    spot_order_p.add_argument("quantity", help="Order quantity")
    spot_order_p.add_argument("--price", help="Limit price")

    # Place futures order
    fut_order_p = subparsers.add_parser("futures-order", help="Place futures order")
    fut_order_p.add_argument("symbol", help="Trading pair")
    fut_order_p.add_argument("side", choices=["buy", "sell"], help="Order side")
    fut_order_p.add_argument("type", choices=["market", "limit"], help="Order type")
    fut_order_p.add_argument("quantity", help="Order quantity")
    fut_order_p.add_argument("--price", help="Limit price")

    # Cancel spot order
    cancel_p = subparsers.add_parser("cancel", help="Cancel spot order")
    cancel_p.add_argument("symbol", help="Trading pair")
    cancel_p.add_argument("order_id", help="Order ID")

    # Cancel futures order
    fcancel_p = subparsers.add_parser("futures-cancel", help="Cancel futures order")
    fcancel_p.add_argument("symbol", help="Trading pair")
    fcancel_p.add_argument("order_id", help="Order ID")

    args = parser.parse_args()

    try:
        match args.command:
            # Public
            case "price":
                result = get_price(args.symbol)
            case "prices":
                result = get_prices(args.filter)
            case "ticker":
                result = get_ticker(args.symbol)
            case "klines":
                result = get_klines(args.symbol, args.interval, args.limit)
            case "orderbook":
                result = get_orderbook(args.symbol, args.limit)
            # Spot private
            case "balance":
                result = get_balance()
            case "orders":
                result = get_open_orders(args.symbol)
            case "spot-order":
                result = place_spot_order(args.symbol, args.side, args.type, args.quantity, args.price)
            case "cancel":
                result = cancel_spot_order(args.symbol, args.order_id)
            # Futures private
            case "futures-balance":
                result = get_futures_balance()
            case "positions":
                result = get_positions()
            case "futures-orders":
                result = get_futures_orders(args.symbol)
            case "futures-order":
                result = place_futures_order(args.symbol, args.side, args.type, args.quantity, args.price)
            case "futures-cancel":
                result = cancel_futures_order(args.symbol, args.order_id)
            case _:
                result = {"success": False, "error": "Unknown command"}
    except ValueError as e:
        result = {"success": False, "error": str(e)}

    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
