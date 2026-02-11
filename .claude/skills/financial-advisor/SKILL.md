---
name: financial-advisor
description: Analyze crypto portfolio across Binance and Gate.io. Use when user asks about their holdings, portfolio health, rebalancing, earn strategies, dust cleanup, market analysis, or overall financial position.
allowed-tools: Bash, Read
---

# Financial Advisor — Crypto Portfolio

Multi-exchange portfolio analysis and advisory for Binance + Gate.io.
User based in Argentina — no crypto tax obligations for individuals.

---

## 1. Portfolio Structure

### Binance
- **Main holdings**: BTC, BNB in Simple Earn Flexible (earning yield)
- **Spot**: BTC, BNB + residual delisted tokens (EDG, VIA — irrecoverable)
- **LD* tokens in spot = Simple Earn positions** (Binance prefixes with `LD`)
- BNB in Simple Earn auto-qualifies for Launchpool (no need to move)

### Gate.io
- **Earn (Uni Lending)**: AKT, AR, GT, METIS — variable interest, auto-reinvest
- **Spot**: GT (small), AKT locked (from earn redemption cycles)
- GT holders get Startup IEO access + up to 50% fee discount
- Uni Lending APY: 5-20% depending on demand

### Dashboard
- Pandora app at `projects/pandora/app/portfolio/page.tsx`
- Sync endpoints: `/api/crypto/sync-binance`, `/api/crypto/sync-gateio`
- Data in Supabase: `crypto_holdings`, `crypto_price_cache`
- Holdings with value <$0.01 filtered from UI

---

## 2. Quick Commands

```bash
# Portfolio Overview
python scripts/binance_handler.py balance
python scripts/gate_handler.py balance

# Prices
python scripts/binance_handler.py price BTCUSDT
python scripts/gate_handler.py price BTC_USDT

# Binance Simple Earn positions
python3 -c "
import os, time, hmac, hashlib, json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
key, secret = os.environ['BINANCE_API_KEY'], os.environ['BINANCE_SECRET_KEY']
params = {'size': 100, 'timestamp': int(time.time()*1000), 'recvWindow': 5000}
qs = urlencode(params)
sig = hmac.new(secret.encode(), qs.encode(), hashlib.sha256).hexdigest()
req = Request(f'https://api.binance.com/sapi/v1/simple-earn/flexible/position?{qs}&signature={sig}', headers={'X-MBX-APIKEY': key})
with urlopen(req, timeout=15) as r: data = json.loads(r.read())
for p in data.get('rows',[]):
    if float(p['totalAmount']) > 0: print(f\"{p['asset']:>8s}  {p['totalAmount']}  rewards={p.get('cumulativeTotalRewards','?')}\")
"

# Gate.io Uni Lending positions
python3 -c "
import sys; sys.path.insert(0,'.')
from scripts.gate_handler import signed_call
import json
r = signed_call('/earn/uni/lends')
if r['success']:
    for b in r['data']: print(f\"{b['currency']:>8s}  amount={b['amount']}  lent={b['lent_amount']}\")
"

# Market data
python scripts/binance_handler.py klines BTCUSDT 1d --limit 30
python scripts/gate_handler.py klines BTC_USDT 1d --limit 30

# Dust check
# Binance: POST /sapi/v1/asset/dust-btc → list, POST /sapi/v1/asset/dust → BNB
# Gate.io: GET /wallet/small_balance → list, POST /wallet/small_balance → GT
```

---

## 3. Allocation Framework

### Models by Risk Profile

| Profile | BTC | ETH | Alts | Stablecoins |
|---------|-----|-----|------|-------------|
| Conservative | 70-80% | 15% | 5% | 5-10% |
| Moderate | 60% | 25% | 10% | 5% |
| Aggressive | 50% | 25% | 20% | 5% |

### Rules
- **Concentration alert**: >50% in single asset = flag it
- **Small portfolio (<$500)**: max 3-5 positions, no micro-alts
- **Rebalancing trigger**: when any asset deviates >15% from target allocation
- **Rebalancing frequency**: quarterly, or threshold-based
- **Prefer rebalancing within same exchange** to avoid withdrawal fees
- **Stablecoins as dry powder**: keep 5-10% for buying dips during corrections

