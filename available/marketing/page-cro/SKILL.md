---
name: page-cro
description: Conversion rate optimization for web pages. Use when asked to audit, improve, or critique a landing page, hero section, pricing page, or any product page for a SaaS or dev tool. Triggers on "optimize this page", "why isn't this converting", "improve the CTA", "audit our landing page", "hero section feedback", "page isn't converting".
---

# Page CRO — Conversion Rate Optimization

Skywalking is a dev studio in Patagonia, Argentina. Visitors are developers and technical decision-makers — skeptical, fast to judge, allergic to marketing fluff.

## Before Analyzing

1. **Page URL or content** — screenshot, copy-paste, or live URL
2. **Primary goal** — what action should the visitor take?
3. **Traffic source** — cold ad traffic vs warm referral vs organic (changes behavior radically)
4. **Current conversion rate** — if known
5. **Audience** — developer? CTO? founder?

If any are missing, ask before auditing.

## Developer Psychology

- **Scan before read** — headline, subheading, CTA, then maybe the rest
- **Trust proof over claims** — numbers, code snippets, GitHub stars, real names beat adjectives
- **Hate being sold to** — conversational and direct > corporate speak
- **Self-qualify in 5 seconds** — "is this for me?" must be answerable immediately
- **Lighthouse score = trust signal** — slow pages signal poor engineering

## Audit Framework (highest impact first)

### 1. Hero Section
- **Headline clarity:** Explainable in 3 seconds?
- **Specificity:** "Deploy in 90 seconds" > "Save time"
- **CTA:** Verb-first, specific. "Start free" > "Get started"
- **Visual proof:** Product screenshot > illustration > abstract graphic
- **FCP:** >3s on mobile = conversion killer

### 2. Trust Signals
- Customer logos (recognizable to audience)
- Testimonials: name + title + company + specific result
- Numbers: users, uptime, performance metrics
- Place trust signals nearest to CTAs

### 3. CTA and Friction
- Primary CTA visible without scrolling
- Repeat at logical decision points
- Each extra form field cuts conversion ~10%
- State "no credit card required" explicitly

### 4. Features vs. Outcomes
- "Real-time sync" → "Your team always works on the same version"
- Include technical depth for developers — available even if not read now

### 5. Performance
- LCP, INP, CLS, TTFB
- Next-gen images, lazy loading, defer non-critical JS
- Each 100ms improvement = measurable conversion lift

## Output Format

```
## CRO Audit: [Page Name]

**Goal:** [primary action]
**Audience:** [who]
**Traffic source:** [cold/warm/organic]

---

### Critical Issues (fix first)
1. [Issue] — [fix] — [expected impact]

### High Impact (this week)
2. [Issue] — [fix]

### Quick Wins
3. [Issue] — [fix]

### Copy Rewrites
**Current:** "[original]"
**Suggested:** "[rewrite]"
**Why:** [1 sentence]

### Lighthouse Flags
- [metric]: [current] → target [X]

---

**Test to run:** [A/B recommendation]
**Measure:** [metric + timeframe]
```

## LATAM Notes

- WhatsApp CTA often outperforms email CTA — consider "Chat on WhatsApp" as secondary
- Regional client logos > global logos for local audiences
- Spanish pages: neutral ES-LATAM for broader reach
