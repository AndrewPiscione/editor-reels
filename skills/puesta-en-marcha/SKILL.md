---
name: puesta-en-marcha
description: Preparar desde cero un Mac para editar reels con Claude Code + CapCut + Remotion — crear la carpeta de trabajo, instalar y probar las herramientas (CapCut 9.x, Node, Remotion, Whisper, detección de cara y silueta) y completar el perfil de marca, guiando a la persona paso a paso. Usar la primera vez que alguien instala el plugin, cuando dice "empezar", "instalar", "configurar", "no me funciona", o cuando otra skill necesita una herramienta que falta.
---

# Puesta en marcha del editor de reels

La persona puede no ser técnica. Hablale en su idioma, claro y breve. **Hacé vos todo lo técnico** (comandos,
pruebas) y pedile solo lo que tiene que hacer con sus manos (instalar una app, abrir CapCut, elegir una carpeta),
**de a un paso por vez**, diciendo: qué hacer, en qué aplicación, dónde hacer clic y qué debería ver. Esperá su
respuesta antes de seguir. Nunca le pidas que copie comandos a otra terminal: los corrés vos.

El kit completo viene dentro del plugin, en `${CLAUDE_PLUGIN_ROOT}/kit`.

## Paso 1 — Explicar y pedir permiso

Contale en 4–5 líneas qué se va a instalar y por qué, y pedí su OK antes de instalar nada:
- Una carpeta de trabajo en su Mac (por defecto `~/Movies/editor-reels`): ahí viven sus videos, su marca y las
  herramientas. No se instala nada fuera de esa carpeta, salvo las apps que instala la persona (CapCut, Node).
- CapCut Desktop (editor de video gratuito). Claude arma los proyectos y la persona los revisa y exporta.
- Remotion (captions, títulos y motion graphics por código), Whisper (transcripción local, sin subir el video),
  capcut-cli (conexión comunitaria, **no oficial**, con CapCut) y herramientas de macOS para detectar la cara.
- Espacio: ~3 GB. Tiempo: 15–30 min. Requiere conexión a internet durante la instalación.
- **Licencia de Remotion:** gratis para personas y empresas de hasta 3 personas; empresas más grandes necesitan
  licencia (remotion.dev/license). Avisarlo.

## Paso 2 — Crear la carpeta de trabajo

1. Preguntar si usa la carpeta sugerida `~/Movies/editor-reels` u otra. No sobrescribir una carpeta existente
   con contenido: si existe, preguntar.
2. Copiar el kit: `cp -R "${CLAUDE_PLUGIN_ROOT}/kit/" "<carpeta>/"` y crear `<carpeta>/proyectos/`.
3. Si esta sesión de Claude Code no está en esa carpeta, pedirle que abra Claude Code ahí (o moverse a esa carpeta
   si la herramienta lo permite). A partir de acá, todo se hace dentro de la carpeta de trabajo.

## Paso 3 — Instalar y probar

Correr `zsh herramientas/instalar.sh` desde la carpeta de trabajo. El script comprueba cada requisito y, si falta
algo que tiene que instalar la persona, se detiene y lo explica. Guiarla **de a uno**:

| Si falta | Qué le decís a la persona |
|---|---|
| Herramientas de Apple | Lo lanzás vos con `xcode-select --install`; ella hace clic en **Instalar** en la ventana que aparece y espera ~10 min |
| Node.js | Entrar a nodejs.org, descargar la versión **LTS** para macOS, abrir el `.pkg` y seguir los pasos |
| CapCut Desktop | Descargarlo de capcut.com/download (Mac), instalarlo, abrirlo, crear un proyecto vacío y cerrarlo con Cmd + Q |
| CapCut 10 o más nuevo | La conexión acepta hasta 9.x. Opciones: conseguir la 9.x o editar igual y exportar el video final desde Remotion |

Después de cada arreglo, volver a correr el instalador. Si algo falla de forma rara, investigarlo vos (leer el
error, buscar la causa) antes de pedirle algo. No inventes rutas de menús: si no estás seguro, pedile una captura.

## Paso 4 — Prueba con CapCut (5 minutos)

1. Pedirle que cierre CapCut (Cmd + Q). Comprobar con `pgrep -i capcut`.
2. Crear un proyecto de prueba: `cd herramientas && npx capcut init "prueba editor" --ratio 9:16` y agregarle un
   texto (`npx capcut add-text "<ruta del proyecto>" 0s 3s "Hola" --font-size 12`). Ruta de proyectos:
   `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`.
3. Pedirle que abra CapCut, entre a "prueba editor" y confirme que ve el texto. Que lo cierre con Cmd + Q.

## Paso 5 — Perfil de marca

Completar `marca/perfil.md` con una charla corta (de a 2–3 preguntas): nombre de la marca, usuario de Instagram,
tema y audiencia, color de acento (si no sabe, proponer uno y mostrarlo), idioma y cómo habla en cámara (voseo,
tuteo…), tono (serio, didáctico, divertido), llamado a la acción habitual, nombres que Whisper puede escribir mal,
si tiene video de cierre con logo (guardarlo como `marca/cierre.mp4`) y reels de referencia que le gusten
(en `referencias/`). Pasar color y usuario a `motion/src/reel/marca.ts`. Si da reels de referencia, mirarlos
(fotogramas con `npx remotion ffmpeg`) y anotar su estilo en el perfil.

## Paso 6 — Listo

Explicarle cómo se trabaja de acá en adelante, en 4 líneas:
1. Dejar la grabación (o varios clips numerados en orden) en `proyectos/<nombre-del-reel>/originales/`.
2. Pedir: "Editá el reel <nombre>" (y si quiere, "escribí primero el guion": skill `guiones-reels`).
3. Claude arma la versión en CapCut y avisa; la persona la abre, la mira y pide cambios con sus palabras.
4. Cuando le gusta, la exporta desde CapCut.
