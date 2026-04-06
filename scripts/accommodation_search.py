#!/usr/bin/env python3
"""
Accommodation Search & Tracker
Search accommodation via Google Hotels (SerpAPI) and Booking.com (RapidAPI).

Usage:
    # Search hotels in a city
    uv run python hive/scripts/accommodation_search.py search --city "Barcelona" --checkin 2026-05-01 --checkout 2026-05-05

    # Search with filters
    uv run python hive/scripts/accommodation_search.py search --city "Rome" --checkin 2026-05-10 --checkout 2026-05-15 --type hostel --max-price 50 --sort price

    # Search for long stays
    uv run python hive/scripts/accommodation_search.py search --city "Milan" --checkin 2026-05-15 --checkout 2026-06-01 --type apartment --sort price

    # Search history
    uv run python hive/scripts/accommodation_search.py history --city "Barcelona"

    # JSON output (for skill consumption)
    uv run python hive/scripts/accommodation_search.py --json search --city "Barcelona" --checkin 2026-05-01 --checkout 2026-05-05
"""

import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# === PATHS ===
HIVE_DIR = Path(__file__).parent.parent
DATA_DIR = HIVE_DIR / "data"
HISTORY_FILE = DATA_DIR / "accommodation_prices.json"
ENV_FILE = HIVE_DIR / ".env"

# === ENV ===

def load_env():
    """Load env vars from hive/.env if not already set."""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = val


# === OUTPUT ===

_json_mode = False


def json_mode() -> bool:
    return _json_mode


# === SERPAPI GOOGLE HOTELS ===


def search_google_hotels(
    query: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    currency: str = "USD",
    sort_by: int = 3,
    min_price: float | None = None,
    max_price: float | None = None,
    property_type: str | None = None,
    free_cancellation: bool = False,
    top_n: int = 15,
) -> list[dict]:
    """Search accommodation via SerpAPI Google Hotels.

    Requires SERPAPI_KEY env var.
    Free tier: 100 searches/month.

    sort_by: 3=lowest price, 8=highest rating, 13=most relevant
    """
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        if not json_mode():
            print("[google_hotels] not configured (set SERPAPI_KEY in hive/.env)")
        return []

    try:
        import urllib.request
        import urllib.parse

        params = {
            "engine": "google_hotels",
            "q": query,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": adults,
            "currency": currency,
            "gl": "us",
            "hl": "en",
            "sort_by": sort_by,
            "api_key": api_key,
        }

        if min_price is not None:
            params["min_price"] = int(min_price)
        if max_price is not None:
            params["max_price"] = int(max_price)
        if free_cancellation:
            params["free_cancellation"] = "true"

        url = f"https://serpapi.com/search?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read())

        properties = data.get("properties", [])
        results = []

        for prop in properties[:top_n]:
            rate = prop.get("rate_per_night", {})
            total = prop.get("total_rate", {})

            price_per_night = rate.get("extracted_lowest") or rate.get("lowest")
            total_price = total.get("extracted_lowest") or total.get("lowest")

            # Parse numeric price from string
            if isinstance(price_per_night, str):
                cleaned = price_per_night.replace("$", "").replace(",", "").replace("€", "").replace("£", "").strip()
                price_per_night = float(cleaned) if cleaned else 0
            if isinstance(total_price, str):
                cleaned = total_price.replace("$", "").replace(",", "").replace("€", "").replace("£", "").strip()
                total_price = float(cleaned) if cleaned else 0

            # Apply type filter
            prop_type = prop.get("type", "Hotel")
            if property_type:
                type_lower = property_type.lower()
                prop_type_lower = prop_type.lower()
                if type_lower not in prop_type_lower and prop_type_lower not in type_lower:
                    continue

            # Extract nearby places safely
            nearby = []
            for p in prop.get("nearby_places", [])[:3]:
                transports = p.get("transportations", [])
                duration = transports[0].get("duration") if transports else None
                nearby.append({"name": p.get("name"), "distance": duration})

            result = {
                "source": "google_hotels",
                "name": prop.get("name", "Unknown"),
                "type": prop_type,
                "stars": prop.get("hotel_class"),
                "rating": prop.get("overall_rating"),
                "reviews": prop.get("reviews"),
                "price_per_night": price_per_night,
                "total_price": total_price,
                "currency": currency,
                "amenities": prop.get("amenities", []),
                "link": prop.get("link"),
                "property_token": prop.get("property_token"),
                "images": [img.get("thumbnail") for img in prop.get("images", [])[:2]],
                "check_in_time": prop.get("check_in_time"),
                "check_out_time": prop.get("check_out_time"),
                "gps": prop.get("gps_coordinates"),
                "description": prop.get("description"),
                "nearby_places": nearby,
            }
            results.append(result)

        return results

    except Exception as e:
        if not json_mode():
            print(f"[google_hotels] error: {e}")
        return []


