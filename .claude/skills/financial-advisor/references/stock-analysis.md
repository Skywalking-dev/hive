# Stock Analysis Reference

## Valuation Deep Dive

### P/E Ratio Benchmarks by Sector (Feb 2026)

| Sector | Typical P/E | Notes |
|--------|------------|-------|
| Technology | 25-40 | Higher justified by growth |
| Healthcare | 15-25 | Wide range (biotech vs pharma) |
| Financials | 10-15 | Lower due to cyclicality |
| Utilities | 15-20 | Stable, bond-like |
| Consumer Staples | 18-25 | Defensive premium |
| Energy | 8-15 | Cyclical, commodity-driven |
| Industrials | 15-22 | GDP-sensitive |
| Real Estate (REITs) | N/A | Use P/FFO instead |

### PEG Ratio (P/E to Growth)
- PEG = P/E / annual EPS growth rate
- <1.0 = undervalued relative to growth
- 1.0-1.5 = fairly valued
- >2.0 = overvalued or growth priced in
- Limitation: assumes growth is sustainable and predictable

### EV/EBITDA vs P/E
- EV/EBITDA is capital-structure neutral (ignores debt)
- Better for comparing companies with different leverage
- Better for M&A valuations
- Use P/E for equity-level analysis, EV/EBITDA for enterprise-level

### Price-to-Book by Industry
- Banks: ~1.0-1.5x (below 1.0 = distressed or opportunity)
- Tech: 5-15x+ (intangible assets dominate)
- REITs: ~1.0-2.0x (close to NAV)
- Manufacturing: 1.5-3.0x

## Fundamental Analysis Workflow

### Step 1: Screen (Quantitative)
1. Revenue growth >10% TTM
2. Positive FCF
3. ROE >15%
4. Debt/Equity <1.0
5. P/E <25 or PEG <1.5

### Step 2: Quality (Qualitative)
1. Identify economic moat type
2. Management track record (capital allocation)
3. Industry tailwinds or headwinds
4. Competitive positioning
5. Insider ownership/transactions

### Step 3: Valuation
1. DCF model (intrinsic value)
2. Comparable company analysis (relative value)
3. Historical P/E range (cyclical view)
4. Margin of safety assessment (20-40% discount)

### Step 4: Timing
1. Technical setup (above 200-day MA, RSI 30-65)
2. Macro environment (rate cycle, sector rotation)
3. Earnings calendar (avoid buying right before uncertain earnings)
4. Position sizing based on conviction level

## DCF Model Template

### Assumptions
```
Revenue Growth Year 1-3: [based on recent trend]
Revenue Growth Year 4-5: [taper toward industry average]
Terminal Growth: 2-3% (GDP growth)
Operating Margin: [based on historical trend]
Tax Rate: 21% (US corporate)
WACC: 8-12% (varies by risk profile)
```

### Sensitivity Table
Build a matrix varying:
- Rows: WACC (8%, 9%, 10%, 11%, 12%)
- Columns: Terminal Growth (1%, 2%, 3%, 4%)
- Cell values: Implied share price
- Find the range of intrinsic values

### Sanity Checks
- Implied terminal P/E should be reasonable (10-20x)
- Terminal value should be <70% of total DCF value
- FCF growth shouldn't exceed revenue growth long-term
- Compare to current market price for margin of safety

## Technical Analysis Patterns

### Moving Average Strategies

**Golden Cross (Bullish)**
- 50-day SMA crosses above 200-day SMA
- Confirms shift from downtrend to uptrend
- Best when accompanied by rising volume
- Historical win rate: ~65% over following 12 months

**Death Cross (Bearish)**
- 50-day SMA crosses below 200-day SMA
- Confirms shift from uptrend to downtrend
- Trigger for defensive positioning
- More reliable in longer timeframes

**EMA vs SMA**
- EMA weights recent prices more heavily
- Better for short-term trading signals
- SMA better for long-term trend identification
- Use 12/26 EMA for MACD calculation

### RSI Divergence Trading
- **Bullish Divergence**: Price makes lower low, RSI makes higher low → reversal up
- **Bearish Divergence**: Price makes higher high, RSI makes lower high → reversal down
- Most reliable on daily/weekly timeframes
- Always confirm with volume and another indicator

### Bollinger Band Squeeze
- When bands contract to narrow range → volatility expansion imminent
- Direction of breakout determines trade direction
- Volume spike on breakout = confirmation
- False breakouts common → use stop-losses

## Dividend Investing Deep Dive

### Dividend Aristocrats Selection Criteria
- S&P 500 member
- 25+ consecutive years of dividend increases
- Minimum market cap and liquidity requirements
- Current list: 69 companies (2026)

### Dividend Kings (50+ Years)
- Even more elite: 50+ consecutive years
- Examples: Coca-Cola (62 years), J&J (62), P&G (68)
- Ultimate "sleep well at night" stocks

### Dividend Safety Metrics
1. **Payout Ratio**: Dividend / EPS. Under 60% = safe. Over 80% = risky.
2. **FCF Payout**: Dividend / FCF. Under 50% = very safe.
3. **Debt/EBITDA**: Under 3x for dividend sustainability.
4. **Dividend Growth Rate**: 5-10% annual growth = healthy.

### DRIP Compound Math
- $10,000 invested at 3.5% yield, 7% dividend growth, 8% stock appreciation
- Year 10: ~$24,000 value, 6.9% yield on cost
- Year 20: ~$62,000 value, 13.5% yield on cost
- Year 30: ~$170,000 value, 26.3% yield on cost
- Reinvestment = snowball effect
