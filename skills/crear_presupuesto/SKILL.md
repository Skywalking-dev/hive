# Skill: Create Presupuesto

**Propósito:** Generar presupuestos profesionales para proyectos de automatización con IA

**Tiempo estimado:** 15-20 minutos
**ROI:** ⭐⭐⭐⭐⭐

---

## Input Requerido

Solicita al usuario la siguiente información (haz preguntas específicas si falta algo):

### 1. Información del Cliente
- Nombre del cliente/empresa
- Industria/sector
- Tamaño (empleados, volumen de operación)
- Punto de dolor específico

### 2. Información del Proyecto
- Título del proyecto
- Problema a resolver (descripción breve)
- Solución propuesta (tecnología/enfoque)
- Alcance (Fase 1, Fase 2, etc.)
- Timeline de implementación

### 3. Costos
- Setup inicial (USD)
- Mantenimiento mensual (USD)
- Costos adicionales (si aplica)

### 4. Información de Contacto
- Nombre: Gonzalo Parra
- Teléfono: +54 11 2162 5416
- Email: info@skywalking.com
- Website: www.skywalking.dev

---

## Output: Estructura del Presupuesto

Genera un archivo markdown siguiendo esta estructura:

```markdown
---
titulo: "[Título del Proyecto]"
cliente: "[Nombre Cliente]"
fecha: "[YYYY-MM-DD]" (usar fecha actual)
total: "USD [setup] + USD [mensual]/mes"
contacto: "Gonzalo Parra · +54 11 2162 5416 · info@skywalking.com"
---

## El Desafío

[Descripción del contexto del cliente: industria, tamaño, volumen de operación]

**El problema principal:** [Descripción del punto de dolor sin mencionar personas específicas ni métricas exactas]

**Resultado:** [Consecuencias del problema: tiempo perdido, frustraciones, pérdidas]

---

## La Solución: [Nombre de la Solución]

[Descripción de alto nivel de la solución y su valor]

**Cómo funciona:**

1. [Paso 1]
2. [Paso 2]
3. [Paso 3]
4. [Paso 4]
5. [Paso 5]
6. [Paso 6]

---

## Beneficios Medibles

- **[Beneficio 1]:** [Descripción]
- **[Beneficio 2]:** [Descripción]
- **[Beneficio 3]:** [Descripción]
- **[Beneficio 4]:** [Descripción]
- **[Beneficio 5]:** [Descripción]

---

## Qué Incluye (Fase 1)

### [Subsección 1]

- [Item 1]
- [Item 2]
- [Item 3]

### [Subsección 2]

- [Item 1]
- [Item 2]
- [Item 3]

### Integraciones Core

- [Integración 1]
- [Integración 2]
- [Integración 3]

### Funcionalidades

- [Funcionalidad 1]
- [Funcionalidad 2]
- [Funcionalidad 3]

---

## Implementación ([X] semanas)

### Semanas 1-[Y]: [Fase 1]

- [Tarea 1]
- [Tarea 2]
- [Tarea 3]

### Semanas [Y+1]-[X]: [Fase 2]

- [Tarea 1]
- [Tarea 2]
- [Tarea 3]

---

## Inversión y ROI

### Setup Inicial (Único)

**USD [monto]**

Incluye:

- [Item 1]
- [Item 2]
- [Item 3]

### Mantenimiento Mensual

**USD [monto]/mes**

Incluye:

- [Item 1]
- [Item 2]
- [Item 3]

### Costos Adicionales (Cliente)

- [Costo 1]: USD [monto]/mes (si aplica)
- [Costo 2]: [Descripción con límites gratuitos si aplica]

### ROI Estimado

- [Beneficio cuantificable 1]
- [Beneficio cuantificable 2]
- **Break-even estimado: [X-Y] meses**

---

## Próximos Pasos

### 1. Call de validación (30 min)

- [Punto 1 a validar]
- [Punto 2 a validar]
- [Punto 3 a validar]

### 2. Firma de propuesta

- 50% adelanto (USD [monto])
- Inicio de desarrollo

### 3. Kickoff técnico (Semana 1)

- [Actividad 1]
- [Actividad 2]
```

---

## Pasos de Ejecución

1. **Recopilar información:** Haz preguntas al usuario para obtener todos los datos necesarios
2. **Generar contenido:** Crea el archivo markdown en `public/presupuestos/[slug].md`
3. **Verificar ruta:** El slug debe ser lowercase con guiones (ej: `clinica-san-martin.md`)
4. **Validar metadata:** Asegurar que el frontmatter esté completo y bien formateado
5. **Confirmar con usuario:** Mostrar un resumen y pedir confirmación antes de guardar

---

## Principios de Redacción

### ✅ HACER:
- Usar lenguaje claro y directo
- Enfocarse en el valor de negocio, no en tecnología
- Generalizar problemas (evitar mencionar personas/roles específicos)
- Evitar métricas demasiado específicas que no se puedan validar
- Usar "Fase 1", "Fase 2" en lugar de "MVP"
- Mantener tono profesional y confiado
- Incluir break-even estimado

### ❌ EVITAR:
- Jerga técnica excesiva
- Promesas imposibles de cumplir
- Métricas inventadas (horas ahorradas sin validar)
- Mencionar roles específicos (secretaria, gerente, etc.)
- Secciones sobre "proyecto experimental" o disclaimers negativos
- Over-engineering en descripciones técnicas

---

## Checklist Final

Antes de entregar el presupuesto, verificar:

- [ ] Frontmatter completo (titulo, cliente, fecha, total, contacto)
- [ ] Fecha en formato YYYY-MM-DD (fecha actual)
- [ ] Contacto: "Gonzalo Parra · +54 11 2162 5416 · info@skywalking.com"
- [ ] Problema descrito sin mencionar personas específicas
- [ ] Beneficios medibles y realistas
- [ ] Costos claros y bien estructurados
- [ ] Timeline realista
- [ ] Sin secciones de "disclaimer" o "experimental"
- [ ] Archivo guardado en `public/presupuestos/[slug].md`
- [ ] Slug en lowercase con guiones

---

## Ejemplo de Uso

**Usuario:** "Necesito un presupuesto para un bot de WhatsApp para una clínica"

**Mentat:**
1. "Perfecto, voy a ayudarte a crear un presupuesto profesional. Necesito algunos datos:"
2. Hace preguntas específicas sobre el cliente, problema, alcance, costos
3. Genera el archivo markdown siguiendo la estructura
4. Muestra resumen y pide confirmación
5. Guarda el archivo en `public/presupuestos/[slug].md`
6. Confirma que el presupuesto estará disponible en `/[slug]/presupuesto`

---

**Última actualización:** 2025-10-21
**Versión:** 1.0
**Maintainer:** Mentat
