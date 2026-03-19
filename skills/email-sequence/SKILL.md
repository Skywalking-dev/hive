---
name: email-sequence
description: Design email sequences for lead nurturing, onboarding, and re-engagement. Use when asked to create a welcome sequence, onboarding drip, re-engagement campaign, or any multi-email nurture flow. Triggers on "email sequence", "welcome emails", "onboarding drip", "nurture campaign", "follow-up sequence", "re-engagement emails", "email automation".
---

# Email Sequence Design

Skywalking builds sequences for (1) our studio pipeline and (2) clients' SaaS products. Developer-friendly tone default. No salesy language. No fake urgency.

Stack: Resend (JSX templates) + n8n for triggers. Drafts go to Gmail handler for review.

## Before Writing

1. **Trigger** — what starts this? (form submit, trial signup, demo booked, inactivity)
2. **Goal** — what should subscriber do by the end?
3. **Audience** — developer, founder, CTO?
4. **Product/service context** — what does it do?
5. **Warm or cold?** — what does subscriber already know?

## Sequence Architecture

**Trigger → Email chain → Goal**

- How many emails, time gaps between sends
- Exit condition (goal achieved = stop)
- Fallback if no engagement (re-engagement or suppress)

Standard lengths:
- Welcome/onboarding: 4-6 emails over 14 days
- Lead nurture: 5 emails over 3 weeks
- Re-engagement: 3 emails over 7 days, then suppress

## Writing Rules for Developers

- **Plain text preferred** — feels like a conversation, not a newsletter
- **Short subjects** — under 45 chars. Specific > clever.
- **No fake personalization** — "Hey {name}, I was thinking about you" when automated = trust killer
- **Lead with utility** — first line delivers value. No "I hope this finds you well."
- **One CTA per email** — multiple = none
- **Respect unsubscribe** — visible, one-click, no guilt
- **No fake urgency** — "expires in 24h" when it doesn't = spam folder

## Sequence Templates

### Welcome (SaaS trial)
```
1. Immediate: "You're in. Here's what to do first." → single activation action
2. Day 2: One feature they haven't found → screenshot/code proof
3. Day 5: Social proof from similar user → real metric
4. Day 10: Address #1 upgrade objection → evidence
5. Day 14: Trial ending → what they lose vs keep
```

### Lead Nurture (studio inquiry)
```
1. Immediate: Confirm receipt + set expectations → book call CTA
2. Day 3: Relevant case study → real numbers
3. Day 7: Educational content, no pitch → reply CTA
4. Day 14: Social proof + recheck → still evaluating?
5. Day 21: Close loop, no pressure → door stays open
```

### Re-engagement (inactive)
```
1. Day 0: "Still there?" → what changed?
2. Day 3: New value they missed → try this one thing
3. Day 7: Graceful exit → stay or unsubscribe
→ Suppress after no action
```

## Output Format

```
## Sequence: [Name]

**Trigger:** [event]
**Goal:** [action]
**Audience:** [who]
**Length:** [N emails over X days]
**Exit:** [what stops it early]

---

| # | Timing | Subject | CTA | Micro-goal |
|---|--------|---------|-----|------------|
| 1 | Immediate | [subject] | [CTA] | [goal] |

---

### Email [N]

**Send:** Day X
**Subject:** [under 45 chars]

[Body — plain, conversational]

**CTA:** [link text]

---

**n8n notes:**
- Trigger: [form / webhook / Supabase event]
- Exit: [tag / event]
- Branch if goal achieved: [stop]

**Metric:** [open rate / click / conversion target]
```

## Compliance

- [ ] Unsubscribe in every email
- [ ] Physical address in footer (Ley 25.326)
- [ ] Opt-in lists only
- [ ] WhatsApp: Meta-approved templates only
- [ ] Suppression honored immediately
