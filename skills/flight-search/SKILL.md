---
name: flight-search
description: Search and compare flight prices via Google Flights and Kiwi Tequila. Use when user asks to find flights, compare prices, explore cheapest dates, or track flight deals.
---

# Flight Search

Search flights via Google Flights (fli) and Kiwi Tequila API. Kiwi provides airline discovery + deep links for direct booking on airline websites.

## When to Use

- User asks to find/search flights between cities
- User wants to compare flight prices
- User wants to explore cheapest travel dates
- User asks about flight deals or price tracking

## Strategy: Kiwi Discovery → Airline Direct

1. **Search with Kiwi** → discover routes, airlines, flight numbers, reference prices
2. **Results include `airline_link`** → direct URL to the airline's booking page
3. **Kiwi prices are ~10-20% higher** than airline direct — always recommend checking the airline site

## Script

All searches go through `hive/scripts/flight_tracker.py`. Always use `--json` for structured output, then present results in a readable table.

## Commands

### Search specific flights

```bash
# One-way (all sources)
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from <ORIGIN> --to <DEST> --date <YYYY-MM-DD>

# Round-trip
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from <ORIGIN> --to <DEST> --date <YYYY-MM-DD> --return-date <YYYY-MM-DD>

# Kiwi only (best for airline discovery + deep links)
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from EZE --to BCN --date 2026-05-01 --source kiwi

# Google Flights only
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from FCO --to ATH --date 2026-05-12 --source google

# With filters
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from FCO --to ATH --date 2026-05-12 --stops NON_STOP --sort CHEAPEST --top 5
```

### Explore cheapest dates

```bash
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json explore --from <ORIGIN> --to <DEST> --start <YYYY-MM-DD> --end <YYYY-MM-DD> --min-days <N> --max-days <N>
```

### Price history

```bash
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json history --from <ORIGIN> --to <DEST>
```

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--from` | IATA code | required | Origin airport |
| `--to` | IATA code | required | Destination airport |
| `--date` | YYYY-MM-DD | required (search) | Departure date |
| `--return-date` | YYYY-MM-DD | omit for one-way | Return date |
| `--stops` | ANY, NON_STOP, ONE_STOP_OR_FEWER, TWO_OR_FEWER_STOPS | ANY | Max stops |
| `--sort` | CHEAPEST, TOP_FLIGHTS, DURATION | CHEAPEST | Sort order |
| `--top` | int | 10 | Max results |
| `--exclude` | comma-separated codes | none | Exclude airlines (e.g. AA,DL,UA) |
| `--threshold` | float USD | none | Alert if price below threshold |
| `--currency` | ARS, EUR, USD | auto | Override price currency |
| `--source` | all, google, kiwi | all | Data source filter |
| `--json` | flag | false | JSON output for programmatic use |

## Currency Detection

The script auto-detects currency based on route:
- **Argentina airports** (EZE, AEP, COR, etc.) → ARS with USD conversion via live rates
- **All other routes** → EUR (Google Flights default for non-AR locale)
- **Kiwi** → always requests in USD (no ARS support)
- Override with `--currency` flag

## Data Sources

| Source | Status | Env Vars | Best For |
|--------|--------|----------|----------|
| Google Flights (fli) | Active | none needed | Price accuracy, date exploration |
| Kiwi Tequila | Active | KIWI_API_KEY | Route discovery, airline links, LCC coverage |

## Kiwi Response Fields

Kiwi results include extra fields vs Google Flights:
- `kiwi_link` — direct Kiwi.com booking URL
- `airline_link` — constructed airline website URL (when pattern available)
- `airlines` — all airline IATA codes in the itinerary
- `seats_available` — remaining seats (when available)
- `outbound.legs[]` — detailed per-leg info (flight number, times, cities)

## Presenting Results

After running the script with `--json`, parse the output and present to the user as a markdown table:

```markdown
| Aerolinea | Precio | Escalas | Duracion | Salida | Llegada | Airline Link |
|-----------|--------|---------|----------|--------|---------|-------------|
```

Include:
- Route and dates in header
- Currency and conversion rate if ARS
- Cheapest option highlighted
- **Airline direct link** when available (recommend checking for lower price)
- Kiwi link as fallback

## Common Airport Codes

| Code | City |
|------|------|
| EZE | Buenos Aires (Ezeiza) |
| AEP | Buenos Aires (Aeroparque) |
| BCN | Barcelona |
| FCO | Roma (Fiumicino) |
| ATH | Atenas |
| MXP | Milan (Malpensa) |
| NCE | Niza |
| MRS | Marsella |
| CDG | Paris |
| LHR | Londres |

## History & Tracking

Prices are auto-saved to `hive/data/flight_prices.json` on every search. Use `history` command to review trends.

## Setup

1. Get Kiwi API key: register at https://tequila.kiwi.com → My Applications → Add application
2. Add to `hive/.env`: `KIWI_API_KEY=your_key_here`
