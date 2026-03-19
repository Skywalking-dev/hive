---
name: report-viewer
description: Render detailed reports as styled HTML dashboards and auto-open in browser. Use when generating reports, plans, budgets, comparisons, or any structured output that benefits from visual presentation. MUST follow Skywalking design system — no AI slop.
---

# Report Viewer

Converts structured reports into polished HTML dashboards using Skywalking's refined design language. Saves to `/tmp/` and opens automatically.

## When to Use

- After generating a detailed report with tables, budgets, comparisons
- Any output with 3+ tables or 2+ sections
- When the user explicitly asks for a visual version

## Design Principles — NO AI SLOP

**Monotone + 1 accent.** Everything in grays/slate. Gold (`#D4AF37`) only for what truly matters.

### Never Do
- Colored badge soup (blue/orange/green pills everywhere)
- Multiple competing accent colors
- Generic dark themes with bright colored elements
- Colored left borders on every card
- Using color as decoration instead of information

### Always Do
- Typography for hierarchy: weight, size, opacity, letter-spacing, uppercase
- Phase tags as dim uppercase text, not colored badges
- Generous spacing — let things breathe
- Subtle borders: `rgba(255,255,255,0.06)`
- `.glow` cards only for the ONE most important thing
- Maps: main stops get visible text labels, minor stops tiny dots with hover tooltip

## Color System

```css
:root {
  --bg: #0a0f14;
  --surface: #11171e;
  --raised: #171f28;
  --border: rgba(255,255,255,0.06);
  --text: rgba(239,238,233,0.72);
  --text-dim: rgba(239,238,233,0.38);
  --text-bright: #EFEEE9;
  --accent: #D4AF37;            /* ONLY accent color */
  --accent-dim: rgba(212,175,55,0.12);
}
```

## Typography

- Font: `Plus Jakarta Sans` (Google Fonts import)
- Headings: weight 300-400, large, letter-spacing -1px
- Section labels: 10px, weight 600, letter-spacing 2.5px, uppercase, `--text-dim`
- Card headers: 11px, weight 600, letter-spacing 1.5px, uppercase, `--text-dim`
- Body: 13-14px, weight 400, `--text`
- Emphasis: weight 500, `--text-bright` (NOT bold, NOT colored)
- Phase tags: 10px, letter-spacing 1px, uppercase, `--text-dim`, inline-block width 80px

## Layout

- **Full width** — no max-width container, padding 48-56px sides
- **Hero map** (if applicable) — 85-90vh, full bleed, title overlaid with gradient
- **Stats bar** — full width grid, 1px borders between items
- **Content** — 40-56px padding
- **Grids** — `.g2`, `.g3`, `.g4` for 2/3/4 column layouts
- **Cards** — `--surface` background, `--border` border, 10px radius, 24px padding

## Card Variants

```css
.c { /* default card */ }
.c.glow {
  /* ONLY for most important item */
  border-color: rgba(212,175,55,0.15);
  background: linear-gradient(135deg, rgba(212,175,55,0.03) 0%, var(--surface) 100%);
}
```

## Tables

- No colored header backgrounds — use `--surface-2` (very subtle)
- Thin bottom borders on rows: `var(--border)`
- Column classes: `.concept` (bright), `.val` (right-aligned), `.total` (accent color)
- Phase tables: `.phase-tag` (dim uppercase) + `.phase-name` (bright)
- Highlight rows: only for birthday/special — accent color on name, dim accent on tag

## Timeline

- Left column: date (11px, dim, right-aligned, 90px wide)
- Vertical line: 1px `--border`
- Dots: 7px, raised bg, dim border (default) | accent fill (epic) | accent glow (birthday) | transparent (flights)
- Right body: place (14px, 500 weight, bright) + desc (12px, text) + transport (11px, dim, pill-style spans in raised bg)

## Maps (Leaflet)

### Tiles
```js
// Dark no-labels base + faded labels overlay
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}{r}.png')
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_only_labels/{z}/{x}/{y}{r}.png', {opacity:0.4})
```

### Main Stops (labeled)
```js
// Gold dot + text label with text-shadow
const dotHtml = '<div style="position:relative">'
  +'<div style="width:12px;height:12px;background:#D4AF37;border-radius:50%;border:2px solid #0a0f14;box-shadow:0 0 16px rgba(212,175,55,0.35)"></div>'
  +'<div style="position:absolute;bottom:18px;left:50%;transform:translateX(-50%);white-space:nowrap;text-align:center">'
    +'<div style="font-size:12px;font-weight:600;color:#EFEEE9;text-shadow:0 1px 6px rgba(0,0,0,0.8)">City Name</div>'
    +'<div style="font-size:9px;color:rgba(239,238,233,0.5);text-shadow:0 1px 4px rgba(0,0,0,0.9)">2 noches</div>'
  +'</div></div>';
```

### Minor Stops
```js
L.circleMarker([lat,lng], {
  radius:3, fillColor:'rgba(239,238,233,0.3)', fillOpacity:1,
  stroke:true, color:'rgba(239,238,233,0.15)', weight:1
}).bindTooltip(name, {className:'minor-tip', direction:'top'})
```

### Routes
```js
// OSRM routing, single accent color, opacity 0.5
async function drawRoute(coords, color, weight) {
  const url = 'https://router.project-osrm.org/route/v1/driving/'+coords.join(';')+'?overview=full&geometries=geojson';
  // ... L.geoJSON with {color, weight, opacity:0.5}
}
```

## Budget Cards

```css
.budget-card { text-align:center; padding:28px; }
.budget-card .amt { font-size:36px; font-weight:300; letter-spacing:-1px; }
.budget-card.pick { border-color:rgba(212,175,55,0.2); }
.budget-card.pick .amt { color:var(--accent); font-weight:400; }
```

## Implementation Steps

1. Build HTML using the design system above
2. Write to `/tmp/report-{slug}-{YYYYMMDD}.html`
3. Open with `open /tmp/report-{slug}-{date}.html`

## Reference Implementation

The canonical example is `/tmp/report-viaje-40-20260319.html` — the travel report that went through multiple design iterations with the user to arrive at this aesthetic.

## Anti-pattern Reference

See memory `feedback_design_no_ai_slop.md` for the full list of what NOT to do.
