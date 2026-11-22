# Editor de reels para Claude Code

Un plugin que convierte a Claude Code en un **editor de reels con criterio profesional**: escribe el guion, corta,
pone captions al ritmo de tu voz, hace texto detrás tuyo (layering), motion graphics, transiciones, sonido, color e
iluminación, y arma todo en **CapCut** para que lo revises y lo exportes.

Funciona en **Mac** (Apple Silicon o Intel) con **Claude Code** (app de escritorio o terminal).

## Qué incluye

| Skill | Para qué |
|---|---|
| `puesta-en-marcha` | Te guía paso a paso para instalar todo (CapCut, Node, Remotion, Whisper…) y armar el perfil de tu marca |
| `guiones-reels` | Escribe guiones con gancho, ritmo y copy listos para grabar |
| `edicion-reels` | Edita tu video de punta a punta y te entrega un proyecto de CapCut para revisar |

Más un kit de herramientas que se copia a tu Mac la primera vez (scripts de edición, revisor automático, proyecto de
Remotion para gráficos y captions, plantillas y la guía de edición).

## Instalación (10 minutos + descargas)

### 1. Tener Claude Code
Si no lo tenés: descargá la app de Claude desde [claude.ai/download](https://claude.ai/download) e iniciá sesión
(pestaña **Code**), o instalá Claude Code siguiendo [code.claude.com](https://code.claude.com/docs).

### 2. Instalar el plugin

**Opción A — desde el archivo `.zip` que te mandaron**
1. Descomprimí `editor-reels.zip` y mové la carpeta `editor-reels` a un lugar fijo, por ejemplo **Documentos**.
   (No la borres después: Claude la usa desde ahí.)
2. Abrí la app **Terminal** del Mac y pegá estas dos líneas (cambiá la ruta si la guardaste en otro lado):
   ```bash
   claude plugin marketplace add ~/Documents/editor-reels
   claude plugin install editor-reels@editor-reels
   ```

**Opción B — desde GitHub** (si te dieron acceso al repositorio)
```bash
claude plugin marketplace add AndrewPiscione/editor-reels
claude plugin install editor-reels@editor-reels
```

### 3. Empezar
Abrí Claude Code (en una sesión nueva) y escribí:

> **Quiero empezar a editar reels. Usá la puesta en marcha.**

Claude te va a explicar qué instala, te va a pedir permiso y te va a guiar de a un paso: descargar CapCut, instalar
Node.js si falta, instalar y probar las herramientas, hacer una prueba con CapCut y completar el perfil de tu marca
(colores, usuario, tono, idioma).

## Uso diario

1. Grabá tu video (o varios clips numerados: `1. ...`, `2. ...`) y dejalo en
   `~/Movies/editor-reels/proyectos/<nombre-del-reel>/originales/`.
2. Pedile a Claude: **"Editá el reel <nombre>"** (o antes: **"escribime un guion sobre…"**).
3. Claude arma la versión en CapCut y te avisa. Abrila, mirala y pedí cambios con tus palabras
   ("el caption tapa mi cara", "más zoom acá", "esa música no").
4. Cuando te guste, exportala desde CapCut.

Cada corrección que le hagas queda anotada en tu carpeta de trabajo, así cada reel sale mejor que el anterior.

## Requisitos y avisos

- **Mac** con macOS reciente, ~3 GB libres e internet durante la instalación.
- **CapCut Desktop 9.x.** La conexión con CapCut usa `capcut-cli`, una herramienta **comunitaria, no oficial**; las
  versiones 10 o más nuevas de CapCut rechazan proyectos armados desde afuera. No actualices CapCut sin probar.
- **Remotion** es gratis para personas y empresas de hasta 3 personas; empresas más grandes necesitan licencia
  ([remotion.dev/license](https://www.remotion.dev/license)).
- La transcripción (Whisper) y la detección de cara funcionan **en tu Mac**: tus videos no se suben a ningún lado.
- Los efectos de sonido y la música se generan por síntesis (sin licencias de terceros).
