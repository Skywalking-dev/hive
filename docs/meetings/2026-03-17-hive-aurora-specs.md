# Hive Landing Page — Design Specifications
> **Date:** 2026-03-17 | **For:** Pixel (Frontend) + Sentinela (QA)
> **Path:** `skywalking.dev/hive`

---

## Context
- **Product:** Hive — Claude Code plugin (40+ skills, 9 agents, open source)
- **Promise:** "Give your AI assistant superpowers."
- **KPI:** Drive GitHub stars, convert enterprise via Calendly (UTM attribution)
- **Palette:** GitHub-native dark terminal theme (`#0D1117` + `#58A6FF` + `#7EE787` + `#F0F6FC`)
- **Typography:** JetBrains Mono (code), Inter (body)
- **Grid:** 8px base spacing

---

## Design Tokens

### Colors
| Token | Hex | WCAG AA | Usage |
|-------|-----|---------|-------|
| `--hive-bg-primary` | `#0D1117` | — | Hero + main bg (dark terminal) |
| `--hive-bg-surface` | `#161B22` | — | Card/panel bg (slightly elevated) |
| `--hive-bg-hover` | `#21262D` | — | Hover state bg |
| `--hive-text-primary` | `#F0F6FC` | 13.5:1 | Body text, high contrast |
| `--hive-text-secondary` | `#8B949E` | 7.2:1 | Secondary text, muted copy |
| `--hive-accent-blue` | `#58A6FF` | 6.1:1 | Links, highlights, CTA hover |
| `--hive-accent-green` | `#7EE787` | 4.9:1 | Success states, badges (secondary) |
| `--hive-accent-orange` | `#FB8500` | 5.8:1 | Warnings, hover accents (if needed) |
| `--hive-border` | `#30363D` | — | Subtle borders, dividers |

**Rationale:** All colors derived from GitHub's native dark theme. Developers recognize this immediately. No custom palette needed.

### Typography
| Role | Font | Weight | Size | Line Height | Letter Space |
|------|------|--------|------|-------------|--------------|
| Display | JetBrains Mono | 700 | 48px | 1.1 (52px) | -0.01em |
| H1 | JetBrains Mono | 600 | 36px | 1.2 (43px) | -0.01em |
| H2 | JetBrains Mono | 600 | 28px | 1.3 (36px) | 0 |
| H3 | Inter | 600 | 22px | 1.4 (30px) | 0 |
| Body | Inter | 400 | 16px | 1.5 (24px) | 0 |
| Body Small | Inter | 400 | 14px | 1.5 (21px) | 0 |
| Meta | Inter | 500 | 12px | 1.4 (16px) | 0.02em |
| Code | JetBrains Mono | 400 | 14px | 1.6 (22px) | 0 |

**Rationale:** JetBrains Mono for display + headlines creates "code-first" feel (monospace = terminal authority). Inter for body ensures readability at smaller sizes without terminal aesthetic fatigue.

### Spacing
| Scale | Value | Usage |
|-------|-------|-------|
| xs | 4px | Badge padding, micro gaps |
| sm | 8px | Button padding h, input padding |
| md | 16px | Card padding, component gaps |
| lg | 24px | Section padding, comfortable breathing |
| xl | 32px | Between major sections |
| 2xl | 48px | Section separation |
| 3xl | 64px | Page-level gaps |

**Grid:** All values multiples of 8px. Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl).

---

## Component Specs

### 1. Hero Section

**Layout:**
```
┌─────────────────────────────┐
│     Hive Logo (nav)         │
├─────────────────────────────┤
│                             │
│  Terminal Animation Area    │
│  (CSS gradient + blink fx)  │
│                             │
│  "Give your AI assistant"   │
│   "superpowers."            │
│                             │
│  "40+ skills. 9 agents."    │
│  "One plugin."              │
│                             │
│  [View on GitHub] [Demo]    │
│                             │
└─────────────────────────────┘
```

**Dimensions:**
- **Full viewport height:** `min-height: 100vh`
- **Max width container:** 1280px (lg breakpoint)
- **Padding:** 64px top/bottom (3xl), 24px left/right (lg)