# === BOOKING.COM VIA RAPIDAPI ===


def _booking_search_dest(query: str) -> dict | None:
    """Search for destination ID on Booking.com."""
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        return None

    try:
        import urllib.request
        import urllib.parse

        url = f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination?query={urllib.parse.quote(query)}"
        req = urllib.request.Request(url, headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "booking-com15.p.rapidapi.com",
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())

        results = data.get("data", [])
        return results[0] if results else None
    except Exception:
        return None


def search_booking(
    query: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    currency: str = "USD",
    sort_by: str = "price",
    min_price: float | None = None,
    max_price: float | None = None,
    property_type: str | None = None,
    top_n: int = 15,
) -> list[dict]:
    """Search accommodation via Booking.com (RapidAPI).

    Requires RAPIDAPI_KEY env var.
    Free tier varies by plan (~500 req/mo typical).
    """
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        if not json_mode():
            print("[booking] not configured (set RAPIDAPI_KEY in hive/.env)")
        return []

    try:
        import urllib.request
        import urllib.parse

        dest = _booking_search_dest(query)
        if not dest:
            if not json_mode():
                print(f"[booking] destination not found: {query}")
            return []

        dest_id = dest.get("dest_id", "")
        search_type = dest.get("search_type", "city")

        sort_map = {
            "price": "price",
            "rating": "review_score",
            "popularity": "popularity",
            "distance": "distance",
        }

        params = {
            "dest_id": dest_id,
            "search_type": search_type,
            "arrival_date": check_in,
            "departure_date": check_out,
            "adults": adults,
            "room_qty": 1,
            "currency_code": currency,
            "sort_by": sort_map.get(sort_by, "price"),
            "page_number": 1,
            "units": "metric",
            "temperature_unit": "c",
            "languagecode": "en-us",
        }

        if min_price is not None:
            params["price_min"] = int(min_price)
        if max_price is not None:
            params["price_max"] = int(max_price)

        url = f"https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "booking-com15.p.rapidapi.com",
        })
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read())

        hotels = data.get("data", {}).get("hotels", [])
        results = []

        for hotel in hotels[:top_n]:
            prop = hotel.get("property", {})
            price_info = prop.get("priceBreakdown", {})

            gross_price = price_info.get("grossPrice", {})
            total_price = gross_price.get("value", 0)

            ci = datetime.strptime(check_in, "%Y-%m-%d")
            co = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (co - ci).days or 1
            price_per_night = round(total_price / nights, 2) if total_price else 0

            accommodation_type = prop.get("accommodationTypeName", "Hotel")

            if property_type:
                if property_type.lower() not in accommodation_type.lower():
                    continue

            photo_urls = prop.get("photoUrls", [])

            # Build Booking.com search link for this property
            hotel_name = prop.get("name", "Unknown")
            booking_link = (
                f"https://www.booking.com/searchresults.html"
                f"?ss={urllib.parse.quote(hotel_name + ' ' + query)}"
                f"&checkin={check_in}&checkout={check_out}"
                f"&group_adults={adults}&no_rooms=1"
            )

            result = {
                "source": "booking",
                "name": hotel_name,
                "type": accommodation_type,
                "stars": prop.get("propertyClass"),
                "rating": prop.get("reviewScore"),
                "reviews": prop.get("reviewCount"),
                "price_per_night": price_per_night,
                "total_price": round(total_price, 2),
                "currency": currency,
                "amenities": [],
                "link": booking_link,
                "images": [photo_urls[0]] if photo_urls else [],
                "gps": {
                    "latitude": prop.get("latitude"),
                    "longitude": prop.get("longitude"),
                },
                "description": prop.get("wishlistName", ""),
            }
            results.append(result)

        return results

    except Exception as e:
        if not json_mode():
            print(f"[booking] error: {e}")
        return []