### Position Sizing
- Per trade: 1-3% of portfolio (conservative), 3-5% (aggressive)
- Speculative coins: max 5-10% total, never >2% per coin
- Never invest more than you can lose completely

---

## 4. Risk Management

### Stop-Loss Strategy
- Trailing stop: 8-15% for crypto (adapts to volatility)
- ATR-based trailing for volatile assets (tighten in calm, widen in chaos)
- Max acceptable portfolio drawdown: 20-30%

### Correlation Awareness
- BTC, ETH, LTC: highly correlated — don't treat as diversification
- Low correlation assets for diversification: ARB, TAO, LINK
- Stablecoins: near-zero correlation to BTC — true hedge

### Exchange Risk
- Diversify across exchanges (don't keep everything on one)
- Binance PoR: >100% reserves (June 2025 audit)
- Gate.io: check PoR periodically
- PoR confirms reserves, NOT solvency (excludes off-chain debts)
- For large holdings: consider self-custody (hardware wallet)

---

## 5. Yield / Earn Strategy

### Current Products

| Platform | Product | Typical APR | Redemption |
|----------|---------|-------------|------------|
| Binance | Simple Earn Flexible | 0.9-4.5% | Instant |
| Binance | Simple Earn Locked | Higher APR | Lock period |
| Gate.io | Uni Lending | 5-20% | Variable |
| Gate.io | HODL & Earn | Up to 50% | 60-day lock |

### Optimization Rules
- **Idle spot → earn always** — no reason to leave coins sitting
- Switch products when APR differential >2-3% after fees
- Never lock >50% of holdings (liquidity matters)
- Binance BNB in Simple Earn = auto Launchpool eligibility (free alpha)
- Gate.io GT = fee discounts + IEO access (hold some)

### Yield Red Flags
- APR >20% without clear yield source = probably unsustainable
- New platforms without track record = counterparty risk
- 2022-2023 lesson: Celsius, BlockFi, FTX collapsed — prefer established platforms

### DeFi vs CEX
- DeFi (Aave): up to 6.5% stablecoins, non-custodial, $1M balance protection
- CEX: user-friendly, competitive rates, custodial risk
- For this portfolio size: CEX earn is fine, DeFi gas fees would eat returns

---

## 6. Market Analysis Toolkit

### On-Chain Indicators
- **Fear & Greed Index**: 0-100 scale. <25 = buy signal (extreme fear), >75 = consider taking profits
- **BTC Dominance**: rising = risk-off. ~60% peak then decline = altseason starting
- **Funding Rates**: extreme positive = overleveraged longs, potential correction
- **Exchange Flows**: inflows = selling pressure, outflows = hodling

### Technical Indicators
- **RSI**: >70 overbought, <30 oversold. Best combined with MACD
- **MACD**: bullish/bearish crossovers for trend confirmation
- **RSI + MACD combo**: 77% win rate in BTC backtests
- **Bollinger Bands**: bands contracting = volatility incoming
- **Volume**: always confirm moves with volume

### Macro Indicators
- **DXY (Dollar Index)**: inverse correlation with crypto. DXY down = crypto up
- **Interest Rates**: cuts = bullish, hikes = bearish
- **Fed policy**: 3 rate cuts in 2025 = supportive backdrop

---

## 7. Market Cycles

### Bitcoin Halving Cycle
- Last halving: April 2024 (reward: 6.25 → 3.125 BTC)
- Next halving: ~April 2028
- Historical pattern: bull market peaks 12-18 months post-halving
- BTC reached $109,350 in Jan 2025, corrected to $78,000 by Feb 2025

### Current Cycle (Feb 2026)
- Post-halving consolidation phase
- BTC around $68,000 — mid-cycle correction territory
- Analysts split: some say bear started, others say "long exhausting bull" into 2026
- Key level: $60,000 support, $100,000+ targets if macro aligns

### Altseason Indicators
- BTC dominance peaks at ~60% then declines
- 75% of top alts outperforming BTC over 3 months = confirmed altseason
- Pattern: BTC leads first, altseason in latter bull stages
- Q4 2025 Altseason Index: 31 (no altseason yet)

---

## 8. Profit-Taking Framework

### Laddered Exit Strategy
- Sell 15% at 1.5x from entry
- Sell 15% (of remainder) at 3x
- Sell 25% at 5x
- Keep 5-10% as "moon bag" (never sell)

### DCA-Out (Dollar Cost Average selling)
- Sell fixed % at regular intervals during bull runs
- Example: 10% weekly for 10 weeks
- Removes emotion from selling decisions

### When to Take Profits
- Fear & Greed Index >75 (extreme greed)
- After >50% portfolio gain
- Near historical cycle tops (12-18 months post-halving)
- When initial investment recovered (play with house money)

### Bear Market Survival
- Core holdings BTC/ETH: 50-80% of portfolio
- DCA weekly/monthly through the bear
- Keep 0.5-1% risk per trade max
- Earn yield on holdings (staking/lending)
- Death cross (50-day MA below 200-day MA) = defensive mode

---

## 9. Emerging Trends (2025-2026)

### Watch List
- **RWA (Real World Assets)**: $33B market, 5x in 2 years. BlackRock BUIDL, tokenized Treasuries
- **AI + Crypto**: TAO, FET, RNDR, NEAR. $24-27B market cap. AI agents on-chain
- **Bitcoin L2**: Lightning (payments), Stacks (DeFi), Merlin ($1.7B TVL), Hemi ($1.2B TVL)
- **Restaking**: EigenLayer $18B TVL, 85%+ market share. LRTs (ether.fi, Renzo, KelpDAO)
- **Regulatory**: US pro-crypto pivot (GENIUS Act July 2025), EU MiCA full effect

### Stablecoin Intelligence
- USDT: largest, S&P downgraded, offshore-focused
- USDC: US-regulated, Circle, more transparent reserves
- De-peg risk: diversify between issuers, don't hold 100% in one stablecoin
- Stablecoin yield: 5-15% on CEX, up to 6.5% DeFi (Aave)

---

## 10. Dust Cleanup Protocol

1. **Binance Earn dust**: redeem small positions via `POST /sapi/v1/simple-earn/flexible/redeem` (redeemAll=true)
2. **Wait 3-5 seconds** for settlement
3. **Binance spot dust**: `POST /sapi/v1/asset/dust` with asset list → BNB
4. **Gate.io spot dust**: `POST /wallet/small_balance` with currency list → GT
5. **Delisted tokens** (EDG, VIA): irrecoverable, ignore
6. **Sub-atomic balances** (TRX 0.0000007, ADA 0.0000001): below dust threshold, ignore

---

## 11. Exchange-Specific Intelligence

### Binance
- BNB in Simple Earn = auto Launchpool + HODLer airdrops (no action needed)
- Launchpool avg return: ~300% for early participants
- VIP levels: Soft Staking counts toward VIP 1-4 since June 2025
- Dust conversion: spot only, earn must be redeemed first
- Signing: HMAC-SHA256, query params, `X-MBX-APIKEY` header

### Gate.io
- GT utility: fee discount (up to 50%), Startup IEO allocation, dedicated support
- Uni Lending: auto-matched with borrowers, daily interest, variable rates
- Startup IEO: need VIP1+, subscribe with GT or USDT
- Small balance convert: all eligible currencies → GT in one call
- Signing: HMAC-SHA512, headers (KEY/SIGN/Timestamp), body SHA512 hashed
- Sign path must include `/api/v4` prefix

---

## 12. Common Mistakes to Flag

- **Over-diversification**: <$500 portfolio with >5 positions = diluted returns
- **Chasing APR**: >20% without clear source = red flag
- **Ignoring fees**: $5 withdrawal fee on $100 = 5% loss. Consolidate transfers
- **Holding dead coins**: delisted/frozen tokens won't recover — accept the loss
- **FOMO buying**: 84% of holders acted on FOMO, 63% say it hurt them
- **Never taking profits**: use laddered exits, don't wait for "the top"
- **100% on one exchange**: counterparty risk. Diversify or self-custody

---

## Safety Rules
- **Read-only by default** — balance/price checks are always safe
- **Confirm before ANY trade, redeem, or dust conversion**
- Present clear summary (what, amount, destination) before executing
- Never place orders without explicit user approval

## Response Style
- Lead with total portfolio value
- Show allocation table with % per asset per exchange
- Flag actionable items (idle balances, dust, rate improvements, risk alerts)
- Keep it concise — numbers over narratives
- Use Fear & Greed + BTC dominance for market context
