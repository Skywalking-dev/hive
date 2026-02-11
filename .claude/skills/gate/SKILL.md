---
name: gate
description: Query Gate.io spot markets, check balances, manage orders and trades. Use when user needs Gate.io crypto prices, portfolio status, or trade execution.
allowed-tools: Bash, Read
---

# Gate.io API v4

Spot access via Python script. Prices, balances, orders, trades.

## Prerequisites
- `GATE_API_KEY` in `.env`
- `GATE_SECRET_KEY` in `.env`

## Quick Commands

```bash
# Prices
python scripts/gate_handler.py price BTC_USDT
python scripts/gate_handler.py prices --filter BTC
python scripts/gate_handler.py ticker ETH_USDT

# Market data
python scripts/gate_handler.py klines BTC_USDT 4h --limit 50
python scripts/gate_handler.py orderbook BTC_USDT --limit 20

# Balances
python scripts/gate_handler.py balance

# Orders & trades
python scripts/gate_handler.py orders --pair BTC_USDT
python scripts/gate_handler.py trades BTC_USDT
```

## Trading (use with caution)

```bash
# Spot
python scripts/gate_handler.py spot-order BTC_USDT buy market 0.001
python scripts/gate_handler.py spot-order BTC_USDT buy limit 0.001 --price 50000
python scripts/gate_handler.py cancel BTC_USDT 12345678
```

## Safety Rules

- **ALWAYS confirm with user before placing or canceling orders**
- Read-only commands (price, balance, orders, trades) are safe to run freely
- For order placement: state pair, side, type, amount, price clearly and wait for explicit approval

## Pair Format
- Underscore separated, uppercase: `BTC_USDT`, `ETH_USDT`, `SOL_USDT`
- Format: `BASE_QUOTE` (e.g. `DOGE_USDT`, `BTC_ETH`)

## Kline Intervals
`10s` `1m` `5m` `15m` `30m` `1h` `4h` `8h` `1d` `7d` `30d`

## Common Errors

| Label | Cause | Fix |
|-------|-------|-----|
| INVALID_CURRENCY_PAIR | Bad pair name | Check pair format (BTC_USDT) |
| BALANCE_NOT_ENOUGH | Insufficient balance | Check balance first |
| INVALID_PARAM_VALUE | Bad parameter | Check amount/price format |
| INVALID_KEY | Invalid API key | Check env vars |
| INVALID_SIGNATURE | Bad signature | Check secret key |

## Output Format

```json
{
  "success": true,
  "data": { ... }
}
```

All commands return JSON with `success` boolean. Non-zero balances only.
