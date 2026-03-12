# Portfolio Models Reference

## Model 1: Conservative (Capital Preservation)

**Best for**: Risk-averse investors, retirees, or those with short time horizon.

| Asset Class | Allocation | Vehicle | Expected Return |
|-------------|-----------|---------|----------------|
| US Stocks (Large Cap) | 25% | VOO/SPY | 8-10% |
| US Stocks (Dividend) | 10% | SCHD/VYM | 7-9% + 3-4% yield |
| International Stocks | 5% | VXUS | 6-8% |
| US Bonds (Aggregate) | 25% | BND | 4-5% |
| Treasury/TIPS | 10% | TLT/TIPS | 4-5% |
| Gold | 10% | GLD | Variable |
| Crypto (BTC only) | 2% | Direct or IBIT | High variance |
| Cash/Money Market | 13% | HYSA/Money Market | 4-5% |

**Expected portfolio return**: 5-7%
**Expected max drawdown**: -15%
**Rebalancing**: Semi-annual

---

## Model 2: Moderate Growth (Balanced)

**Best for**: Mid-career professionals with 10+ year horizon.

| Asset Class | Allocation | Vehicle | Expected Return |
|-------------|-----------|---------|----------------|
| US Stocks (Core) | 35% | VOO/VTI | 8-10% |
| US Stocks (Growth) | 10% | QQQ/QQQM | 10-15% |
| US Stocks (Dividend) | 10% | SCHD | 7-9% + 3.7% yield |
| International Stocks | 10% | VXUS | 6-8% |
| US Bonds | 10% | BND/IEF | 4-5% |
| Gold | 7% | GLD | Variable |
| Crypto (BTC/ETH) | 5% | 70/30 split | High variance |
| Thematic ETFs | 5% | SMH/ITA | Varies |
| Individual Stocks | 5% | Max 5% each | Varies |
| Cash | 3% | HYSA | 4-5% |

**Expected portfolio return**: 8-10%
**Expected max drawdown**: -25%
**Rebalancing**: Quarterly

---

## Model 3: Aggressive Growth

**Best for**: Young investors with 20+ year horizon and high risk tolerance.

| Asset Class | Allocation | Vehicle | Expected Return |
|-------------|-----------|---------|----------------|
| US Stocks (Core) | 30% | VOO/VTI | 8-10% |
| US Stocks (Growth) | 15% | QQQ + individual | 10-15% |
| International Stocks | 10% | VXUS + EM | 6-8% |
| Individual Stocks | 10% | Conviction picks | Varies |
| Crypto | 10% | BTC 60%, ETH 25%, Alts 15% | High variance |
| Thematic ETFs | 10% | AI, Defense, Nuclear | Varies |
| Gold | 5% | GLD | Variable |
| Bonds | 5% | BND/HYG | 4-6% |
| Cash | 5% | Dry powder | 4-5% |

**Expected portfolio return**: 10-14%
**Expected max drawdown**: -35%
**Rebalancing**: Quarterly + threshold (>5% drift)

---

## Model 4: All Weather (Dalio, Updated 2026)

**Best for**: All conditions; minimize drawdowns, sacrifice some upside.

| Asset Class | Allocation | Vehicle | Rationale |
|-------------|-----------|---------|-----------|
| US Stocks | 30% | VTI | Growth engine |
| Long-Term Bonds | 35% | TLT | Deflation hedge |
| Intermediate Bonds | 15% | IEF | Moderate duration |
| Gold | 12% | GLD | Inflation hedge + crisis |
| Commodities | 5% | GSG/DJP | Inflation hedge |
| Cash | 3% | HYSA | Liquidity |

**Key principle**: Risk parity — equal risk contribution from each asset class.
**2026 modification**: Increased gold from 7.5% to 12% due to structural demand.
**Historical performance**: ~7% CAGR with <15% max drawdown.

---

## Model 5: Barbell Strategy

**Best for**: Those who want maximum convexity — protect capital + capture asymmetric upside.