# === VERIFY AVAILABILITY ===


def verify_property(
    property_token: str,
    query: str,
    check_in: str,
    check_out: str,
    adults: int = 1,
    currency: str = "EUR",
) -> dict | None:
    """Verify availability and get real booking links for a property.

    Uses SerpAPI property details endpoint. Costs 1 search credit.
    Returns confirmed booking options with direct links.
    """
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        if not json_mode():
            print("[verify] not configured (set SERPAPI_KEY in hive/.env)")
        return None

    try:
        import urllib.request
        import urllib.parse

        params = {
            "engine": "google_hotels",
            "q": query,
            "property_token": property_token,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": adults,
            "currency": currency,
            "gl": "us",
            "hl": "en",
            "api_key": api_key,
        }

        url = f"https://serpapi.com/search?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read())

        prices = data.get("prices", [])
        if not prices:
            return {"available": False, "name": data.get("name", "Unknown"), "options": []}

        options = []
        for p in prices:
            rate = p.get("rate_per_night", {})
            options.append({
                "source": p.get("source", "Unknown"),
                "price_per_night": rate.get("extracted_lowest") or rate.get("lowest"),
                "total": p.get("total_rate", {}).get("extracted_lowest"),
                "link": p.get("link", ""),
                "official": p.get("official", False),
                "num_guests": p.get("num_guests"),
                "room_type": p.get("room_name"),
            })

        nearby = []
        for place in data.get("nearby_places", [])[:5]:
            transports = place.get("transportations", [])
            nearby.append({
                "name": place.get("name"),
                "distance": transports[0].get("duration") if transports else None,
                "rating": place.get("rating"),
            })

        return {
            "available": True,
            "name": data.get("name", "Unknown"),
            "description": data.get("description"),
            "overall_rating": data.get("overall_rating"),
            "reviews": data.get("reviews"),
            "amenities": data.get("amenities", []),
            "nearby_places": nearby,
            "options": options,
        }

    except Exception as e:
        if not json_mode():
            print(f"[verify] error: {e}")
        return None


# === HISTORY ===


