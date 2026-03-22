Es un registry de Vercel (open source via vercel-labs/skills) donde se   instalan skills con npx skills add <repo>. Básicamente son archivos      markdown que inyectan conocimiento procedimental a agentes AI (Claude    Code, Cursor, Copilot, etc). Son exactamente lo mismo que nuestros       skills en hive/skills/, pero con distribución pública.
                   Lo relevante para nosotros (por stack)
                                   Alta prioridad — instalar ya:
                                            Skill: supabase-postgres-best-practices                                  Repo: supabase/agent-skills                                              Por qué: 39K installs. Best practices oficiales para Kokoro              ────────────────────────────────────────                                 Skill: vercel-react-best-practices                                       Repo: vercel-labs/agent-skills                                           Por qué: 225K installs. React patterns para Pixel                        ────────────────────────────────────────                                 Skill: web-design-guidelines                                             Repo: vercel-labs/agent-skills                                           Por qué: 179K installs. Design guidelines para Aurora/Pixel              ────────────────────────────────────────                                 Skill: vercel-composition-patterns                                       Repo: vercel-labs/agent-skills                                           Por qué: 91K. Composition patterns Next.js                               ────────────────────────────────────────                                 Skill: stripe-best-practices                                             Repo: stripe/ai                                                          Por qué: Para Natu, Miicel (payments)                                    ────────────────────────────────────────                                 Skill: n8n-conventions                                                   Repo: n8n-io/n8n                                                         Por qué: Convenciones oficiales para Flux
                                Media prioridad — evaluar:
                                               Skill: seo-audit                                                         Repo: coreyhaines31/marketingskills                                      Por qué: 47K. Complemento para Lumen                                     ────────────────────────────────────────                                 Skill: programmatic-seo                                                  Repo: coreyhaines31/marketingskills                                      Por qué: 26K. SEO programático                                           ────────────────────────────────────────                                 Skill: content-strategy + copywriting                                    Repo: coreyhaines31/marketingskills                                      Por qué: Para Pregon                                                     ────────────────────────────────────────                                 Skill: systematic-debugging                                              Repo: obra/superpowers
  Por qué: 34K. Debugging metódico                                         ────────────────────────────────────────                                 Skill: subagent-driven-development                                       Repo: obra/superpowers                                                   Por qué: 22K. Orquestación multi-agente (lo que hacemos con Mentat)      ────────────────────────────────────────                                 Skill: dispatching-parallel-agents                                       Repo: obra/superpowers  Por qué: 19K. Paralelismo de agentes

  Interesante pero secundario:

  ┌─────────────────┬──────────────────────────────┬─────────────────┐     │      Skill      │             Repo             │      Nota       │
  ├─────────────────┼──────────────────────────────┼─────────────────┤
  │ mcp-builder     │ anthropics/skills            │ 23K. Para       │
  │                 │                              │ construir MCPs  │     ├─────────────────┼──────────────────────────────┼─────────────────┤
  │ brand-guideline │                              │ 15K.            │
  │ s               │ anthropics/skills            │ Complemento a P │
  │                 │                              │ RODUCT_IDENTITY │
  ├─────────────────┼──────────────────────────────┼─────────────────┤
  │                 │ coreyhaines31/marketingskill │ 20K. Structured │
  │ schema-markup   │ s                            │  data para      │
  │                 │                              │ Lumen           │
  ├─────────────────┼──────────────────────────────┼─────────────────┤
  │ page-cro +      │ coreyhaines31/marketingskill │ CRO para        │
  │ signup-flow-cro │ s                            │ landings        │
  └─────────────────┴──────────────────────────────┴─────────────────┘

  Observación clave

  Nuestro sistema de skills (hive/skills/) es compatible en concepto pero
   no en formato. skills.sh usa un formato estándar distribuible via npm.
   Dos caminos posibles:

  1. Consumir — instalar skills relevantes con npx skills add y que
  convivan con los nuestros
  2. Publicar — adaptar nuestros skills (n8n-*, process_video, etc.) al
  formato skills.sh y publicarlos. Algunos como n8n-code-javascript o
  process_video no tienen equivalente en el registry y podrían tener
  tracción.

  Recomendación

  Quick win: instalar los 6 de alta prioridad y ver cómo se integran con
  nuestro setup. Son markdown puro, sin riesgo.

  Balanced: además, evaluar publicar 2-3 skills nuestros como test de
  distribución (buen branding para Skywalking).