**Safe End (75%)**:
| Asset | Allocation | Vehicle |
|-------|-----------|---------|
| Treasury Bonds | 30% | TLT/IEF |
| IG Corporate Bonds | 15% | LQD |
| Dividend Stocks | 15% | SCHD/VYM |
| Cash/Money Market | 10% | HYSA |
| Gold | 5% | GLD |

**Speculative End (25%)**:
| Asset | Allocation | Vehicle |
|-------|-----------|---------|
| Growth Stocks | 8% | Individual picks |
| Crypto | 7% | BTC/ETH/alts |
| Thematic ETFs | 5% | SMH, ITA, ARKK |
| Early-stage/Venture | 3% | If accessible |
| Options (defined risk) | 2% | Calls/LEAPs |

**Nothing in the middle**: Avoid medium-risk assets with insufficient upside and meaningful downside.

---

## Model 6: Argentine Investor (via CEDEARs)

**Best for**: Argentine residents wanting USD-linked returns via local market.

| Asset | Allocation | Vehicle | Notes |
|-------|-----------|---------|-------|
| CEDEARs (S&P 500) | 25% | SPY CEDEAR | Core US exposure |
| CEDEARs (NASDAQ) | 10% | QQQ CEDEAR | Growth tilt |
| CEDEARs (Individual) | 15% | AAPL, MSFT, NVDA, MELI | Conviction picks |
| ONs (Hard Dollar) | 15% | Corporate bonds USD | Income + safety |
| Crypto (Binance/Gate) | 10% | BTC/ETH/BNB | Offshore USD exposure |
| FCI Renta Fija | 5% | Via Argentine broker | ARS yield |
| Argentine Stocks | 5% | Merval stocks | Local exposure |
| Gold | 5% | Physical or GLD CEDEAR | Hedge |
| Cash ARS | 5% | Money Market FCI | Liquidity |
| Cash USD | 5% | Stablecoins or MEP | Dry powder |

**Advantages**: CEDEARs exempt from capital gains tax + dollar-linked. ONs provide USD income. Crypto provides offshore diversification.

---

## Position Sizing Rules (All Models)

### Per-Position Limits
- **ETFs**: Up to 25% in a single broad ETF (VOO, VTI)
- **Individual stocks**: Max 5% each, max 20% total
- **Single crypto**: Max 5% (BTC can go higher given dominance)
- **Thematic/speculative**: Max 2-3% per bet

### Risk Per Trade
- Conservative: Max 0.5-1% of portfolio at risk
- Moderate: Max 1-2%
- Aggressive: Max 2-3%
- Formula: `Position Size = (Portfolio * Risk%) / (Entry - Stop Loss)`

### Correlation Adjustment
When two positions are highly correlated (>0.7), count combined position size against limits.
- BTC + MSTR = correlated → combined limit applies
- NVDA + SMH = correlated → choose one, not both

---

## Rebalancing Decision Tree

```
1. Has any allocation drifted >5% from target?
   ├── YES → Evaluate tax impact
   │   ├── Taxable account → Consider tax-loss harvesting first
   │   │   ├── Losers available → Sell losers, harvest loss, rebalance
   │   │   └── No losers → Rebalance with new contributions if possible
   │   └── Tax-advantaged → Rebalance freely
   └── NO → Check calendar
       ├── Quarterly review due → Review allocations, no action needed
       └── Not due → Wait
```

### Tax-Loss Harvesting Rules
1. Sell the losing position
2. Buy a "substantially different" but similar asset (e.g., sell VOO → buy VTI)
3. Wait 31 days before buying back the original (wash sale rule)
4. Offset capital gains dollar-for-dollar
5. If losses > gains: deduct up to $3,000/year from ordinary income

**Argentina note**: Capital gains on CEDEARs are exempt for individuals, so tax-loss harvesting is less relevant for CEDEAR positions. Focus on crypto and international positions.

---

## Risk Budget Framework

Total portfolio risk budget = 100 "risk units"

