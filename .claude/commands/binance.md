---
description: Query Binance prices, balances, positions, or manage orders
argument-hint: price BTCUSDT | balance | positions | futures-balance | klines BTCUSDT 4h
---

Access Binance spot and futures markets using the binance skill.

> [!IMPORTANT]
> Follow the rules in the [binance] skill.

# Usage

## Market data (public)
- `price <symbol>` - current price
- `prices --filter BTC` - all prices filtered
- `ticker <symbol>` - 24h stats
- `klines <symbol> <interval>` - candlestick data
- `orderbook <symbol>` - order book depth

## Account (private)
- `balance` - spot balances
- `futures-balance` - futures balances
- `positions` - open futures positions
- `orders` - open spot orders
- `futures-orders` - open futures orders

## Trading (requires explicit user confirmation)
- `spot-order <symbol> <side> <type> <qty> [--price]`
- `futures-order <symbol> <side> <type> <qty> [--price]`
- `cancel <symbol> <order_id>`
- `futures-cancel <symbol> <order_id>`

# Prerequisites
- `BINANCE_API_KEY` in `.env`
- `BINANCE_SECRET_KEY` in `.env`
- `BINANCE_TESTNET=true` in `.env` (optional)
