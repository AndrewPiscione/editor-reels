#!/usr/bin/env python3
"""Revisor automático de un reel ANTES de entregarlo (criterio de editor, aprendido del feedback del usuario).

Uso: python3 herramientas/revisar_reel.py proyectos/<reel>/briefs/brief_vNN.json
Requiere haber corrido antes: armar_reel.py <brief> --solo-datos

Revisa la versión con los datos reales (cara y silueta detectadas, silencios de la voz) y lista los problemas
por gravedad. Si hay ERRORES, no se entrega: se corrige y se vuelve a revisar.
"""
import json, os, re, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTION = os.path.join(BASE, "motion")

b = json.load(open(sys.argv[1]))
v = b["version"]
graf = os.path.join(BASE, b["carpeta_graficos"])
p = json.load(open(os.path.join(graf, f"capas_{v}.json")))
tramos = p.get("tramos", [])
caps = p["captions"]
graficos = p["graficos"]
destacados = p["destacados"]
total = p["duracion"]
caras = json.load(open(os.path.join(BASE, b["caras_archivo"]))) if b.get("caras_archivo") else []
personas = json.load(open(os.path.join(BASE, b["personas_archivo"]))) if b.get("personas_archivo") else []
problemas = []


def avisar(nivel, t, texto):
    problemas.append((nivel, t, texto))


def tramo(t):
    return next((x for x in tramos if x["t"] <= t < x["t"] + x["d"]), tramos[-1] if tramos else None)


def cara(t):
    """Caja de la cara en el reel (con zoom): (arriba, abajo, x0, x1) o None."""
    tr = tramo(t)
    if not tr or not caras:
        return None
    src = tr["src"] + t - tr["t"]
    d = min(caras, key=lambda k: abs(k["t"] - src))
    if abs(d["t"] - src) > 0.3:
        return None
    z = lambda y: 0.5 + (y - 0.5) * tr["escala"]
    return z(d["arriba"]), z(d["abajo"]), z(d["x0"]), z(d["x1"])


def cabeza(t):
    tr = tramo(t)
    if not tr or not personas:
        return None
    n = int(round((tr["src"] + t - tr["t"]) * 30))
    if 0 <= n < len(personas) and "cabeza" in personas[n]:
        return 0.5 + (personas[n]["cabeza"] - 0.5) * tr["escala"]
    return None


def muestras(s, e, paso=0.1):
    t = s
    while t < e:
        yield t
        t += paso


