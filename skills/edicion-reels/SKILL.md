---
name: edicion-reels
description: Editar reels verticales (Instagram, TikTok, Shorts) con criterio de editor profesional — cortes, microzooms, captions al ritmo de la voz, texto detrás de la persona (layering), motion graphics en Remotion, transiciones, sonido, música, color e iluminación, armado en CapCut y portada. Usar siempre que la persona pida editar un video o reel, hacer una nueva versión (v02, v03…), corregir captions, gráficos, música o efectos, o preparar una portada.
---

# Edición de reels

Objetivo: editar **como un editor profesional, por criterio propio**, para que la primera versión ya salga cerca de
la final y cada reel necesite menos correcciones.

## Antes de hacer nada

1. Trabajar en la carpeta de trabajo del editor (por defecto `~/Movies/editor-reels`, la que tiene `herramientas/`,
   `motion/` y `marca/perfil.md`). **Si no existe o falta algo instalado, usar primero la skill `puesta-en-marcha`.**
2. Leer completa la guía `GUIA-DE-EDICION.md` de la carpeta de trabajo (si no está: `${CLAUDE_SKILL_DIR}/referencias/guia-de-edicion.md`).
   La sección 0 es el proceso de decisión; la 2, lo que un editor exigente ya rechazó.
3. Leer `marca/perfil.md` (marca, colores, idioma, tono, gustos y rechazos de esta persona).
4. Partir de `plantillas/brief-reel.json` (y `plantillas/clips.json` si son varios clips) → copiar a
   `proyectos/<reel>/briefs/brief_v01.json`.

## Proceso (el detalle está en la guía)

1. **Mirar todo el material** antes de cortar: hoja de contacto (`Hoja`) + transcripción. Qué cuenta la historia,
   qué tomas sin voz deben quedar (pantallas, objetos, gestos), dónde hay trabas, dónde cambia la escena o el plano.
2. **Escribir el recorrido emocional** en el brief (`_recorrido_emocional`). Cada efecto necesita un "porque".
3. **Preparar la fuente**: unir clips (`Combinar`), igualar luz entre tomas, color, luz de rostro, voz (`voz.py`,
   −14 LUFS). Medir sobre la fuente final: cara (`herramientas/caras`), silueta (`herramientas/personas`),
   transcripción palabra por palabra (`transcribir.mjs`), corrigiendo cómo habla la persona y los nombres propios.
4. **Efectos con moderación**: 1 gancho, 2–3 destacados, 2–4 palabras con layering separadas ≥ 4 s, 1 gráfico por
   idea (lo que dura la frase), transición sutil en cada cambio fuerte de escena, 1 riser con remate,
   música solo si la persona la pide.
5. **Ubicar según la cara real**: nada sobre la cara; captions a una altura fija por toma; layering que sale desde
   detrás de la cabeza y termina arriba de ella.
6. **Verificar**: `armar_reel.py --solo-datos` → `revisar_reel.py` (**0 errores**) → `vista_previa.py` de los
   momentos clave **mirando las imágenes** → render de capas → mirar un fotograma de cada capa exportada →
   `armar_reel.py` (con CapCut cerrado) → `capcut lint` y `diagnose` → copia de respaldo.
7. **Entregar**: tabla "pedido → qué hice", lo que no pude comprobar y **una sola acción** para la persona
   (abrir CapCut, entrar al proyecto "<reel> vNN", revisarlo). Exportar también la portada a `finales/`.

## Reglas que no se negocian

- Respetar el tono del perfil. En temas serios: nada caricaturesco (sin rebotes, inclinaciones, flashes ni pops repetidos).
- No inventar hechos ni cambiar lo que dice la persona en captions o títulos.
- Las grabaciones originales no se tocan. Nunca escribir en CapCut con CapCut abierto. Respaldo antes de cada cambio.
- Versiones numeradas (v01, v02…). Cambiar solo lo pedido y avisar si algo afecta otras partes.
- No elegir música si no se pide. Los tiempos que dicta la persona vienen de CapCut como `ss:ff` (30 fps):
  "37:25" = 37 s + 25 fotogramas = 37,83 s.

## Cuando la persona corrige algo nuevo

En la misma sesión: si es criterio de edición, añadirlo a `GUIA-DE-EDICION.md`; si es gusto de su marca, a
`marca/perfil.md`; y si se puede comprobar automáticamente, añadir la comprobación a `herramientas/revisar_reel.py`.
Así cada corrección se aprende una sola vez.