**Terminal Animation:**
- **Height:** 240px
- **Border:** 1px `--hive-border`, `border-radius: 8px`
- **Background:** `--hive-bg-surface`
- **Content:** Animated slash command prompts (e.g., `/shape`, `/dev`, `/ship_it`) appearing one per 800ms
- **Animation:** Typewriter effect (CSS `animation: type 0.6s steps(30, end)`)
- **Cursor:** Blinking green (`--hive-accent-green`) pipe character `|`
- **Text color:** `--hive-text-primary`
- **Font:** JetBrains Mono 14px

**Headline:**
- **Primary:** "Give your AI assistant superpowers."
  - Font: JetBrains Mono 48px/700, `--hive-text-primary`
  - Margin top: 32px (xl)
  - Line height: 1.1 (52px)
- **Secondary:** "40+ skills. 9 agents. One plugin."
  - Font: Inter 16px/400, `--hive-text-secondary`
  - Margin top: 16px (md)

**CTA Buttons (Row):**
- Layout: `flex gap-16` (md)
- **Primary:** "View on GitHub"
  - Padding: 12px 24px (sm md)
  - Background: transparent, border 2px `--hive-accent-blue`
  - Color: `--hive-accent-blue`
  - Hover: background `--hive-bg-hover`, color `--hive-accent-blue`
  - Border radius: 6px
  - Font: Inter 16px/600
  - Transition: 150ms ease-out
  - **Badge right:** GitHub stars (small, inline)
- **Secondary:** "Book a demo"
  - Padding: 12px 24px
  - Background: `--hive-accent-blue` 20% opacity, border 1px `--hive-accent-blue`
  - Color: `--hive-accent-blue`
  - Hover: background `--hive-accent-blue` 30% opacity
  - Font: Inter 16px/600
  - Transition: 150ms ease-out

**Responsive:**
- **mobile (<640px):** Stack buttons vertically, terminal height 180px, display 36px
- **tablet (640-768px):** Display 40px, buttons side-by-side
- **desktop (>768px):** Display 48px, full layout

**Accessibility:**
- Focus ring: 2px `--hive-accent-blue` with 2px offset (WCAG AA)
- Alt text on logo
- Semantic HTML: `<h1>` for primary headline

**Test IDs:**
```
data-testid="hero-container"
data-testid="hero-terminal"
data-testid="hero-headline-primary"
data-testid="hero-headline-secondary"
data-testid="cta-github"
data-testid="cta-demo"
data-testid="github-stars-badge"
```

---

### 2. Demo Section (Optional, Post-Hero)

**Layout:** Centered GIF/video player
- **Width:** 100% max 960px
- **Aspect ratio:** 16:9
- **Margin:** 48px (2xl) top/bottom
- **Border:** 1px `--hive-border`, radius 8px
- **Autoplay:** disabled, play button overlay

**Copy above:**
- **Headline:** "See it in action"
  - Font: Inter 22px/600, `--hive-text-primary`
  - Margin bottom: 16px (md)

---

### 3. Skills Grid

**Layout:**
- Container max-width: 1280px, padding 24px (lg)
- Grid: `grid-auto-flow: row, grid-template-columns: repeat(auto-fit, minmax(240px, 1fr))`
- Gap: 16px (md)
- Grouping: Section headers above each category (e.g., "AI Systems", "Development", "Automation")

**Card Spec:**
```
┌──────────────────────┐
│ [Icon]               │
│ Skill Name           │
│ One-liner desc.      │
└──────────────────────┘
```

**Dimensions:**
- **Width:** Auto (grid responsive), min 240px
- **Height:** auto, content-fit
- **Padding:** 16px (md) internal

**Style:**
- **Background:** `--hive-bg-surface`
- **Border:** 1px `--hive-border`, radius 8px
- **Hover:** Background `--hive-bg-hover`, border `--hive-accent-blue` 50%, transition 150ms
- **Shadow:** None (flat design per identity)

**Content:**
- **Icon:** 32x32px SVG, `--hive-text-primary`
- **Name:** Inter 16px/600, `--hive-text-primary`
- **Description:** Inter 14px/400, `--hive-text-secondary`, max 100 chars
- **Margin:** Icon-to-name 8px (sm), name-to-desc 8px (sm)

