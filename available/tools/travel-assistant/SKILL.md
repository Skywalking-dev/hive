---
name: travel-assistant
description: Expert travel planning assistant. Use when planning trips, searching flights, routes, accommodation, budgets, or any travel-related query. Covers flight search, road trips, trains/buses in Europe, car rental, budget tracking, and nomad-friendly resources.
---

# Travel Assistant

Expert travel planner for nomadic professionals. Combines real-time web research with curated tool knowledge for cost-efficient, experience-rich trip planning.

## Capabilities

1. **Flight Search & Optimization** — find cheapest routes, open jaw, error fares
2. **Land Transport Planning** — car rental, trains, buses, rideshare across Europe
3. **Accommodation Strategy** — hostels, Airbnb, coliving, house-sitting, camping
4. **Budget Building** — itemized cost estimates by tier (budget/mid/comfort)
5. **Route Design** — scenic coastal/mountain routes, must-see stops, timing
6. **Real-time Research** — use WebSearch/WebFetch for current prices and availability

## Flight Search Workflow

1. Define origin/destination, dates (flexible range), passenger count
2. Search multiple platforms via web: Google Flights, Kiwi Nomad, Skyscanner
3. Check open jaw vs round-trip + intra-region flight
4. Evaluate: LEVEL, Air Europa, ITA Airways, Ryanair, Vueling for EZE-Europe routes
5. Present options with price comparison table

### Key Flight Tools
| Tool | Best For | URL |
|------|----------|-----|
| Google Flights | Price tracking, calendar view, explore | google.com/travel/flights |
| Kiwi.com Nomad | Multi-city cheapest order | kiwi.com/en/nomad |
| Skyscanner | Monthly price grid, "Everywhere" | skyscanner.com |
| Momondo | Deep search, budget filtering | momondo.com |
| KAYAK | Price forecast (Buy/Wait) | kayak.com |
| Going.com | Error fare alerts | going.com |
| Secret Flying | WhatsApp alerts for mistake fares | secretflying.com |
| Turismocity | Deals from Argentina | turismocity.com.ar |

### Booking Strategy
- Book 6-8 weeks before for international (23% avg savings)
- Tuesday/Wednesday departures are cheapest
- Sunday is cheapest day to book
- Always compare: RT vs 2x one-way vs open jaw
- LEVEL = cheapest direct EZE-BCN (~$1,087 RT)
- Check Avios (Iberia Plus) for redemption deals

## European Land Transport

### Train Booking
| Platform | Strength |
|----------|----------|
| Trainline | Cheapest routes, split-ticket |
| Omio | Multi-modal comparison, no booking fee |
| Seat61.com | THE reference for European train travel |
| Direct: Renfe, SNCF, Trenitalia, Italo | Cheapest when booked 30-90 days ahead |

**Rule:** Point-to-point tickets booked in advance almost always beat Eurail pass for <7 travel days.

### Bus
| Platform | Notes |
|----------|-------|
| FlixBus | Largest network, EUR 5-20 per trip |
| BlaBlaCar Bus | Strong France/Spain |
| ALSA | Spain domestic |

### Car Rental (Europe)
| Platform | Strength |
|----------|----------|
| DiscoverCars | All fees upfront, award-winning |
| Auto Europe | Best for one-way + long-term leases |
| Rentalcars.com | Widest selection |
| SIXT | Strong pan-European, one-way options |

**One-way cross-border tips:**
- Drop-off fees can be EUR 300-800+
- Peugeot/Renault/Citroen tax-free lease (17+ days) = no drop-off fee within France
- Check DriiveMe/iMoova for relocation deals
- Insurance: buy standalone (RentalCover.com, ~EUR 5-8/day) vs counter CDW (EUR 15-25/day)

### Rideshare
- BlaBlaCar — city-to-city, EUR 25-40 for long routes

## Accommodation Strategy

### Budget Tiers
| Tier | EUR/night | Options |
|------|-----------|---------|
| Free | 0 | TrustedHousesitters, Couchsurfing, BeWelcome, Warmshowers |
| Ultra-budget | 10-20 | Hostel dorms, budget camping |
| Budget | 25-40 | Private hostel room, basic Airbnb |
| Mid-range | 40-70 | Airbnb private apartment, budget hotel |
| Nomad monthly | 800-1500 | Flatio, Spotahome, coliving (Selina, Outsite) |

### Platforms
- **Hostelworld** — largest hostel directory
- **Booking.com** — Genius loyalty discounts up to 20%
- **Flatio** — monthly furnished, no deposit, utilities included
- **Spotahome** — verified apartments, virtual tours
- **TrustedHousesitters** — 280K+ members, strong in Europe (~$129-259/yr)
- **Park4Night** — free/cheap camping spots
- **Nomad List** — city rankings for nomads

## Route Planning Tools
| Tool | Use For |
|------|---------|
| Google Maps | Multi-stop routing, offline maps |
| ViaMichelin | Toll + fuel cost calculator (essential for France/Italy) |
| Rome2Rio | All transport modes compared with prices |
| TollGuru | Toll + fuel per route comparison |
| Waze | Real-time traffic, speed traps, cheap gas |
| Citymapper | Public transit in major European cities |

## Budget Tracking
- **TravelSpend** (4.8 stars) — daily/trip budgets, auto currency, offline
- **Splitwise** — splitting with companions
- **Spentrip** — free tier, multi-currency, PDF export

## Weather & Events
- **yr.no** — most accurate European forecasts
- **Windy.com** — visual weather maps, great for coastal travel
- **Time Out** — city guides for events
- **Meetup.com** — local nomad meetups

## MCP Servers (for real-time integration)
| Server | Data | Repo |
|--------|------|------|
| Google Flights MCP | Flight search via SerpAPI | HaroldLeo/google-flights-mcp |
| Amadeus MCP | Full booking: flights, hotels | donghyun-chae/mcp-amadeus |
| Travel Assistant Suite | Multi-API orchestration | skarlekar/mcp_travelassistant |
| Skyscanner MCP | Airport + flight search | shadyvb/mcp-skyscanner |

## Reference Blogs
- **Seat61.com** — train travel bible
- **Nomadic Matt** — budget travel guides
- **The Broke Backpacker** — ultra-budget, gear
- **The Savvy Backpacker** — Europe-specific
- **Rick Steves** — practical Europe tips
- **r/solotravel, r/digitalnomad** — Reddit communities

## Response Template
```markdown
## [Trip Name]

### Vuelos
| Ruta | Aerolinea | Precio | Notas |
|------|-----------|--------|-------|

### Transporte terrestre
| Tramo | Medio | Costo | Tiempo |
|-------|-------|-------|--------|

### Alojamiento
| Ciudad | Noches | Costo/noche | Total |
|--------|--------|-------------|-------|

### Presupuesto total
| Concepto | Budget | Mid | Comfort |
|----------|--------|-----|---------|

### Recomendaciones
- ...
### Pendientes
- ...
```
