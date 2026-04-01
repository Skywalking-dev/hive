---
name: technical-drawing
description: Generate technical construction drawings (floor plans, elevations, sections) as ISO-standard SVG/HTML sheets. Use when creating architectural plans, construction documentation, or any dimensioned technical drawing for EterHabitats or other construction projects.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Technical Drawing

Generate professional technical construction drawings as SVG embedded in HTML. Output follows ISO 5457 (sheets), ISO 128 (line types/weights), ISO 7200 (title block). Saves to project `docs/planos/` and auto-opens in browser.

## When to Use

- Floor plans (plantas)
- Elevations (elevaciones)
- Sections/cuts (cortes)
- Construction details
- Any dimensioned architectural drawing

## Drawing Types

| Type | Spanish | View | Typical Scale |
|------|---------|------|---------------|
| Floor plan | Planta | Top-down | 1:50, 1:100 |
| Elevation | Elevación | Front/side | 1:50, 1:100 |
| Section | Corte | Cut-through | 1:50 |
| Detail | Detalle | Zoomed area | 1:20, 1:10 |

## Sheet Structure

```
┌─────────────────────────────────────────────────┐
│ [20mm]        DRAWING AREA              [10mm]  │
│       ┌─────────────────────────────┐           │
│[10mm] │                             │ [10mm]    │
│       │   TECHNICAL DRAWING         │           │
│       │   (scale 1.30 recommended)  │           │
│       │                             │           │
│       │   SCALE BAR    NORTH        │           │
│       │   NOTES                     │           │
│       ├─────────────────────────────┤           │
│       │ TITLE BLOCK (ISO 7200)      │           │
│[10mm] └─────────────────────────────┘           │
└─────────────────────────────────────────────────┘
```

## Design System

### Page

```css
body {
  background: #0f1117;           /* dark surround */
  font-family: 'Inter', system-ui, sans-serif;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.drawing-board {
  max-width: 1340px;
  aspect-ratio: 420 / 297;       /* A3 landscape */
  background: /* grid + white */
    linear-gradient(rgba(160,175,200,0.10) 1px, transparent 1px),
    linear-gradient(90deg, rgba(160,175,200,0.10) 1px, transparent 1px),
    linear-gradient(rgba(160,175,200,0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(160,175,200,0.04) 1px, transparent 1px),
    #ffffff;
  background-size: 72px 72px, 72px 72px, 14.4px 14.4px, 14.4px 14.4px;
  border-radius: 3px;
  box-shadow: 0 4px 60px rgba(0,0,0,0.5);
}
```

### Colors

| Element | Color | Use |
|---------|-------|-----|
| Walls / structure | `#1a2744` | Dark navy blue — all structural lines |
| Dimension lines (cotas) — primary | `#1a2744` | Total dimensions, zones |
| Dimension lines (cotas) — openings | `#c0392b` | Red — window/door/opening dimensions |
| Reference lines | `#1a2744` opacity 0.2 | Dashed extension lines |
| Zone fill — taller/work | `#e8f0e8` opacity 0.12 | Subtle green tint |
| Zone fill — lab/secondary | `#f0ebe0` opacity 0.12 | Subtle warm tint |
| Container body fill | `#f2f4f7` | Light gray background |
| Text labels | `#1a2744` various opacities | Consistent with lines |

### Line Weights (ISO 128)

| Weight | SVG stroke-width | Use |
|--------|-------------------|-----|
| Extra wide | 2.1 | Frame border, techo/suelo lines |
| Wide | 1.5 | Exterior walls, portón |
| Medium | 1.05 | Interior walls, windows, doors |
| Thin | 0.5-0.6 | Dimension lines (cotas) |
| Narrow | 0.2-0.3 | Reference/extension lines, hatching |

### Line Types

```
Continuous ─────────   Visible edges, walls
Dashed - - - - -       Hidden elements, reference lines (stroke-dasharray="2,3")
Dot-dash —·—·—         Axes, partition walls (stroke-dasharray="8,3,2,3")
```

## Dimension System (Cotas)

### Indicators

- **Primary cotas:** Architectural tick (diagonal 45°, red `#c0392b`)
- **Secondary cotas:** Smaller tick or filled arrow
- **All text on white background** (`<rect>` behind `<text>` for legibility)

### Tick Markers (SVG defs)

```xml
<!-- Primary tick -->
<marker id="tick" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
  <line x1="0" y1="8" x2="8" y2="0" stroke="#c0392b" stroke-width="1.2"/>
</marker>

<!-- Secondary tick -->
<marker id="tick2" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
  <line x1="0" y1="6" x2="6" y2="0" stroke="#c0392b" stroke-width="0.9"/>
</marker>

<!-- Filled arrows for small cotas -->
<marker id="al" markerWidth="6" markerHeight="6" refX="6" refY="3" orient="auto">
  <path d="M6,0 L0,3 L6,6" fill="#c0392b" stroke="none"/>
</marker>
```

