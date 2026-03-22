---
name: flight-search
description: Search and compare flight prices via Google Flights and Amadeus. Use when user asks to find flights, compare prices, explore cheapest dates, or track flight deals.
---

# Flight Search

Search flights via Google Flights (fli library) and optionally Amadeus API.

## When to Use

- User asks to find/search flights between cities
- User wants to compare flight prices
- User wants to explore cheapest travel dates
- User asks about flight deals or price tracking

## Script

All searches go through `hive/scripts/flight_tracker.py`. Always use `--json` for structured output, then present results in a readable table.

## Commands

### Search specific flights

```bash
# One-way
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from <ORIGIN> --to <DEST> --date <YYYY-MM-DD>

# Round-trip
uv run python /Users/gpublica/workspace/skywalking/hive/scripts/flight_tracker.py --json search --from <ORIGIN> --to <DEST> --date <YYYY-MM-DD> --return-date <YYYY-MM-DD>

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
| `--json` | flag | false | JSON output for programmatic use |

## Currency Detection

The script auto-detects currency based on route:
- **Argentina airports** (EZE, AEP, COR, etc.) → ARS with USD conversion via live rates
- **All other routes** → EUR (Google Flights default for non-AR locale)
- Override with `--currency` flag

## Data Sources

| Source | Status | Env Vars |
|--------|--------|----------|
| Google Flights (fli) | Active | none needed |
| Amadeus | Ready (needs account) | AMADEUS_CLIENT_ID, AMADEUS_CLIENT_SECRET |

## Presenting Results

After running the script with `--json`, parse the output and present to the user as a markdown table:

```markdown
| Aerolinea | Precio | ~USD | Escalas | Duracion | Salida | Llegada |
|-----------|--------|------|---------|----------|--------|---------|
```

Include:
- Route and dates in header
- Currency and conversion rate if ARS
- Cheapest option highlighted
- Booking link to Google Flights when relevant

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