def load_history() -> list[dict]:
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def save_history(entry: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append(entry)
    HISTORY_FILE.write_text(json.dumps(history, indent=2, default=str))
    return len(history)


def get_history(city: str | None = None, last_n: int = 20) -> list[dict]:
    history = load_history()
    if city:
        city_lower = city.lower()
        history = [h for h in history if city_lower in h.get("city", "").lower()]
    return history[-last_n:]


# === OUTPUT ===


def output(data: dict):
    """Output results — JSON or human-readable."""
    if json_mode():
        print(json.dumps(data, indent=2, default=str))
        return

    if data.get("error"):
        print(f"\nError: {data['error']}")
        return

    command = data.get("command", "")

    if command == "search":
        props = data.get("properties", [])
        print(f"\n{'='*90}")
        print(f"  {data.get('city', '?')} | {data.get('dates', '?')} | {data.get('nights', '?')} nights | {len(props)} results")
        print(f"{'='*90}")

        for p in props:
            name = p.get("name", "?")[:35]
            ptype = p.get("type", "?")[:12]
            rating = p.get("rating")
            reviews = p.get("reviews", 0)
            ppn = p.get("price_per_night", 0)
            total = p.get("total_price", 0)
            cur = p.get("currency", "USD")
            source = p.get("source", "?")[:7]
            stars = f"{'*' * p['stars']}" if p.get("stars") else ""

            rating_str = f"{rating}/10" if rating else "N/A"

            line = f"  {cur} {ppn:>7.0f}/n ({total:>7.0f} tot)"
            line += f" | {name:<35} | {ptype:<12} | {stars:<5} | {rating_str:<7} ({reviews or 0} rev) [{source}]"
            print(line)

        if props:
            valid = [p for p in props if p.get("price_per_night")]
            if valid:
                cheapest = min(valid, key=lambda x: x["price_per_night"])
                print(f"\n  Cheapest: {cheapest['name']} — {cheapest['currency']} {cheapest['price_per_night']:.0f}/night")
            rated = [p for p in props if p.get("rating")]
            if rated:
                best_rated = max(rated, key=lambda x: x["rating"])
                print(f"  Best rated: {best_rated['name']} — {best_rated['rating']}/10")

        sources = set(p["source"] for p in props)
        print(f"  Sources: {', '.join(sources)}")

    elif command == "verify":
        name = data.get("name", "?")
        available = data.get("available", False)
        options = data.get("options", [])

        print(f"\n{'='*80}")
        print(f"  {name} | {'AVAILABLE' if available else 'NOT AVAILABLE'} | {len(options)} booking options")
        print(f"{'='*80}")

        if data.get("overall_rating"):
            print(f"  Rating: {data['overall_rating']}/5 ({data.get('reviews', 0)} reviews)")
        if data.get("nearby_places"):
            places = ", ".join(f"{p['name']} ({p['distance']})" for p in data["nearby_places"][:3] if p.get("distance"))
            print(f"  Near: {places}")

        if options:
            print(f"\n  Booking options:")
            for o in options:
                ppn = o.get("price_per_night", "?")
                src = o.get("source", "?")
                room = o.get("room_type", "")
                official = " [OFFICIAL]" if o.get("official") else ""
                print(f"    {src:<20} {ppn:>7}/n{official}  {room}")
                if o.get("link"):
                    print(f"      {o['link'][:120]}")
        else:
            print("  No booking options available for these dates.")

    elif command == "history":
        entries = data.get("entries", [])
        print(f"\n{'='*70}")
        print(f"  Accommodation Search History | {len(entries)} entries")
        print(f"{'='*70}")
        for entry in entries:
            ts = entry.get("timestamp", "?")[:16]
            city = entry.get("city", "?")
            cheapest = entry.get("cheapest_per_night", 0)
            count = entry.get("result_count", "?")
            cur = entry.get("currency", "USD")
            print(f"  {ts} | {city:<20} | {cur} {cheapest:>7.0f}/n | {count} results")


# === CLI ===


def cmd_search(args):
    """Search accommodation in a city."""
    ci = datetime.strptime(args.checkin, "%Y-%m-%d")
    co = datetime.strptime(args.checkout, "%Y-%m-%d")
    nights = (co - ci).days

    if nights <= 0:
        output({"error": "checkout must be after checkin"})
        return

    dates = f"{args.checkin} → {args.checkout}"

    # Build query for Google Hotels
    query = f"Hotels in {args.city}"
    if args.type:
        type_map = {
            "hostel": "Hostels",
            "apartment": "Vacation rentals",
            "hotel": "Hotels",
            "guesthouse": "Guest houses",
            "bnb": "Bed and breakfasts",
            "villa": "Villas",
            "resort": "Resorts",
        }
        query_type = type_map.get(args.type.lower(), args.type)
        query = f"{query_type} in {args.city}"

    if not json_mode():
        print(f"\nSearching accommodation: {args.city}")
        print(f"Dates: {dates} ({nights} nights) | Adults: {args.adults} | Currency: {args.currency}")
        if args.max_price:
            print(f"Max price: {args.currency} {args.max_price}/night")
        if args.type:
            print(f"Type: {args.type}")

    sort_map = {"price": 3, "rating": 8, "relevance": 13}

    source = getattr(args, "source", "all")
    properties = []

    # Google Hotels (SerpAPI)
    if source in ("all", "google"):
        try:
            gh = search_google_hotels(
                query=query,
                check_in=args.checkin,
                check_out=args.checkout,
                adults=args.adults,
                currency=args.currency,
                sort_by=sort_map.get(args.sort, 3),
                min_price=args.min_price,
                max_price=args.max_price,
                property_type=args.type,
                free_cancellation=args.free_cancel,
                top_n=args.top,
            )
            properties.extend(gh)
        except Exception as e:
            if not json_mode():
                print(f"[google_hotels] error: {e}")

    # Booking.com (RapidAPI)
    if source in ("all", "booking"):
        try:
            bk = search_booking(
                query=args.city,
                check_in=args.checkin,
                check_out=args.checkout,
                adults=args.adults,
                currency=args.currency,
                sort_by=args.sort,
                min_price=args.min_price,
                max_price=args.max_price,
                property_type=args.type,
                top_n=args.top,
            )
            properties.extend(bk)
        except Exception as e:
            if not json_mode():
                print(f"[booking] error: {e}")

    # Sort all by price per night
    properties.sort(key=lambda x: x.get("price_per_night") or float("inf"))

    result = {
        "command": "search",
        "city": args.city,
        "dates": dates,
        "nights": nights,
        "adults": args.adults,
        "currency": args.currency,
        "properties": properties,
    }

    # Save to history
    if properties:
        valid = [p for p in properties if p.get("price_per_night")]
        if valid:
            cheapest = min(valid, key=lambda x: x["price_per_night"])
            save_history({
                "timestamp": datetime.now().isoformat(),
                "city": args.city,
                "dates": dates,
                "nights": nights,
                "cheapest_per_night": cheapest["price_per_night"],
                "cheapest_name": cheapest["name"],
                "currency": args.currency,
                "result_count": len(properties),
            })

    output(result)
    return result


def cmd_verify(args):
    """Verify availability and get booking links for a property."""
    if not json_mode():
        print(f"\nVerifying availability: token={args.token[:30]}...")

    query = f"Hotels in {args.city}" if args.city else "Hotels"

    result = verify_property(
        property_token=args.token,
        query=query,
        check_in=args.checkin,
        check_out=args.checkout,
        adults=args.adults,
        currency=args.currency,
    )

    if result is None:
        output({"command": "verify", "error": "verification failed"})
        return

    result["command"] = "verify"
    output(result)
    return result


def cmd_history(args):
    """Show search history."""
    entries = get_history(
        city=args.city if args.city != "ANY" else None,
        last_n=args.last,
    )

    result = {
        "command": "history",
        "entries": entries,
    }

    output(result)
    return result


def main():
    global _json_mode

    load_env()

    parser = argparse.ArgumentParser(description="Accommodation Search & Tracker")
    parser.add_argument("--json", action="store_true", help="JSON output mode")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # search
    p_search = subparsers.add_parser("search", help="Search accommodation in a city")
    p_search.add_argument("--city", required=True, help="City name (e.g. 'Barcelona')")
    p_search.add_argument("--checkin", required=True, help="Check-in date YYYY-MM-DD")
    p_search.add_argument("--checkout", required=True, help="Check-out date YYYY-MM-DD")
    p_search.add_argument("--adults", type=int, default=1, help="Number of adults (default: 1)")
    p_search.add_argument("--type", help="Property type: hotel, hostel, apartment, guesthouse, bnb, villa, resort")
    p_search.add_argument("--min-price", type=float, help="Min price per night in currency")
    p_search.add_argument("--max-price", type=float, help="Max price per night in currency")
    p_search.add_argument("--sort", default="price", choices=["price", "rating", "relevance"])
    p_search.add_argument("--currency", default="EUR", help="Currency code (default: EUR)")
    p_search.add_argument("--top", type=int, default=15, help="Max results per source")
    p_search.add_argument("--source", default="all", choices=["all", "google", "booking"])
    p_search.add_argument("--free-cancel", action="store_true", help="Only show free cancellation")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify availability and get booking links")
    p_verify.add_argument("--token", required=True, help="property_token from search results")
    p_verify.add_argument("--city", default="", help="City name (for query context)")
    p_verify.add_argument("--checkin", required=True, help="Check-in date YYYY-MM-DD")
    p_verify.add_argument("--checkout", required=True, help="Check-out date YYYY-MM-DD")
    p_verify.add_argument("--adults", type=int, default=1, help="Number of adults (default: 1)")
    p_verify.add_argument("--currency", default="EUR", help="Currency code (default: EUR)")

    # history
    p_history = subparsers.add_parser("history", help="Show search history")
    p_history.add_argument("--city", default="ANY", help="Filter by city")
    p_history.add_argument("--last", type=int, default=20, help="Show last N entries")

    args = parser.parse_args()
    _json_mode = args.json

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "search": cmd_search,
        "verify": cmd_verify,
        "history": cmd_history,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