**Section Header (before each category):**
- Font: Inter 18px/600, `--hive-text-primary`
- Margin bottom: 16px (md), margin top: 32px (xl, except first)
- Color: `--hive-accent-blue`

**Grouping:** Determine 3-5 categories (e.g., AI, Development, Workflow, Testing, etc.). List all skill names explicitly in implementation doc.

**Responsive:**
- **mobile (<640px):** 2-column grid, minmax 120px
- **tablet (640px+):** 3-column grid, minmax 180px
- **desktop (1024px+):** 4-column grid, minmax 240px

**Accessibility:**
- Each card is a semantic button or link (`<button>` or `<a>`)
- Focus ring: 2px `--hive-accent-blue` offset 2px
- ARIA label per card

**Test IDs:**
```
data-testid="skills-section"
data-testid="skills-category-{category-name}"
data-testid="skill-card-{skill-name}"
data-testid="skill-icon-{skill-name}"
```

---

### 4. Agents Carousel

**Layout:** Horizontal scroll container
- **Container:** Full width, padding 24px (lg) top/bottom, overflow-x auto (hidden scrollbar)
- **Inner width:** max-content
- **Gap between cards:** 16px (md)

**Card Spec:**
```
┌─────────────────────┐
│   [Avatar Circle]   │
│   Agent Name        │
│   Focus Area        │
│   [→ Expand]        │
└─────────────────────┘
```

**Dimensions:**
- **Width:** 240px fixed
- **Height:** 200px fixed
- **Padding:** 16px (md)

**Style:**
- **Background:** `--hive-bg-surface`
- **Border:** 1px `--hive-border`, radius 8px
- **Hover:** Border `--hive-accent-blue`, bg `--hive-bg-hover`, transition 150ms

**Content:**
- **Avatar:** 64x64px circle (border-radius: 50%), SVG initials or icon, background `--hive-accent-blue` 20%, color `--hive-accent-blue`
- **Name:** Inter 16px/600, `--hive-text-primary`, margin-top 12px (sm)
- **Focus:** Inter 14px/400, `--hive-text-secondary`, margin-top 4px (xs)
- **Expand arrow:** `→` in `--hive-accent-blue`, right-aligned, margin-top auto

**Click/Expand Behavior:**
- Click card → modal or expanded panel appears
- Modal background: `--hive-bg-primary` with opacity overlay (70%)
- Modal content: Full agent bio (150 words max), skills list (3-5 bullets), link to agent profile
- Close: X button, escape key, click outside
- Animation: Fade in 200ms, scale from 0.95 to 1.0

**Carousel Navigation (optional):**
- If agents list >6 items: left/right chevron buttons at ends
- Chevrons: `--hive-text-secondary`, hover `--hive-accent-blue`, 150ms transition

**Agents List (9 total):**
1. Aurora — Product Designer
2. Pixel — Frontend Specialist
3. Kokoro — Backend Specialist
4. Sentinela — QA Expert
5. Hermes — Deployment Specialist
6. Flux — Automation Specialist
7. Oraculo — Research Specialist
8. Pregon — Marketing Specialist
9. Lumen — SEO Specialist

(Exact avatars/bios to be provided by Pregon or branded icons)

**Responsive:**
- **mobile (<640px):** Card width 180px, visible 1.5 cards
- **tablet (640px+):** Card width 200px, visible 2.5 cards
- **desktop (1024px+):** Card width 240px, visible 3-4 cards

**Accessibility:**
- Keyboard nav: arrow keys to scroll
- Tab through cards, arrow into modal
- ARIA labels per card
- Focus ring: 2px `--hive-accent-blue`

**Test IDs:**
```
data-testid="agents-carousel"
data-testid="agent-card-{agent-name}"
data-testid="agent-expand-modal"
data-testid="agent-modal-close"
```

---

### 5. Quick Start Section

**Layout:**
- Container: max-width 1280px, centered, padding 24px (lg)
- Margin top: 48px (2xl) from previous section

**Copy:**
- **Headline:** "Get started in 30 seconds"
  - Font: Inter 28px/600, `--hive-text-primary`
  - Margin bottom: 24px (lg)

**Code Block:**
```
┌──────────────────────────────┐
│ $ npm install hive-plugin    │
│ $ hive /shape --help         │
│                              │
│ → Ready to ship!             │
└──────────────────────────────┘
```

