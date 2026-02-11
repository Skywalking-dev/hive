---
description: Query Gate.io prices, balances, or manage orders
argument-hint: price BTC_USDT | balance | klines BTC_USDT 4h | trades BTC_USDT
---

Access Gate.io spot markets using the gate skill.

> [!IMPORTANT]
> Follow the rules in the [gate] skill.

# Usage

## Market data (public)
- `price <pair>` - current price
- `prices --filter BTC` - all prices filtered
- `ticker <pair>` - 24h stats
- `klines <pair> <interval>` - candlestick data
- `orderbook <pair>` - order book depth

## Account (private)
- `balance` - spot balances
- `orders` - open spot orders
- `trades <pair>` - recent trades

## Trading (requires explicit user confirmation)
- `spot-order <pair> <side> <type> <amount> [--price]`
- `cancel <pair> <order_id>`

# Prerequisites
- `GATE_API_KEY` in `.env`
- `GATE_SECRET_KEY` in `.env`
