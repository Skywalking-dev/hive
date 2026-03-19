# Hive en skywalking.dev — Landing Page & Presentación

> **Fecha:** 2026-03-17 | **Participantes:** Aurora, Pregon | **Repo:** github.com/Skywalking-dev/hive

## Decisiones necesarias

1. Estructura de la landing page (secciones, orden)
2. Diseño visual y estilo (hero, colores, tipografía)
3. CTAs y flujo de conversión
4. Contenido principal (copy, messaging)
5. Conexión con lead generation
6. Ubicación en la web (path, navegación)

---

## Propuestas

### Aurora

| Decisión | Propuesta | Justificación |
|---|---|---|
| Estructura | Hero → Demo GIF → Skills grid → Agents showcase → Install → CTA | Muestra valor en 5 segundos, profundiza después |
| Diseño hero | Terminal dark con slash commands animados, fondo `#0D1117` | El producto es CLI-first, el hero debe reflejarlo |
| Paleta | `#0D1117` bg, `#58A6FF` links, `#7EE787` success, `#F0F6FC` text | GitHub-native feel, familiar para devs |
| Tipografía | JetBrains Mono para código, Inter para copy | Estándar dev tooling, alta legibilidad |
| Skills grid | Cards con icon + nombre + 1 línea, agrupados por categoría | Scannable, el dev encuentra su stack en 3 seg |
| Agents | Carousel horizontal con avatar + nombre + focus, click expande | No ocupa espacio vertical, invita exploración |

**Necesito de otros:** Copy del hero y CTAs de Pregon
**Conflicto que veo:** ninguno

### Pregon

| Decisión | Propuesta | Justificación |
|---|---|---|
| Hero copy | "Give your AI assistant superpowers." + "40+ skills. 9 agents. One plugin." | Directo, cuantificable, sin buzzwords |
| CTA primario | "View on GitHub" (botón) + star count badge | Devs quieren ver código, no landing pages |
| CTA secundario | "Want this for your team? Book a call" → Calendly con UTM | Convierte enterprise sin espantar OSS crowd |
| Path | `skywalking.dev/hive` | SEO-friendly, memorable, linkeable desde README |
| Navegación | Item "Open Source" en nav principal → dropdown con Hive | Señala identidad OSS de Skywalking |
| Lead gen flow | GitHub → README link → /hive → Calendly (`utm_source=hive`) | Attribution clara, funnel medible |
| Social proof | GitHub stars badge + "Used in production at Skywalking" | Credibilidad sin inventar testimonials |

**Necesito de otros:** Hero visual y skill cards de Aurora
**Conflicto que veo:** ninguno

---

## Conflictos

Ninguno. Las propuestas son complementarias.

---

## Decisiones finales

| # | Decisión | Resolución | Owner |
|---|---|---|---|
| 1 | Estructura | Hero (terminal animado + copy) → Demo GIF → Skills grid → Agents carousel → Quick Start → CTAs | Pixel |
| 2 | Diseño | Dark terminal hero `#0D1117`, JetBrains Mono + Inter, paleta GitHub-native | Aurora → Pixel |
| 3 | CTAs | Primario: "View on GitHub" con stars badge. Secundario: "Book a call" → Calendly `?utm_source=github&utm_medium=hive&utm_campaign=oss-launch` | Pregon |
| 4 | Copy | Hero: "Give your AI assistant superpowers." Sub: "40+ skills. 9 agents. One plugin." | Pregon |
| 5 | Lead gen | README → skywalking.dev/hive → Calendly. UTM en todos los links. | Pregon |
| 6 | Path | `skywalking.dev/hive`, nav item "Open Source" | Pixel |

## Timeline

| Día | Entregable | Owner | Depende de |
|---|---|---|---|
| D+0 | Specs de diseño (Figma o doc) | Aurora | — |
| D+1 | Copy final (hero, secciones, CTAs) | Pregon | Aurora specs |
| D+2 | Implementación landing page | Pixel | Aurora + Pregon |
| D+3 | SEO meta tags + schema markup | Lumen | Pixel deploy |
| D+3 | Calendly setup + UTM config | Pregon | — |

## Pendientes (usuario)

- Confirmar path `skywalking.dev/hive` o preferís otro
- Calendly link para el CTA de enterprise
- Querés mostrar el demo GIF en el hero o un terminal estático con commands?
