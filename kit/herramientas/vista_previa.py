#!/usr/bin/env python3
"""Genera imágenes de vista previa (video + capas de Remotion) en momentos del reel.

Uso: python3 herramientas/vista_previa.py proyectos/reel-01/briefs/brief_v02.json 1.2 13 17 ...
Requiere antes: armar_reel.py <brief> --solo-datos
"""
import json, os, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTION = os.path.join(BASE, "motion")

b = json.load(open(sys.argv[1]))
v = b["version"]
graf = os.path.join(BASE, b["carpeta_graficos"])
props = json.load(open(os.path.join(graf, f"capas_{v}.json")))
cortes = json.load(open(os.path.join(graf, f"cortes_{v}.json")))
salida = os.path.join(BASE, os.path.dirname(b["carpeta_graficos"]), "revisiones", f"vista-previa_{v}")
os.makedirs(salida, exist_ok=True)
os.makedirs(os.path.join(MOTION, "public/vista-previa"), exist_ok=True)

for t in map(float, sys.argv[2:]):
    o, src = 0.0, None
    for x, y in cortes["keep"]:
        if t < o + (y - x):
            src = x + t - o
            break
        o += y - x
    fondo = f"vista-previa/fondo_{t:.2f}.jpg"
    subprocess.run(["npx", "remotion", "ffmpeg", "-v", "error", "-y", "-ss", f"{src:.3f}", "-i", os.path.join(BASE, b["original"]),
                    "-frames:v", "1", os.path.join(MOTION, "public", fondo)], cwd=MOTION, check=True)
    p = os.path.join(salida, f"props_{t:.2f}.json")
    tr = next((x for x in props.get("tramos", []) if x["t"] <= t < x["t"] + x["d"]), None)
    json.dump({**props, "fondo": fondo, "escala": tr["escala"] if tr else 1}, open(p, "w"))
    out = os.path.join(salida, f"t{t:05.2f}.jpg")
    subprocess.run(["npx", "remotion", "still", "VistaPrevia", out, f"--props={p}", f"--frame={round(t * 30)}",
                    "--image-format=jpeg", "--scale=0.4", "--log=error"], cwd=MOTION, check=True)
    os.remove(p)
    print(out)
