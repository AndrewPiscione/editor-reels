#!/bin/zsh
# Instala y prueba todo lo que necesita el editor de reels en este Mac.
# Uso: zsh herramientas/instalar.sh   (desde la carpeta de trabajo, p. ej. ~/Movies/editor-reels)
# No instala nada fuera de esta carpeta. Si falta algo que tiene que instalar la persona, lo dice y se detiene.
set -u
RAIZ="${0:A:h:h}"
cd "$RAIZ"
ok()   { print -P "%F{green}✔%f $1"; }
mal()  { print -P "%F{red}✖%f $1"; }
info() { print "  $1"; }
FALTA=0

print "== Editor de reels: instalación en $RAIZ"

# 1. Mac con Apple Silicon o Intel
[[ "$(uname)" == "Darwin" ]] && ok "macOS $(sw_vers -productVersion) ($(uname -m))" || { mal "Este kit funciona solo en Mac."; exit 1; }

# 2. Herramientas de línea de comandos de Apple (compilador, Python)
if xcode-select -p >/dev/null 2>&1; then ok "Herramientas de desarrollo de Apple"
else mal "Faltan las herramientas de desarrollo de Apple."
     info "Ejecutar: xcode-select --install   (se abre una ventana: Instalar, ~10 min). Después, volver a correr este instalador."
     FALTA=1; fi

# 3. Node.js 18 o más nuevo
if command -v node >/dev/null && [[ "$(node -p 'process.versions.node.split(".")[0]')" -ge 18 ]]; then ok "Node.js $(node -v)"
else mal "Falta Node.js (versión 18 o más nueva)."
     info "Descargar el instalador LTS para macOS desde https://nodejs.org , abrir el .pkg y seguir los pasos."
     FALTA=1; fi

# 4. Python 3
command -v python3 >/dev/null && ok "Python $(python3 -V 2>&1 | cut -d' ' -f2)" || { mal "Falta Python 3 (viene con las herramientas de Apple)."; FALTA=1; }

# 5. CapCut Desktop 9.x
CAPCUT=/Applications/CapCut.app/Contents/Info.plist
if [[ -f "$CAPCUT" ]]; then
  V="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' "$CAPCUT" 2>/dev/null)"
  if [[ "${V%%.*}" -ge 10 ]]; then mal "CapCut $V: la conexión con CapCut acepta hasta la versión 9.x (la 10 rechaza proyectos armados desde afuera)."
     info "Instalar CapCut 9.x o seguir sin CapCut: el reel se puede exportar igual desde Remotion."
  else ok "CapCut Desktop $V"; fi
  [[ -d "$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft" ]] && ok "Carpeta de proyectos de CapCut" \
    || info "Abrir CapCut una vez y crear un proyecto vacío para que exista su carpeta de proyectos."
else mal "Falta CapCut Desktop."
     info "Descargarlo desde https://www.capcut.com/download (versión para Mac), abrirlo una vez, crear un proyecto vacío y cerrarlo."
     FALTA=1; fi

if [[ $FALTA -eq 1 ]]; then print "\nFaltan cosas de arriba: instalarlas y volver a correr este instalador."; exit 2; fi

# 6. Paquetes de Remotion (gráficos) y herramientas
print "\n== Instalando paquetes (unos minutos)…"
(cd motion && npm install --no-fund --no-audit --loglevel=error) && ok "Remotion (motion graphics y captions)" || { mal "Falló la instalación de Remotion"; exit 1; }
(cd herramientas && npm install --no-fund --no-audit --loglevel=error) && ok "capcut-cli y Whisper (paquetes)" || { mal "Falló la instalación de herramientas"; exit 1; }

# Elige un SDK de macOS que compile (los SDK muy nuevos a veces fallan al enlazar)
compilar_con_sdk() {  # $@ = comando a correr
  "$@" >/dev/null 2>&1 && return 0
  for sdk in $(ls -d /Library/Developer/CommandLineTools/SDKs/MacOSX[0-9]*.sdk 2>/dev/null | sort -rV); do
    SDKROOT="$sdk" "$@" >/dev/null 2>&1 && { info "(compilado con $(basename $sdk))"; return 0; }
  done
  return 1
}

# 7. Whisper (transcripción local) + modelo (~1,5 GB)
if [[ -x herramientas/whisper.cpp/main ]]; then ok "Whisper ya compilado"
else
  print "\n== Descargando y compilando Whisper…"
  (cd herramientas && node instalar-whisper.mjs >/dev/null 2>&1) || true
  if [[ ! -x herramientas/whisper.cpp/main ]]; then
    (cd herramientas/whisper.cpp && make clean >/dev/null 2>&1; compilar_con_sdk make -j8 main)
  fi
  [[ -x herramientas/whisper.cpp/main ]] && ok "Whisper compilado" || { mal "No se pudo compilar Whisper"; exit 1; }
fi
if [[ -f herramientas/whisper.cpp/ggml-medium.bin ]]; then ok "Modelo de transcripción"
else print "== Descargando el modelo de transcripción (~1,5 GB)…"
     (cd herramientas && node descargar-modelo.mjs) && ok "Modelo de transcripción" || { mal "No se pudo descargar el modelo"; exit 1; }
fi

# 8. Detección de cara, silueta y recorte (Vision de macOS)
for t in caras personas recortar; do
  if [[ -x "herramientas/$t" ]]; then ok "Herramienta $t"; continue; fi
  (cd herramientas && compilar_con_sdk swiftc -O "$t.swift" -o "$t") && ok "Herramienta $t" || { mal "No se pudo compilar $t"; exit 1; }
done

# 9. Efectos de sonido propios (síntesis, sin licencias)
python3 herramientas/sonidos.py >/dev/null && ok "Efectos de sonido generados en audio/sfx"

# 10. Prueba rápida: Remotion exporta una capa transparente
print "\n== Prueba rápida…"
mkdir -p proyectos/_prueba
(cd motion && npx remotion render ReelDelante ../proyectos/_prueba/capa-prueba.mov --codec=prores --prores-profile=4444 \
   --pixel-format=yuva444p10le --image-format=png --frames=0-29 --log=error) && ok "Remotion exporta capas transparentes" \
   || mal "Remotion no pudo exportar (revisar conexión a internet: las tipografías se descargan de Google Fonts)"
print "\nListo. El editor de reels está instalado."