### Horizontal Cotas (3 levels below drawing)

```
L1 (closest): Individual openings — red, tick2 markers
L2 (middle):  Zone parciales — navy, tick markers
L3 (farthest): Total exterior — navy, tick markers, bold text
```

### Vertical Cotas — Use Level Marks

Instead of stacked dimension lines, use **level marks** (marcas de nivel):

```xml
<!-- Level mark: triangle + boxed value -->
<g transform="translate(-82, {y_position})">
  <polygon points="0,0 6,-4 6,4" fill="#1a2744"/>
  <rect x="7" y="-6" width="28" height="12" fill="#ffffff" rx="1" stroke="#1a2744" stroke-width="0.3"/>
  <text x="21" y="3" text-anchor="middle" font-size="8" fill="#1a2744" font-weight="700">+0.00</text>
</g>
```

Level marks are cleaner than stacked dimension lines. Use red (`#c0392b`) for opening levels, navy for structural levels.

### Text Behind White Background

Every dimension text MUST have a white rect behind it:

```xml
<rect x="{text_x - 14}" y="{text_y - 8}" width="28" height="10" fill="#ffffff" rx="1"/>
<text x="{text_x}" y="{text_y}" text-anchor="middle" font-size="9" fill="#c0392b" font-weight="600">1.80</text>
```

## Title Block (ISO 7200)

Position: bottom-right corner of frame. 510u × 165u.

| Row | Fields |
|-----|--------|
| 1 | Company name + location |
| 2 | Drawing title + subtitle |
| 3 | Escala · Fecha · Dibujó · Aprobó |
| 4 | N° Plano · Revisión · Formato · Hoja |

### Naming Convention

```
{PROJECT}-{DISCIPLINE}-{NUMBER}

ET-ARQ-001    EterHabitats, Arquitectura, Planta
ET-ARQ-002    EterHabitats, Arquitectura, Elevación
ET-EST-001    EterHabitats, Estructura, Detalle
```

## Scale Bar

Always include. Alternating black/white segments, 5m total at 1:50.

```xml
<g transform="translate(x, y)">
  <text x="0" y="-6" font-size="7" fill="#1a2744" opacity="0.5">ESCALA 1:50</text>
  <!-- 1m = 60u at 1:50 -->
  <rect x="0" y="0" width="60" height="4" fill="#1a2744"/>
  <rect x="60" y="0" width="60" height="4" fill="none" stroke="#1a2744" stroke-width="0.4"/>
  <!-- ... repeat ... -->
  <text x="0" y="12" text-anchor="middle" font-size="5.5" fill="#1a2744">0</text>
  <text x="300" y="12" text-anchor="middle" font-size="5.5" fill="#1a2744">5m</text>
</g>
```

## SVG Coordinate System

```
viewBox: "0 0 1260 891" (A3 proportions × 3 for resolution)
1 SVG unit ≈ 0.333mm paper

Frame: x=60 y=30 → x=1230 y=861 (margins: 20mm left, 10mm others)
Title block: translate(720, 696)

Drawing group: translate + scale(1.30) for comfortable viewing
Scale factor at 1:50: 1m real = 60 SVG units
```

## Print Support

```css
@media print {
  body { background: white; padding: 0; }
  .drawing-board {
    box-shadow: none; border-radius: 0;
    max-width: none; width: 420mm; height: 297mm;
  }
  @page { size: A3 landscape; margin: 0; }
}
```

## Implementation Steps

1. Read project specs (dimensions, materials, openings)
2. Calculate SVG coordinates: `dimension_m × 60 = SVG units`
3. Build SVG with frame → title block → drawing group → cotas → scale bar → notes
4. Apply `scale(1.30)` to drawing group for comfortable size
5. Write to `{project}/docs/planos/{name}.html`
6. Open with `open {path}`

## Conventions

- All measurements in **meters** (display without "m" suffix in cotas, with suffix in notes)
- Openings identified as **V-01** (ventana), **D-01** (puerta), **P-01** (portón)
- Zones labeled in uppercase, low opacity, inside the drawing
- North arrow always present
- Notes section below drawing, numbered list
- Spanish neutral LATAM for all text

## Reference Implementation

- Floor plan: `projects/eterhabitats/docs/planos/container-planta.html`
- Elevation: `projects/eterhabitats/docs/planos/container-elevacion.html`

## Anti-patterns

- NO rotated text on vertical dimensions — use level marks instead
- NO overlapping dimension lines — separate into clear levels
- NO dimension text without white background
- NO colored fills on structural elements — navy lines on white only
- NO multiple accent colors — navy for structure, red for opening cotas only
- NO AI-slop gradients or decorative elements