**Style:**
- **Background:** `--hive-bg-surface`
- **Border:** 1px `--hive-border`, radius 8px
- **Padding:** 16px (md)
- **Font:** JetBrains Mono 14px, `--hive-text-primary`
- **Prompt:** `$` in `--hive-text-secondary`, command in `--hive-text-primary`
- **Output:** `→` in `--hive-accent-green`, text in `--hive-text-secondary`
- **Copy button:** Top-right corner, icon + "Copy", hover `--hive-accent-blue`, 150ms transition

**Copy button on hover:**
- **Position:** absolute, top 8px right 8px
- **Padding:** 4px 8px (xs sm)
- **Background:** `--hive-bg-hover`
- **Border:** 1px `--hive-border`
- **Font:** Inter 12px/500
- **Radius:** 4px
- **Transition:** opacity 150ms (hidden by default, shown on hover)

**Responsive:**
- **mobile (<640px):** Font 12px, padding 12px
- **desktop (>768px):** Font 14px, padding 16px

**Accessibility:**
- Code block is not interactive (no zoom/select issues)
- Copy button: keyboard accessible, focus ring 2px `--hive-accent-blue`
- Alt text: "Installation command for Hive plugin"

**Test IDs:**
```
data-testid="quickstart-section"
data-testid="quickstart-codeblock"
data-testid="quickstart-copy-button"
```

---

### 6. Call-to-Action Section (Final)

**Layout:** Centered, minimal
- **Margin:** 48px (2xl) top, 32px (xl) bottom
- **Padding:** 32px (xl) horizontal

**Copy:**
- **Headline:** "Ready to supercharge your workflow?"
  - Font: Inter 24px/600, `--hive-text-primary`
  - Margin bottom: 16px (md)
- **Subheading:** "Join 100+ developers using Hive in production."
  - Font: Inter 16px/400, `--hive-text-secondary`
  - Margin bottom: 24px (lg)

**Buttons:**
- Layout: `flex gap-16 justify-center`, wrap on mobile
- **Primary:** "View on GitHub" (repeat, full star count badge)
  - Style: same as hero
- **Secondary:** "Book a call"
  - Style: same as hero
  - Link: `https://calendly.com/... ?utm_source=github&utm_medium=hive&utm_campaign=oss-launch`
  - Opens in new tab

**Responsive:**
- **mobile (<640px):** Stack vertically, full width buttons
- **desktop (>640px):** Side-by-side, auto width

**Test IDs:**
```
data-testid="final-cta-section"
data-testid="final-cta-github"
data-testid="final-cta-calendly"
```

---

## Page-Level Specs

### Navigation
- **Logo:** Hive + icon (left)
- **Items:** Home | Docs | Blog | Open Source (dropdown: Hive + others) | GitHub
- **Mobile:** Hamburger menu, drawer overlay
- **Sticky:** Yes, on scroll down, elevation shadow 2px
- **Background:** `--hive-bg-primary` with 95% opacity (slight blur on scroll)

**Test IDs:**
```
data-testid="nav-container"
data-testid="nav-open-source-dropdown"
data-testid="nav-hive-link"
```

### Footer
- **Background:** `--hive-bg-surface`
- **Padding:** 24px (lg)
- **Columns:** Company, Resources, Legal (3-col grid on desktop, stack on mobile)
- **Links:** Use `--hive-accent-blue` on hover
- **Copyright:** "© 2026 Skywalking. Licensed under MIT."
- **Social icons:** GitHub, Twitter, LinkedIn (SVG 16px, `--hive-text-secondary`, hover `--hive-accent-blue`)

**Test IDs:**
```
data-testid="footer-container"
data-testid="footer-social-github"
```

### Animations

| Element | Event | Duration | Easing | Effect |
|---------|-------|----------|--------|--------|
| Hero terminal | Page load | 600ms | steps(30) | Typewriter commands |
| Terminal cursor | Page load | 600ms-∞ | — | Blink `--hive-accent-green` |
| Skill cards | Scroll into view | 200ms | ease-out | Fade in + slide up (stagger 50ms) |
| Agent carousel cards | Hover | 150ms | ease-out | Border color, bg shift |
| CTA buttons | Hover | 150ms | ease-out | Background/border shift |
| Modal (agent expand) | Open | 200ms | ease-out | Fade in + scale (0.95→1.0) |
| Links | Hover | 150ms | ease-out | Color to `--hive-accent-blue` |

