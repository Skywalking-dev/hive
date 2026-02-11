---
name: binance
description: Query Binance spot and futures markets, check balances, manage positions and orders. Use when user needs crypto prices, portfolio status, or trade execution.
allowed-tools: Bash, Read
---

# Binance API

Spot + Futures access via Python script. Prices, balances, positions, orders.

## Prerequisites
- `BINANCE_API_KEY` in `.env`
- `BINANCE_SECRET_KEY` in `.env`
- `BINANCE_TESTNET=true` in `.env` (optional, for testnet)

## Quick Commands

```bash
# Prices
python scripts/binance_handler.py price BTCUSDT
python scripts/binance_handler.py prices --filter BTC
python scripts/binance_handler.py ticker ETHUSDT

# Market data
python scripts/binance_handler.py klines BTCUSDT 4h --limit 50
python scripts/binance_handler.py orderbook BTCUSDT --limit 20

# Balances
python scripts/binance_handler.py balance
python scripts/binance_handler.py futures-balance

# Positions & orders
python scripts/binance_handler.py positions
python scripts/binance_handler.py orders --symbol BTCUSDT
python scripts/binance_handler.py futures-orders --symbol BTCUSDT
```

## Trading (use with caution)

```bash
# Spot
python scripts/binance_handler.py spot-order BTCUSDT buy market 0.001
python scripts/binance_handler.py spot-order BTCUSDT buy limit 0.001 --price 50000
python scripts/binance_handler.py cancel BTCUSDT 12345678

# Futures
python scripts/binance_handler.py futures-order BTCUSDT buy market 0.01
python scripts/binance_handler.py futures-order BTCUSDT sell limit 0.01 --price 100000
python scripts/binance_handler.py futures-cancel BTCUSDT 12345678
```

## Safety Rules

- **ALWAYS confirm with user before placing or canceling orders**
- Read-only commands (price, balance, positions) are safe to run freely
- For order placement: state symbol, side, type, quantity, price clearly and wait for explicit approval
- Prefer testnet (`BINANCE_TESTNET=true`) for testing

## Symbol Format
- Always uppercase: `BTCUSDT`, `ETHUSDT`, `SOLUSDT`
- Pairs end in quote asset: `USDT`, `BTC`, `ETH`, `BUSD`

## Kline Intervals
`1m` `3m` `5m` `15m` `30m` `1h` `2h` `4h` `6h` `8h` `12h` `1d` `3d` `1w` `1M`

## Common Errors

| Code | Cause | Fix |
|------|-------|-----|
| -1121 | Invalid symbol | Check symbol name |
| -2010 | Insufficient balance | Check balance first |
| -1013 | Invalid quantity | Check LOT_SIZE filter |
| -2015 | Invalid API key | Check env vars |
| -1022 | Invalid signature | Check secret key |
| -1021 | Timestamp out of sync | Check system clock |

## Output Format

```json
{
  "success": true,
  "data": { ... }
}
```

All commands return JSON with `success` boolean. Non-zero balances/positions only.