def cruza(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


def fmt(t):
    return f"{int(t)}:{int(round((t % 1) * 30)):02d}"


def visible(t):
    return not any(a <= t < b for a, b in p["ocultarCaptions"])


# ---------- Captions ----------
for i, c in enumerate(caps):
    dur = c["e"] - c["s"]
    if dur < 0.2:
        avisar("ERROR", c["s"], f"caption «{c['texto']}» dura {dur:.2f} s (parpadea)")
    if i + 1 < len(caps) and c["e"] > caps[i + 1]["s"] + 1e-6:
        avisar("ERROR", c["s"], f"captions superpuestos: «{c['texto']}» y «{caps[i + 1]['texto']}»")
    if "fundidoFinal" in p and c["e"] > p["fundidoFinal"]["s"] + 0.05:
        avisar("AVISO", c["s"], f"caption «{c['texto']}» sigue visible durante el fundido a la firma")
    alto = 0.085 if c.get("detras") else 0.05
    top = (c.get("top") or 66) / 100
    for t in muestras(c["s"], c["e"]):
        if not c.get("detras") and not visible(t):
            continue
        k = cara(t)
        if k and cruza(top, top + alto, k[0], k[1]):
            avisar("ERROR", t, f"caption «{c['texto']}» tapa la cara (texto {top:.2f}–{top + alto:.2f}, cara {k[0]:.2f}–{k[1]:.2f})")
            break
    if c.get("detras"):
        cab = [cabeza(t) for t in muestras(c["s"], c["e"])]
        cab = [x for x in cab if x is not None]
        if cab and top + alto > sorted(cab)[int(len(cab) * 0.15)] + 0.005:
            avisar("AVISO", c["s"], f"«{c['texto']}» detrás de la cabeza termina tocando el pelo (puede verse 'intercalado')")
        if dur > 1.0:
            avisar("AVISO", c["s"], f"«{c['texto']}» detrás de la cabeza dura {dur:.1f} s (que se vaya rápido)")
    if top < 0.035 or top + alto > 0.86:
        avisar("AVISO", c["s"], f"caption «{c['texto']}» fuera de la zona segura de Instagram (top {top:.2f})")

# Saltos de altura dentro de una misma toma
for a, c in zip(caps, caps[1:]):
    tr = tramo(a["s"])
    src_a, src_c = (tr["src"] + a["s"] - tr["t"], tr["src"] + c["s"] - tr["t"]) if tr else (a["s"], c["s"])
    cambio_plano = any(src_a < x <= src_c for x in b.get("captions", {}).get("cambios_de_plano", []))
    if (not a.get("detras") and not c.get("detras") and tramo(a["s"]) is tramo(c["s"]) and not cambio_plano
            and abs((a.get("top") or 66) - (c.get("top") or 66)) > 3):
        avisar("AVISO", c["s"], f"el caption cambia de altura dentro de la misma toma ({a.get('top')} → {c.get('top')})")

# Caption repetido abajo mientras arriba se lee lo mismo
for d in destacados:
    for c in caps:
        if not c.get("detras") and cruza(c["s"], c["e"], d["s"], d["e"]) and visible(c["s"] + 0.01):
            norm = lambda w: re.sub(r"\W", "", w).lower()
            palabras_d = {norm(w) for l in d["lineas"] for w in l["texto"].split() if len(norm(w)) >= 4}
            if any(norm(w) in palabras_d for w in c["texto"].split()):
                avisar("ERROR", c["s"], f"caption «{c['texto']}» repite lo que dice el destacado de arriba")
                break

# Captions en silencios (la voz no acompaña)
r = subprocess.run(["npx", "remotion", "ffmpeg", "-hide_banner", "-i", os.path.join(BASE, b["audio_16k"]), "-af",
                    "silencedetect=noise=-40dB:d=0.35", "-f", "null", "-"], cwd=MOTION, capture_output=True, text=True)
ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
silencios = list(zip(ini, fin)) + [tuple(x) for x in b.get("captions", {}).get("sin_voz", [])]
for c in caps:
    tr = tramo(c["s"])
    src = tr["src"] + c["s"] - tr["t"] if tr else c["s"]
    for a0, a1 in silencios:
        if a0 + 0.1 < src < a1 - 0.1 and visible(c["s"] + 0.01):
            avisar("ERROR", c["s"], f"caption «{c['texto']}» aparece en un silencio (antes de que lo digas)")
            break

# ---------- Layering ----------
usos = sorted([(c["s"], c["e"], c["texto"]) for c in caps if c.get("detras")] +
              [(d["s"], d["e"], d["lineas"][0]["texto"]) for d in destacados if d.get("recortar", True)])
for (a0, a1, ta), (b0, b1, tb) in zip(usos, usos[1:]):
    if b0 - a1 < 4.0:
        avisar("AVISO", b0, f"layering muy seguido: «{ta}» y «{tb}» con {b0 - a1:.1f} s entre sí (mínimo ~4 s)")

# ---------- Gráficos ----------
cajas = {  # zona aproximada de cada gráfico: (alto, x0, x1)
    "comentario": (0.15, 0.1, 0.9), "etiqueta": (0.05, 0.3, 0.7), "seguir": (0.09, 0.1, 0.75),
    "lista": (0.17, 0.05, 0.95), "familia": (0.14, 0.1, 0.9), "banco": (0.18, 0.1, 0.9),
}
for g in graficos:
    if g["tipo"] == "cedula":
        alto, x0, x1 = (0.15, 0.39, 0.61) if g.get("lado") == "centro" else (0.18, 0.0, 0.3) if g.get("lado") == "izquierda" else (0.18, 0.7, 1.0)
    elif g["tipo"] in cajas:
        alto, x0, x1 = cajas[g["tipo"]]
    else:
        continue  # el escaneo va sobre la cara a propósito
    top = (g.get("top") or {"seguir": 12, "etiqueta": 9.5, "lista": 72}.get(g["tipo"], 50)) / 100
    for t in muestras(g["s"] + 0.2, g["e"]):
        k = cara(t)
        if k and cruza(top, top + alto, k[0], k[1]) and cruza(x0, x1, k[2], k[3]):
            avisar("ERROR", t, f"gráfico «{g['tipo']}» tapa la cara")
            break
for a, c in zip(sorted(graficos, key=lambda g: g["s"]), sorted(graficos, key=lambda g: g["s"])[1:]):
    if a["tipo"] != "lista" and c["tipo"] != "lista" and a["e"] > c["s"] + 0.02:
        avisar("ERROR", c["s"], f"dos gráficos a la vez: «{a['tipo']}» y «{c['tipo']}» (recarga el cuadro)")
for g in graficos:
    for d in destacados:
        if g["tipo"] in ("cedula", "etiqueta", "seguir") and d["top"] < 35 and cruza(g["s"], g["e"], d["s"], d["e"]):
            avisar("ERROR", g["s"], f"gráfico «{g['tipo']}» arriba al mismo tiempo que el destacado «{d['lineas'][0]['texto']}»")
    if g["tipo"] in ("escaneo", "cedula", "comentario") and g["e"] - g["s"] > 2.2:
        avisar("AVISO", g["s"], f"gráfico «{g['tipo']}» dura {g['e'] - g['s']:.1f} s (que dure lo que la frase + 0,3 s)")

# ---------- Final y gancho ----------
if "fundidoFinal" in p and tramos:
    dur_audio = float(subprocess.run(["npx", "remotion", "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                      "csv=p=0", os.path.join(BASE, b["audio_16k"])], cwd=MOTION, capture_output=True, text=True).stdout)
    finales = [a0 for a0, a1 in zip(ini, fin) if a1 >= dur_audio - 0.3]
    if finales:  # fin real de la voz (inicio del silencio final), llevado al tiempo del reel
        ultimo = tramos[-1]
        voz_fin = ultimo["t"] + finales[-1] - ultimo["src"]
        if voz_fin > p["fundidoFinal"]["s"] + 0.03:
            avisar("ERROR", voz_fin, "la última palabra se pisa con el fundido a la firma (se corta)")
if destacados and destacados[0]["s"] == 0:
    h = destacados[0]
    if any(c["s"] < h["e"] and visible(c["s"] + 0.01) for c in caps):
        avisar("ERROR", 0, "hay captions durante el gancho (la portada debe quedar limpia)")
    if h.get("recortar", True):
        avisar("ERROR", 0, "el título del gancho pasa por la máscara de persona (puede borrarse)")

# ---------- Informe ----------
orden = {"ERROR": 0, "AVISO": 1}
problemas.sort(key=lambda x: (orden[x[0]], x[1]))
if not problemas:
    print("✔ Sin problemas detectados.")
for nivel, t, texto in problemas:
    print(f"{nivel:5} {fmt(t):>6}  {texto}")
errores = sum(1 for x in problemas if x[0] == "ERROR")
print(f"\n{errores} errores, {len(problemas) - errores} avisos.")
sys.exit(1 if errores else 0)
