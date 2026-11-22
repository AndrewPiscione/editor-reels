# Editor de reels (Claude Code + Remotion + CapCut)

> **OBLIGATORIO:** antes de editar un video (nuevo o revisión), leer completa [GUIA-DE-EDICION.md](GUIA-DE-EDICION.md)
> (sección 0 = proceso de decisión) y [marca/perfil.md](marca/perfil.md). Partir de `plantillas/brief-reel.json`.
> **Antes de entregar cualquier versión:** `python3 herramientas/revisar_reel.py <brief>` con 0 errores y mirar las
> vistas previas. Si la persona corrige algo nuevo, anotarlo en la guía (criterio de edición) o en el perfil (gusto
> de marca) en la misma sesión. Si falta algo instalado, usar la skill `puesta-en-marcha`.

Hablar en el idioma de la persona, claro y breve. Puede no ser técnica: hacer yo las pruebas técnicas y pedirle solo
lo imprescindible (abrir/cerrar CapCut, mirar el resultado, dejar archivos en una carpeta), en un bloque corto.

## Herramientas (todo dentro de esta carpeta)

- CapCut Desktop **9.x** (`/Applications/CapCut.app`). No actualizar a 10: capcut-cli rechaza CapCut 10.
  Proyectos de CapCut (no mover): `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<proyecto>/`.
- capcut-cli 0.29.0 (comunitario, no oficial) en `herramientas/node_modules`: `cd herramientas && npx capcut ...`
- Remotion 4.0.535 en `motion/` (captions, gráficos, color). FFmpeg: `npx remotion ffmpeg` / `npx remotion ffprobe`.
- Whisper (whisper.cpp 1.5.5 + modelo medium) en `herramientas/whisper.cpp/`:
  `node herramientas/transcribir.mjs <wav 16k absoluto> <salida.json> [idioma]`.
- `herramientas/caras` (cara por fotograma), `herramientas/personas` (máscara de persona por fotograma),
  `herramientas/recortar` (quita el fondo de una foto): Swift + Vision de macOS.
- `herramientas/armar_reel.py <brief>`: arma el reel (capas de Remotion + proyecto de CapCut). `--solo-datos` solo
  calcula; `--reiniciar` rehace una versión existente.
- `herramientas/revisar_reel.py <brief>`: revisor automático. `herramientas/vista_previa.py <brief> <segundos…>`.
- `herramientas/voz.py` (voz clara y pareja, −14 LUFS), `herramientas/sonidos.py` (efectos y música por síntesis).
- Composiciones de Remotion: `Combinar` (unir clips + color + luz), `Gradeo`, `Hoja`, `VistaPrevia`,
  `ReelDelante` / `ReelDetras` (capas transparentes ProRes 4444).

## Notas técnicas comprobadas
- CapCut 9.6 guarda pero NO muestra fotogramas clave de escala → microzoom = escala fija por tramo (lo hace el script).
- El recorte de persona de CapCut (`matting`) no funciona bien → el texto detrás de la persona se hace en Remotion.
- Remotion no sigue enlaces simbólicos en `motion/public/`: copiar los videos ahí.
- Si un compilador falla con el SDK más nuevo de macOS, probar `SDKROOT=/Library/Developer/CommandLineTools/SDKs/<otro>.sdk`.

## Reglas
- Nunca escribir en un proyecto de CapCut con CapCut abierto (`pgrep -i capcut`). Copia de respaldo antes de cada cambio.
- Las grabaciones de `proyectos/<reel>/originales/` no se tocan nunca. Versiones numeradas: v01, v02…
- Cambiar solo lo pedido. No elegir música si no se pide. No inventar hechos ni cambiar lo que dice la persona.
- No inventar rutas de menús de CapCut: si no hay certeza, pedir una captura.
- Pedir aprobación antes de instalar software, tocar archivos fuera de esta carpeta o subir algo a internet.

## Estructura
```
marca/ (perfil.md, logo, cierre)  referencias/  audio/{musica,sfx}  motion/  herramientas/  plantillas/
proyectos/<reel>/{originales,transcripciones,briefs,graficos,revisiones,finales,respaldos}
```