**CSS Motion:** Prefer `transition` + `transform` for performance. No animations on devices with `prefers-reduced-motion: reduce`.

---

## Responsive Breakpoints

| Breakpoint | Width | Key Changes |
|------------|-------|-------------|
| mobile | <640px | Display 36px, buttons stack, 2-col skills, single agent card |
| tablet | 640-1024px | Display 40px, buttons inline, 3-col skills, 2-3 agent cards |
| desktop | >1024px | Display 48px, all layouts full, 4-col skills, 3-4 agent cards |

---

## Accessibility Checklist

- **WCAG AA minimum:** All text has sufficient contrast (tested above)
- **Keyboard nav:** Tab through all interactive elements, Enter/Space to activate
- **Focus rings:** 2px `--hive-accent-blue`, 2px offset, visible at all times
- **Alt text:** All images, icons, badges have semantic labels
- **Semantic HTML:** `<h1>`, `<button>`, `<a>`, `<nav>`, `<footer>`
- **Motion:** Respect `prefers-reduced-motion`, disable animations for those users
- **Color alone:** Don't use color to convey status (pair with icon or text)
- **Form fields:** Labels, error states, success states clear

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page load time (CLS) | <2s | Vercel Analytics |
| GitHub CTR | >15% | UTM tracking |
| Calendly conversion (enterprise) | >5% | Calendly + UTM source |
| Mobile friendly | 100% | Lighthouse audit |
| Accessibility score | 95+ | Lighthouse a11y |

---

## Handoff Checklist for Pixel

- [ ] Implement hero with terminal animation (CSS typewriter + blink cursor)
- [ ] Build skills grid with responsive auto-fit layout, hover states
- [ ] Create agents carousel with horizontal scroll + modal expand behavior
- [ ] Style code block with copy button (hover reveal)
- [ ] Implement sticky nav with Open Source dropdown
- [ ] Add all `data-testid` attributes per spec
- [ ] Test responsive breakpoints (mobile/tablet/desktop)
- [ ] Verify WCAG AA contrast + keyboard nav
- [ ] Disable animations for `prefers-reduced-motion`
- [ ] Connect GitHub stars API endpoint (badge in hero + final CTA)
- [ ] Connect Calendly link with UTM params to both CTA sections

## QA Checklist for Sentinela

- [ ] Hero terminal animation plays on page load, commands appear at 800ms intervals
- [ ] CTA buttons navigate correctly (GitHub link, Calendly new tab)
- [ ] Skills cards render all 40+ items, hover states trigger
- [ ] Agent carousel scrolls horizontally, expand modal opens/closes
- [ ] All `data-testid` selectors found (no missing IDs)
- [ ] Focus ring visible on all buttons/links
- [ ] Keyboard nav: Tab through hero → skills → agents → CTAs
- [ ] Mobile layout: hero 36px, buttons stack, 2-col grid
- [ ] Tablet layout: hero 40px, buttons inline, 3-col grid
- [ ] Desktop layout: hero 48px, full spacing, 4-col grid
- [ ] Copy button in code block works, copies text to clipboard
- [ ] Calendly link opens in new tab, UTM params present
- [ ] GitHub stars badge updates (or hardcoded if API unavailable)
- [ ] No color-only status indicators (validate icons + text)
- [ ] Motion disabled for `prefers-reduced-motion: reduce` users
- [ ] LCP (Largest Contentful Paint) <2.5s, CLS <0.1

---

## Notes

- **No custom SVG illustrations:** Use icon library (e.g., Heroicons, Lucide) for skill cards + nav
- **GIF in demo section:** Pixel to source/record 30-60s plugin demo if approved
- **Calendly iframe vs. link:** Recommend link (cleaner, UTM friendly)
- **GitHub API stars:** Use GitHub REST API if available, else hardcode current count + refresh monthly

---

**Ready for Pixel. Questions? Slack #hive-landing.**