| Risk Profile | Risk Budget Distribution |
|-------------|------------------------|
| Stocks (equities) | 40-60 units |
| Bonds | 10-20 units |
| Crypto | 10-20 units |
| Gold/Commodities | 5-10 units |
| Cash | 0 units |

**How it works**: Higher volatility assets consume more risk units per dollar invested.
- $1 in VOO ≈ 1 risk unit
- $1 in QQQ ≈ 1.3 risk units (higher volatility)
- $1 in BTC ≈ 3-4 risk units
- $1 in alt crypto ≈ 5-8 risk units
- $1 in BND ≈ 0.3 risk units

This ensures a 5% crypto allocation doesn't dominate portfolio risk.

---

## Emergency Fund Integration

### Sizing by Profile
- Employed (stable job): 3-6 months expenses
- Self-employed/freelancer: 6-12 months
- Sole income for family: 6-12 months
- Approaching retirement: 12-24 months

### Where to Keep It
1. High-yield savings account (HYSA) — 4-5% in 2026
2. Money market fund
3. Short-term Treasury bills
4. **NOT invested** in stocks, crypto, or volatile assets

### Argentina Specific
- Split between ARS and USD
- ARS portion: Money Market FCI (instant liquidity)
- USD portion: Stablecoins (USDC/USDT on CEX) or MEP dollars
- Account for inflation: adjust target every 6 months
- Current monthly expenses ~$4M ARS → 3-month fund = ~$12M ARS

---

## FIRE Framework (Financial Independence)

### 4% Rule (Updated Dec 2025 — Bill Bengen)
- Save 25x annual expenses → withdraw 4% annually
- **Bengen 2025 update**: Early retirees may be "cheating themselves" — 4.7% is safe for 30 years, 4.2% for 50 years under worst historical scenarios
- **Dynamic approach**: 3.5-5.0% variable (cut in down markets, increase in good) — massively increases success rate
- Example: $42.4M ARS/year expenses → need ~$1.06B ARS ($888K USD at CCL 1,200)
- In USD terms: ~$35K/year expenses → need ~$875K USD

### FIRE Numbers by Spending Level

| Annual Spend (USD) | 25x (4% SWR) | 33x (3% SWR - safer) |
|--------------------|--------------|-----------------------|
| $20,000 | $500,000 | $660,000 |
| $35,000 | $875,000 | $1,155,000 |
| $50,000 | $1,250,000 | $1,650,000 |
| $75,000 | $1,875,000 | $2,475,000 |

### Passive Income Streams
1. **Dividends**: 3-5% yield on SCHD/VYM/O
2. **Bond coupons**: 4-6% from BND/LQD
3. **Crypto earn**: 1-5% on stablecoins/BTC
4. **REIT dividends**: 4-6% from VNQ/O
5. **ON coupons**: 5-10% hard dollar (Argentina)
6. **Rental income**: Variable

### Path to FIRE
1. Calculate annual expenses accurately (use Pandora data)
2. Determine FIRE number (25-33x expenses)
3. Calculate savings rate and time to FIRE
4. Invest consistently: DCA into diversified portfolio
5. Track progress quarterly; adjust as expenses change

---

## Buy/Sell Checklists

### Before Buying
- [ ] Written thesis (3 bullets max)
- [ ] Defined exit criteria (target + stop-loss)
- [ ] Position size passes sleep test
- [ ] Not duplicating existing exposure
- [ ] Forward-looking valuation is attractive
- [ ] Macro environment supports the trade

### Before Selling
- [ ] Is original thesis broken? (If yes, sell)
- [ ] Would I buy at current price? (If no, sell)
- [ ] Am I selling for emotional reasons? (If yes, wait 24h)
- [ ] Tax implications considered?
- [ ] Better opportunity for the capital?

### Trade Journal Template
Record for every trade:
1. **Date and ticker**
2. **Thesis**: Why buying/selling? (3 bullets max)
3. **Position size and rationale**
4. **Entry price and target price**
5. **Stop-loss level**
6. **Outcome**: What happened and why?
7. **Lesson**: What would you do differently?

Review monthly. Look for: repeated mistakes, emotional trades, forecast accuracy.
