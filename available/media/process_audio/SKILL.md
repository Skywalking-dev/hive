# Skill: process_audio

**Propósito:** Procesar archivos de audio (conversión + transcripción) de forma batch o individual
**Tiempo estimado:** 2-5 min por archivo
**ROI:** ⭐⭐⭐⭐

---

## Input Requerido

- Ruta a archivo de audio (mp3, wav, m4a, ogg, etc.)
- Operaciones deseadas: `--convert`, `--transcribe` o ambas
- Formato de salida (opcional): `--format mp3|wav|m4a`

---

## Output

1. **Audio convertido:** `/tmp/audio_processed/{basename}_{timestamp}.{format}`
2. **Transcripción:** `/tmp/audio_processed/{basename}_{timestamp}.txt`
3. **Metadata:** duración, tamaño, preview del texto

---

## Pasos de Ejecución

1. Validar que archivo de entrada existe
2. Verificar dependencias (ffmpeg, OPENAI_API_KEY si transcribe)
3. Crear directorio de output si no existe
4. Si `--convert`:
   - Convertir a formato especificado con ffmpeg
   - Extraer metadata (duración, tamaño)
5. Si `--transcribe`:
   - Upload audio a OpenAI Whisper API
   - Guardar transcript en .txt
   - Mostrar preview
6. Reportar paths de outputs

---

## Principios

### ✅ HACER:
- Validar archivo existe antes de procesar
- Usar timestamps en nombres para evitar colisiones
- Comprimir audio a 128kbps para reducir costos de API
- Mostrar preview de transcripción (primeras 3 líneas)
- Reportar metadata útil (duración, tamaño)

### ❌ EVITAR:
- Sobrescribir archivos originales
- Transcribir sin validar OPENAI_API_KEY
- Procesar archivos >25MB sin split (límite Whisper API)

---

## Uso Desde Claude Code

Cuando usuario solicita procesar audio:

1. **Conversión simple:**
```bash
skills/process_audio/scripts/process_audio.sh /path/to/audio.wav --convert --format mp3
```

2. **Solo transcribir:**
```bash
skills/process_audio/scripts/process_audio.sh /path/to/audio.mp3 --transcribe
```

3. **Conversión + transcripción:**
```bash
skills/process_audio/scripts/process_audio.sh /path/to/audio.m4a --convert --transcribe --format mp3
```

4. **Batch processing (múltiples archivos):**
```bash
for f in /path/to/audios/*.wav; do
  skills/process_audio/scripts/process_audio.sh "$f" --convert --transcribe --format mp3
done
```

---

## Checklist Final

- [ ] Script ejecutable (`chmod +x`)
- [ ] ffmpeg instalado (`brew install ffmpeg`)
- [ ] OPENAI_API_KEY en `.env` (si transcribe)
- [ ] Output dir configurable via `AUDIO_OUTPUT_DIR`
- [ ] Archivos generados con timestamps únicos
- [ ] Preview de transcripción mostrado

---

## Ejemplo de Uso

**Usuario:** "Necesito transcribir este audio de reunión y convertirlo a mp3"

**Mentat:**
```bash
skills/process_audio/scripts/process_audio.sh /Users/gonza/Downloads/reunion_2025.wav \
  --convert --transcribe --format mp3
```

**Output esperado:**
```
Converting: /Users/gonza/Downloads/reunion_2025.wav -> /tmp/audio_processed/reunion_2025_20250122_143022.mp3
✓ Converted: /tmp/audio_processed/reunion_2025_20250122_143022.mp3
  Duration: 1847.2s | Size: 28M
Transcribing: /tmp/audio_processed/reunion_2025_20250122_143022.mp3
✓ Transcript: /tmp/audio_processed/reunion_2025_20250122_143022.txt
  Preview:
  Bienvenidos a la reunión del equipo de producto. Hoy vamos a discutir...
  La prioridad número uno es finalizar el módulo de pagos antes del...
  Necesitamos coordinar con el equipo de backend para la integración...

Done. Output dir: /tmp/audio_processed
```

---

## Dependencias

- **ffmpeg:** Conversión de formatos (`brew install ffmpeg`)
- **OpenAI API:** Whisper para transcripción (configura `OPENAI_API_KEY` en `.env`)
- **curl:** Upload a API (nativo en macOS/Linux)

---

## Limitaciones

- Whisper API: max 25MB por archivo (split si excede)
- Idioma predeterminado: español (`language=es`)
- Formato conversión: mp3 @ 128kbps

---

## Mejoras Futuras

- [ ] Soporte para batch con progress bar
- [ ] Auto-split archivos >25MB
- [ ] Detección automática de idioma
- [ ] Timestamps en transcripción (formato SRT/VTT)
- [ ] Integración con Supabase Storage

---

**Última actualización:** 2025-01-22
**Versión:** 1.0
**Maintainer:** Mentat
