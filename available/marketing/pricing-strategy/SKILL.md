---
name: pricing-strategy
description: Pricing strategy for SaaS products and dev studio services. Use when asked to design pricing tiers, set rates, evaluate freemium vs paid, create packaging, or adapt pricing for LATAM markets. Triggers on "how should we price this", "pricing tiers", "freemium or paid", "what should we charge", "pricing page", "LATAM pricing", "consulting rates".
---

# Pricing Strategy

Skywalking operates in two pricing modes — (1) studio service pricing and (2) helping clients design SaaS pricing. LATAM purchasing power, USD/local currency dynamics, and B2B trust-building shape what works.

## Before Designing

1. **What is being priced?** — service, SaaS subscription, one-time product, hybrid
2. **Who pays?** — founder, CTO, finance team, self-serve developer
3. **Value delivered** — measurable outcome (time saved, revenue, cost avoided)
4. **Competitive range** — what do alternatives cost?
5. **Geography** — Argentina, LATAM-wide, global?
6. **Stage** — pre-revenue, early customers, scaling?

## SaaS Pricing Models

**Per-seat:** Value scales with team. Risk: customers minimize seats.
**Usage-based:** Aligns cost with value. Risk: unpredictable revenue.
**Flat-rate:** Simple. Risk: leaves money on table at top end.
**Tiered (recommended):** Free → Pro → Business. Each tier unlocks value, not just limits.

Tier design:
- Free: genuinely useful, not enough for real business
- Mid: 70-80% of paying customers land here
- Top: annual contract, custom pricing

### Studio Service Pricing

**Project-based:** Fixed scope, fixed price. Client gets predictability.
**Retainer:** Monthly, defined outcomes. Preferred for ongoing work.
**Value-based:** Priced against business outcome. "We build the checkout that recovers $X/month" > "40 hours at $Y".

## LATAM Context

**USD vs. Local Currency:**
- Argentina: invoice in USD (standard B2B tech)
- Brazil: BRL-first for local SMBs
- Mexico/Colombia/Chile: USD OK for B2B; local for self-serve

**Purchasing Power Parity:**
- LATAM buyers: 30-60% lower WTP vs US for equivalent products
- Regional pricing (geo-IP discount) is standard and expected
- Frame as "local pricing" not "discount"

**Price Points (LATAM B2B):**
- Entry: $29-49/mo
- Mid: $99-199/mo
- High: $299-499/mo
- Enterprise: custom, annual

## Packaging Principles

- Name tiers after stages: "Starter", "Team", "Scale" > "Basic", "Pro"
- Lead with outcomes, not features
- Annual: 2 months free > X% off (psychologically stronger)
- Show most expensive first (anchoring)
- Highlight recommended plan visually

## Common Mistakes

- Underpricing from imposter syndrome (LATAM studios price 40-60% below market)
- Too many tiers (2-3 optimal)
- Cost-based pricing instead of value-based
- No annual option (2-3x higher churn on monthly-only)
- Free tier that cannibalizes paid

## Output Format

```
## Pricing: [Product/Service]

**Model:** [subscription/project/retainer/value-based]
**Reasoning:** [1-2 sentences]

---

| Tier | Price | For | Key unlock |
|------|-------|-----|------------|
| [name] | $X/mo | [who] | [what] |

### LATAM Adaptation
- Argentina: [approach]
- Broader LATAM: [PPP notes]

### Upgrade Triggers
- [A → B]: [what forces upgrade]

### Pricing Page
- Recommended: [tier, why]
- CTA: [text per tier]

---

**Test:** [pricing experiment]
**Risk:** [what could go wrong]
```
