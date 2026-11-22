---
name: guiones-reels
description: Escribir guiones de reels con potencial viral para la marca de la persona — de la idea, noticia o caso real al guion por beats (lo que se dice, lo que se ve, dirección y edición), la frase de portada y el copy del post. Usar cuando pida un guion, script, hook o gancho, ideas de video o el copy de un reel.
---

# Guiones de reels

Antes de escribir, leer `marca/perfil.md` de la carpeta de trabajo del editor (voz, idioma, tono, llamado a la
acción, audiencia) y `${CLAUDE_SKILL_DIR}/referencias/metodo.md` (método, fórmulas de gancho, ritmo y reglas
de escritura). Si no hay perfil, preguntar lo mínimo: marca, audiencia, tono e idioma.

## Método (4 pasos)

1. **Insight**: una idea que contradice lo que el espectador da por sentado.
2. **Caso o dato real** con nombre, lugar, cifra y fecha, y **fuente primaria verificada** (link). Si falta, preguntar.
3. **Demostración**: mostrarlo, no contarlo (algo en cámara, pantalla, objeto, mockup, titular anotado).
4. **Tip accionable + llamado a la acción** de la marca.

## Reglas

- Se decide en **2 segundos y sin sonido**: imagen fuerte + frase corta en pantalla que sirve de portada.
- Hook hablado de **8 palabras o menos** (≈3 s). Ninguna línea más de **4 s** sin que cambie algo en pantalla.
- Más de 25 s → segundo micro-hook entre los segundos 6 y 8.
- Ritmo: **165 palabras/minuto** (30 s ≈ 82 palabras, 45 s ≈ 124). Medir con
  `python3 ${CLAUDE_SKILL_DIR}/scripts/contar_beats.py guion.txt`. Recortar si pasa de la duración pedida.
- Una idea y un llamado a la acción. El hook tiene que pagarse: lo que promete, el reel lo cumple.
- Nunca inventar hechos, cifras, citas ni fuentes. En temas sensibles, informar sin enseñar a hacer daño.

## Entrega (formato fijo)

Ficha: título · formato · fuente (link) · audiencia · llamado a la acción · duración · dirección general →
**tabla de beats** (Hook 0–3 s / Tensión / Desarrollo / Tip o insight / Llamado a la acción) con columnas:
Voz · En pantalla · Dirección · Edición → **frase de portada** → **copy** (primera línea fuerte, palabras clave,
3–5 hashtags). Al final: conteo de palabras y segundos por beat, y qué fuentes falta verificar.

Después, la edición sigue la skill `edicion-reels`: el recorrido emocional del video sale de este guion.
Si la persona corrige un guion, anotar su gusto en `marca/perfil.md`.
