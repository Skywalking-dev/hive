---
name: gate
description: Query Gate.io spot/futures markets, earn products, check balances, manage orders and positions. Use when user needs Gate.io crypto prices, portfolio status, trade execution, or earn management.
allowed-tools: Bash, Read
---

# Gate.io API v4

Spot + Futures (USDT perps) + Earn (UniLoan, Dual Investment).

## Prerequisites
- `GATE_API_KEY` in `.env`
- `GATE_SECRET_KEY` in `.env`

## Spot

```bash
# Prices
python scripts/gate_handler.py price BTC_USDT
python scripts/gate_handler.py prices --filter BTC
python scripts/gate_handler.py ticker ETH_USDT

# Market data
python scripts/gate_handler.py klines BTC_USDT 4h --limit 50
python scripts/gate_handler.py orderbook BTC_USDT --limit 20

# Account
python scripts/gate_handler.py balance
python scripts/gate_handler.py orders --pair BTC_USDT
python scripts/gate_handler.py trades BTC_USDT

# Trading
python scripts/gate_handler.py spot-order BTC_USDT buy market 0.001
python scripts/gate_handler.py spot-order BTC_USDT buy limit 0.001 --price 50000
python scripts/gate_handler.py cancel BTC_USDT 12345678
```

## Futures (USDT perps)

```bash
# Prices & data
python scripts/gate_handler.py futures-price BTC_USDT
python scripts/gate_handler.py futures-ticker BTC_USDT
python scripts/gate_handler.py futures-klines BTC_USDT 1h --limit 50
python scripts/gate_handler.py futures-orderbook BTC_USDT --limit 20
python scripts/gate_handler.py funding-rate BTC_USDT --limit 10

# Account
python scripts/gate_handler.py futures-balance
python scripts/gate_handler.py positions
python scripts/gate_handler.py futures-orders --contract BTC_USDT
python scripts/gate_handler.py futures-trades BTC_USDT

# Trading (size: >0=long, <0=short; price 0=market)
python scripts/gate_handler.py futures-order BTC_USDT 10               # market long 10 contracts
python scripts/gate_handler.py futures-order BTC_USDT -5               # market short 5 contracts
python scripts/gate_handler.py futures-order BTC_USDT 10 --price 50000 # limit long
python scripts/gate_handler.py futures-order BTC_USDT 10 --reduce-only # reduce only
python scripts/gate_handler.py futures-cancel 12345678

# Leverage
python scripts/gate_handler.py set-leverage BTC_USDT 20    # isolated 20x
python scripts/gate_handler.py set-leverage BTC_USDT 0     # cross margin
```

## Earn (UniLoan / Simple Earn)

```bash
# Browse products
python scripts/gate_handler.py earn-products
python scripts/gate_handler.py earn-products --currency USDT

# Positions & history
python scripts/gate_handler.py earn-positions
python scripts/gate_handler.py earn-positions --currency USDT
python scripts/gate_handler.py earn-interest --currency USDT
python scripts/gate_handler.py earn-history --currency USDT

# Lend / redeem
python scripts/gate_handler.py earn-lend USDT 100
python scripts/gate_handler.py earn-lend USDT 100 --min-rate 0.0001
python scripts/gate_handler.py earn-redeem USDT 50
```

## Earn (Dual Investment)

```bash
python scripts/gate_handler.py dual-products
python scripts/gate_handler.py dual-order 12345 100
python scripts/gate_handler.py dual-orders
```

## Safety Rules

- **ALWAYS confirm with user before placing/canceling orders or earn operations**
- Read-only commands (price, balance, positions, earn-products) are safe
- For futures: state contract, size, direction, price, leverage clearly
- For earn: state currency, amount, confirm before lend/redeem

## Pair/Contract Format
- Underscore separated, uppercase: `BTC_USDT`, `ETH_USDT`, `SOL_USDT`
- Same format for spot pairs and futures contracts

## Intervals
- Spot: `10s` `1m` `5m` `15m` `30m` `1h` `4h` `8h` `1d` `7d` `30d`
- Futures: `10s` `1m` `5m` `15m` `30m` `1h` `4h` `8h` `1d` `7d`

## Common Errors

| Label | Cause | Fix |
|-------|-------|-----|
| INVALID_CURRENCY_PAIR | Bad pair name | Check format (BTC_USDT) |
| BALANCE_NOT_ENOUGH | Insufficient balance | Check balance first |
| INVALID_PARAM_VALUE | Bad parameter | Check amount/price/size |
| INVALID_KEY | Invalid API key | Check env vars |
| INVALID_SIGNATURE | Bad signature | Check secret key |
| POSITION_NOT_FOUND | No position for contract | Check positions first |
| ORDER_NOT_FOUND | Invalid order ID | Check open orders |

## Output Format

```json
{
  "success": true,
  "data": { ... }
}
```

All commands return JSON with `success` boolean. Non-zero balances/positions only.
