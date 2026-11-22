#!/usr/bin/env python3
"""Arma una versión editable del reel en CapCut a partir de la grabación original.

Uso:  python3 herramientas/armar_reel.py proyectos/reel-01/briefs/brief_v02.json

Lee el brief (JSON) y:
1. Calcula los cortes por silencios y los tiempos de cada palabra en el reel.
2. Renderiza en Remotion dos capas transparentes: "delante" (captions + motion graphics)
   y "detrás" (textos destacados).
3. Crea un proyecto nuevo en CapCut con, de abajo a arriba: video cortado con zooms,
   capa "detrás", persona recortada (solo en los destacados), capa "delante" y la firma final.
Nunca toca los originales. CapCut debe estar cerrado.
"""
import json, os, re, subprocess, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERR = os.path.join(BASE, "herramientas")
MOTION = os.path.join(BASE, "motion")


def remotion(tool, *args):  # ffmpeg/ffprobe que trae Remotion (no hay otro en el sistema)
    return subprocess.run(["npx", "remotion", tool, *args], cwd=MOTION, capture_output=True, text=True)
DRAFTS = os.path.expanduser("~/Movies/CapCut/User Data/Projects/com.lveditor.draft")


def cap(*args, ok=(0,)):
    r = subprocess.run(["npx", "capcut", *map(str, args)], cwd=HERR, capture_output=True, text=True)
    out = (r.stdout.strip().splitlines() or [""])[-1]
    if r.returncode not in ok:
        sys.exit(f"capcut {' '.join(map(str, args[:2]))} falló:\n{r.stdout}\n{r.stderr}")
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return {"raw": r.stdout}


def silencios(audio, db, min_s):
    r = remotion("ffmpeg", "-hide_banner", "-i", audio, "-af", f"silencedetect=noise={db}dB:d={min_s}", "-f", "null", "-")
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(ini, fin))


def palabras(tokens, correcciones):
    """Une tokens de Whisper en palabras con inicio/fin en segundos."""
    out = []
    for t in tokens:
        txt = t["text"]
        if not txt.strip():
            continue
        if txt.startswith(" ") or not out:
            out.append({"w": txt.strip(), "s": t["startMs"] / 1000, "e": t["endMs"] / 1000})
        else:
            out[-1]["w"] += txt
            if re.sub(r"[\W_]", "", txt):  # los signos (".", "?") no alargan la palabra
                out[-1]["e"] = t["endMs"] / 1000
    limpio = []
    for p in out:
        w = re.sub(r'[\"“”.,;:!¡]', "", p["w"])  # se conservan ¿ y ?
        if w:
            limpio.append({**p, "w": w})
    # Corrige nombres propios mal transcritos (frases del original -> texto correcto)
    norm = lambda x: re.sub(r"[\W_]", "", x).lower()
    res, i = [], 0
    while i < len(limpio):
        for mal, bien in correcciones.items():
            m = mal.split(" ")
            if [norm(x["w"]) for x in limpio[i:i + len(m)]] == [norm(x) for x in m]:
                s, e = limpio[i]["s"], limpio[i + len(m) - 1]["e"]
                bs = bien.split(" ")
                paso = (e - s) / len(bs)
                res += [{"w": w, "s": s + j * paso, "e": s + (j + 1) * paso} for j, w in enumerate(bs)]
                i += len(m)
                break
        else:
            res.append(limpio[i])
            i += 1
    return res


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def buscar_frase(ws, frase, ocurrencia=1):
    """Devuelve (inicio, fin) en el original de la n-ésima aparición de una frase dicha."""
    norm = lambda x: re.sub(r"\W", "", x).lower()
    objetivo = [norm(x) for x in frase.split()]
    n = 0
    for i in range(len(ws) - len(objetivo) + 1):
        if [norm(w["w"]) for w in ws[i:i + len(objetivo)]] == objetivo:
            n += 1
            if n == ocurrencia:
                return ws[i]["s"], ws[i + len(objetivo) - 1]["e"]
    sys.exit(f"No encontré la frase en la transcripción: «{frase}»")


def escribir_timelines(proj, cambios):
    """Aplica a mano la escala/posición fija de cada segmento en todas las copias de la línea de tiempo.
    (capcut-cli no tiene comando para la escala fija y los fotogramas clave de escala no se ven en CapCut 9.6.)"""
    for nombre in ("draft_info.json", "template-2.tmp", "draft_content.json"):
        ruta = os.path.join(proj, nombre)
        if not os.path.exists(ruta):
            continue
        try:
            d = json.load(open(ruta))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if "tracks" not in d:
            continue
        for t in d["tracks"]:
            for sg in t["segments"]:
                if sg["id"] in cambios:
                    esc, y = cambios[sg["id"]]
                    sg["clip"]["scale"] = {"x": esc, "y": esc}
                    sg["clip"]["transform"] = {"x": 0.0, "y": y}
        tmp = ruta + ".tmp-armar"
        json.dump(d, open(tmp, "w"), ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, ruta)


def vaciar(proj):
    """Quita todo el contenido de un proyecto creado por este script (para rehacer la misma versión)."""
    d = json.load(open(os.path.join(proj, "draft_info.json")))
    for t in d["tracks"]:
        for sg in t["segments"]:
            cap("remove", proj, sg["id"])
    cap("prune", proj)


def main(brief_path):
    b = json.load(open(brief_path))
    v = b["version"]
    raw = os.path.join(BASE, b["original"])
    proj = os.path.join(DRAFTS, b["proyecto_capcut"])
    graf = os.path.join(BASE, b["carpeta_graficos"])
    if "--solo-datos" in sys.argv:
        pass
    elif subprocess.run(["pgrep", "-i", "capcut"], capture_output=True).returncode == 0:
        sys.exit("CapCut está abierto. Ciérralo con Cmd + Q y vuelve a intentarlo.")
    elif os.path.exists(proj) and "--reiniciar" in sys.argv:
        vaciar(proj)
    elif os.path.exists(proj):
        sys.exit(f"Ya existe el proyecto '{b['proyecto_capcut']}'. Usa un nombre de versión nuevo.")
    fps = b.get("fps", 30)
    fr = lambda t: round(t * fps) / fps  # alinea a fotogramas

    # 1. Cortes por silencios, con reglas distintas por zona del original
    #    (p. ej. sin cortes en la parte de efectos de IA, pocos cortes en la parte dramática)
    c = b["cortes"]
    zonas = c.get("zonas", [{"hasta": 1e9, "pausa_minima": c.get("pausa_minima", 0.35), "margen": c.get("margen", 0.12)}])
    zona = lambda t: next((z for z in zonas if t < z["hasta"]), zonas[-1])
    dur = float(remotion("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", raw).stdout)
    sil = silencios(os.path.join(BASE, b["audio_16k"]), c["umbral_db"], min(z["pausa_minima"] for z in zonas))
    keep, a = [], max(0.0, c.get("inicio", 0.0))
    for s, e in sil:
        z = zona(s)
        if e - s < z["pausa_minima"]:
            continue
        s2, e2 = s + z["margen"], e - z["margen"]
        if s2 < e2 and s2 > a:
            keep.append((a, s2))
            a = e2
    keep.append((a, min(dur, c.get("fin", dur))))
    # Tramos que se quitan a mano (trabas, palabras repetidas): [inicio, fin] en segundos del original
    for q0, q1 in c.get("quitar", []):
        nuevo = []
        for x, y in keep:
            if q1 <= x or q0 >= y:
                nuevo.append((x, y))
                continue
            if x < q0:
                nuevo.append((x, q0))
            if q1 < y:
                nuevo.append((q1, y))
        keep = nuevo
    keep = [(fr(x), fr(y)) for x, y in keep if y - x > 0.15]

    # Cortes invisibles forzados (p. ej. el final del gancho) y tramos largos divididos en el
    # inicio de una palabra para poder cambiar el zoom
    ws = palabras(json.load(open(os.path.join(BASE, b["transcripcion"]))), b["captions"].get("correcciones", {}))
    forzados = [fr(t) for t in c.get("forzar", [])]
    con_forzados = []
    for x, y in keep:
        for t in forzados:
            if x + 0.3 < t < y - 0.3:
                con_forzados.append((x, t))
                x = t
        con_forzados.append((x, y))
    partidos = []
    for x, y in con_forzados:
        maximo = zona(x).get("tramo_maximo", b["zoom"].get("tramo_maximo", 99))
        while y - x > maximo:
            n = int((y - x) // maximo) + 1
            ideal = x + (y - x) / n
            inicios = [fr(w["s"]) for w in ws if x + 1.0 < w["s"] < y - 1.0]
            if not inicios:
                break
            corte = min(inicios, key=lambda t: abs(t - ideal))
            partidos.append((x, corte))
            x = corte
        partidos.append((x, y))
    keep = partidos

    def mapa(t):  # tiempo del original -> tiempo en el reel
        o = 0.0
        for x, y in keep:
            if t < x:
                return o
            if t <= y:
                return o + t - x
            o += y - x
        return o

    total = fr(sum(y - x for x, y in keep))

    # 2. Captions, destacados y gráficos en tiempos del reel
    resaltar = {re.sub(r"\W", "", w).lower() for w in b["captions"]["resaltar"]}
    minimo = b["captions"].get("duracion_minima", 0.25)
    # Palabras que caen en un tramo quitado (trabas) no van en los captions
    ws = [w for w in ws if not any(q0 <= w["s"] < q1 for q0, q1 in c.get("quitar", []))]
    cues = []
    for i, p in enumerate(ws):
        s = fr(mapa(p["s"]))
        e = fr(mapa(ws[i + 1]["s"])) if i + 1 < len(ws) else fr(min(total, mapa(p["e"]) + 0.3))
        e = min(e, fr(mapa(p["e"]) + b["captions"].get("max_tras_palabra", 0.45)))  # no quedarse en los silencios
        if cues and (cues[-1][1] - cues[-1][0] < minimo):
            cues[-1] = [cues[-1][0], e, cues[-1][2] + " " + p["w"]]
        else:
            cues.append([s, e, p["w"]])
    for i in range(1, len(cues)):
        cues[i][0] = max(cues[i][0], cues[i - 1][1])
    for a_, b_ in b["captions"].get("no_separar", []):  # p. ej. ["Marca", "ID"]: van juntos en un caption
        for i in range(len(cues) - 1):
            if cues[i][2].endswith(a_) and cues[i + 1][2].startswith(b_):
                cues[i][2] += " " + b_
                cues[i + 1][2] = cues[i + 1][2][len(b_):].strip()
    cues = [c for c in cues if c[2]]
    def texto_caption(w):
        w = w.lower()
        for propio in b["captions"].get("nombres_propios", ["IA"]):  # se escriben siempre así
            w = re.sub(rf"\b{propio.lower()}\b", propio, w)
        return w

    captions = [{"s": s, "e": e, "texto": texto_caption(w),
                 "resaltar": any(re.sub(r"\W", "", x).lower() in resaltar for x in w.split()),
                 "clave": [x for x in w.split() if re.sub(r"\W", "", x).lower() in resaltar]}
                for s, e, w in cues if e > s]

    destacados, ocultar, sonidos = [], [], []
    for d in b.get("destacados", []):
        s0, e0 = buscar_frase(ws, d["frase"], d.get("ocurrencia", 1))
        s, e = fr(mapa(s0) + d.get("adelanto", 0.0)), fr(mapa(e0) + d.get("extra", 0.4))
        if "fin_original" in d:
            e = fr(mapa(d["fin_original"]))
        s = 0.0 if s < 0.2 else s
        destacados.append({"s": s, "e": e, "top": d["top"], "lineas": d["lineas"], "recortar": d.get("recortar", True),
                           "zoom": d.get("zoom"), "top_auto": d.get("top_auto", False), "tapado": d.get("tapado", 0.35),
                           "margen": d.get("margen", 0.0)})
        if d.get("sonido"):
            sonidos.append((s + d.get("sonido_desfase", 0.0), d["sonido"], d.get("volumen", 0.5)))
        for desfase, archivo, vol in d.get("sonidos_extra", []):
            sonidos.append((s + desfase, archivo, vol))
        if d.get("ocultar_captions", True):
            ocultar.append([s, e])
    graficos = []
    for g in b.get("graficos", []):
        if "frase" in g:
            s0, e0 = buscar_frase(ws, g["frase"], g.get("ocurrencia", 1))
            s, e = fr(mapa(s0) + g.get("adelanto", 0.0)), fr(mapa(e0) + g.get("extra", 0.5))
        if "inicio_original" in g:
            s = fr(mapa(g["inicio_original"]))
        if "fin_original" in g:
            e = fr(mapa(g["fin_original"]))
        if "inicio_reel" in g:
            s = fr(g["inicio_reel"])
        if "fin_reel" in g:
            e = fr(g["fin_reel"])
        gr = {"tipo": g["tipo"], "s": max(0.0, s), "e": e}
        for k in ("texto", "arriba", "debajo_de_cara", "top", "arriba_de_cabeza"):
            if k in g:
                gr[k] = g[k]
        if "items" in g:  # cada chip aparece cuando se dice su palabra
            gr["items"] = [{"texto": it["texto"], "icono": it["icono"], "grupo": it.get("grupo", "empresas"),
                            "s": fr(mapa(buscar_frase(ws, it["frase"], it.get("ocurrencia", 1))[0]) + it.get("adelanto", -0.05))}
                           for it in g["items"]]
        if "conector" in g:  # texto que une dos grupos, aparece cuando se dice
            gr["conector"] = {"texto": g["conector"]["texto"],
                              "s": fr(mapa(buscar_frase(ws, g["conector"]["frase"])[0]))}
        if "alerta_frase" in g:
            gr["alerta"] = fr(mapa(buscar_frase(ws, g["alerta_frase"])[0]))
        graficos.append(gr)
        if g.get("sonido"):
            sonidos.append((max(0.0, s) + g.get("sonido_desfase", 0.0), g["sonido"], g.get("volumen", 0.6)))
        if g.get("ocultar_captions"):
            ocultar.append([max(0.0, s), e])

    # Transiciones (oscurecimiento de suspenso) con su sonido de subida e impacto
    transiciones = []
    for tr in b.get("transiciones", []):
        corte = fr(mapa(tr["corte_original"]))
        transiciones.append({"s": max(0.0, corte - tr.get("antes", 0.9)), "e": corte + tr.get("despues", 0.35), "corte": corte,
                             "intensidad": tr.get("intensidad", 1.0), "destello": tr.get("destello", False)})
        if tr.get("sonido_subida"):
            sonidos.append((max(0.0, corte - tr.get("antes_sonido", 0.95)), tr["sonido_subida"], tr.get("volumen_subida", 0.35)))
        if tr.get("sonido_corte"):
            sonidos.append((corte, tr["sonido_corte"], tr.get("volumen_corte", 0.4)))

    for sx in b.get("sonidos_sueltos", []):
        sonidos.append((fr(mapa(sx["original"])), sx["archivo"], sx.get("volumen", 0.3)))

    # Risers largos de tensión que culminan en un golpe (síntesis propia)
    sys.path.insert(0, HERR)
    import sonidos as sintesis
    for k, rz in enumerate(b.get("risers", [])):
        r0, r1 = fr(mapa(rz["desde_original"])), fr(mapa(rz["hasta_original"]))
        ruta = os.path.join(graf, f"riser-{k + 1}_{v}.wav")
        tipo = rz.get("tipo", "riser")  # "riser" (ruido que sube) u "oscuro" (racimo grave que se abre)
        muestras = sintesis.riser_oscuro(d=r1 - r0, semilla=30 + k) if tipo == "oscuro" else sintesis.riser(d=r1 - r0, semilla=20 + k)
        sintesis.guardar(ruta, muestras)
        sonidos.append((r0, ruta, rz.get("volumen", 0.12)))
        if rz.get("culmina"):
            sonidos.append((r1, rz["culmina"], rz.get("volumen_culmina", 0.3)))

    # Música dramática generada para el tramo pedido, con golpes en palabras clave
    pistas_musica = []
    m = b.get("musica")
    if m:
        ms = fr(mapa(buscar_frase(ws, m["desde_frase"])[0]) + m.get("adelanto", -0.3))
        fin_frase = buscar_frase(ws, m["hasta_frase"])
        me = fr(mapa(fin_frase[0] if m.get("hasta_inicio") else fin_frase[1]) + m.get("extra", 0.8))
        golpes = [mapa(buscar_frase(ws, g)[0]) - ms for g in m.get("golpes_en", [])]
        ruta = os.path.join(graf, f"musica-tension_{v}.wav")
        atenuar = [(mapa(buscar_frase(ws, a["desde_frase"])[0]) - ms, mapa(buscar_frase(ws, a["hasta_frase"])[0]) - ms, a["ganancia"])
                   for a in m.get("atenuar", [])]
        sintesis.musica_tension(ruta, me - ms, golpes, salida=m.get("salida", 1.8), atenuar=atenuar)
        pistas_musica.append((ms, me - ms, ruta, m.get("volumen", 0.25)))
    f = b.get("firma")
    if f and not f.get("fin_reel"):  # automático: la firma dura ~3,9 s tras el fundido (logo completo)
        f["fin_reel"] = fr(total + f.get("duracion_visible", 3.9))
    mc = b.get("musica_cierre")
    if mc and not mc.get("hasta_reel"):  # automático: hasta el último fotograma, mezclada con la firma
        mc["hasta_reel"] = f["fin_reel"] if f else total
    if mc:  # beat suave que entra al pedir que te sigan y se va antes de la firma
        cs_ = fr(mapa(buscar_frase(ws, mc["desde_frase"])[0]) + mc.get("adelanto", -0.4))
        ce = fr(mc["hasta_reel"])
        ruta = os.path.join(graf, f"musica-cierre_{v}.wav")
        sintesis.musica_cierre(ruta, ce - cs_, entrada=mc.get("entrada", 0.6), salida=mc.get("salida", 1.6))
        pistas_musica.append((cs_, ce - cs_, ruta, mc.get("volumen", 0.2)))

    fundido = f.get("fundido", 0) if f else 0
    # 2b. Microzoom de cada tramo (se calcula antes para colocar captions y gráficos según la cara)
    z = b["zoom"]
    caras = sorted(b.get("caras", []), key=lambda c: c["desde_original"])
    def cara_en(src):  # posición de la cara (fracción de la altura, sin zoom) en ese momento del original
        c = [k for k in caras if k["desde_original"] <= src + 1e-6]
        return c[-1] if c else None
    tramos, o = [], 0.0
    for x, y in keep:
        tramos.append({"t": o, "d": y - x, "src": x})
        o += y - x
    solapa = lambda sg, rangos: any(sg["t"] < e - 0.15 and sg["t"] + sg["d"] > s + 0.15 for s, e in rangos)
    alterna, previa, paso, zona_prev = 0, None, 0, None
    for sg in tramos:
        zn = zona(sg["src"])
        dz = next((d for d in destacados if solapa(sg, [(d["s"], d["e"])])), None)
        if zn is not zona_prev:
            paso, zona_prev = 0, zn
        forzado = next((zf["escala"] for zf in z.get("forzados", []) if abs(zf["desde_original"] - sg["src"]) < 0.05), None)
        if forzado is not None:  # zoom puntual elegido a mano (p. ej. un golpe dramático)
            esc = forzado
        elif dz is not None:
            esc = dz["zoom"] if dz.get("zoom") is not None else z["destacado"]
        elif zn.get("zoom_progresivo"):  # se va cerrando poco a poco: más tensión
            esc = zn["zoom_progresivo"][min(paso, len(zn["zoom_progresivo"]) - 1)]
            paso += 1
        elif z.get("grafico") is not None and solapa(sg, [(g["s"], g["e"]) for g in graficos]):
            esc = z["grafico"]
        else:
            esc = z["alternos"][alterna % len(z["alternos"])]
            alterna += 1
            if esc == previa:  # dos cortes seguidos nunca con el mismo encuadre
                esc = z["alternos"][alterna % len(z["alternos"])]
                alterna += 1
        previa = esc
        sg["escala"] = esc
        cara = cara_en(sg["src"])
        # Compensación: el centro de la cara queda en el mismo lugar al acercar (transform y: + arriba, en medias alturas)
        if z.get("compensar") is False:  # sin desplazamiento: la posición final de la cara es exacta y predecible
            sg["ty"] = 0.0
        else:
            sg["ty"] = 2 * (cara["centro"] - 0.5) * (esc - 1) if cara else -z["compensar_cara"] * (esc - 1)

    # Cara detectada fotograma a fotograma (herramientas/caras, Vision de macOS) sobre la fuente
    detecciones = json.load(open(os.path.join(BASE, b["caras_archivo"]))) if b.get("caras_archivo") else []

    def cara_en_reel(t0, t1):
        """Cara (arriba, abajo) en fracción de altura entre t0 y t1 del reel, ya con el zoom de cada tramo.
        Devuelve el peor caso (la cara más alta y el mentón más bajo) para que nada la tape."""
        arriba, abajo = [], []
        t = t0
        while t <= t1 + 1e-6:
            sg = next((x for x in tramos if x["t"] <= t < x["t"] + x["d"]), tramos[-1])
            src = sg["src"] + t - sg["t"]
            if detecciones:
                d = min(detecciones, key=lambda k: abs(k["t"] - src))
                if abs(d["t"] - src) < 0.5:
                    esc = sg["escala"]  # zoom alrededor del centro (sin desplazamiento)
                    arriba.append(0.5 + (d["arriba"] - 0.5) * esc)
                    abajo.append(0.5 + (d["abajo"] - 0.5) * esc)
            else:
                cara = cara_en(src)
                if cara:
                    abajo.append(cara["centro"] + (cara["menton"] - cara["centro"]) * sg["escala"])
            t += 0.1
        if not abajo:
            return None
        return (min(arriba) if arriba else None, max(abajo))

    def debajo_de_cara(t_reel, separacion=0.035, hasta=None):
        r = cara_en_reel(t_reel, hasta if hasta is not None else t_reel)
        return None if r is None else r[1] + separacion

    personas = json.load(open(os.path.join(BASE, b["personas_archivo"]))) if b.get("personas_archivo") else []

    def cabeza_en_reel(t0, t1):
        """Punto más alto que alcanza la cabeza (fracción de altura, con zoom) entre t0 y t1."""
        ys, t = [], t0
        while t <= t1 + 1e-6 and personas:
            sg = next((x for x in tramos if x["t"] <= t < x["t"] + x["d"]), tramos[-1])
            n = int(round((sg["src"] + t - sg["t"]) * 30))
            if 0 <= n < len(personas) and "cabeza" in personas[n]:
                ys.append(0.5 + (personas[n]["cabeza"] - 0.5) * sg["escala"])
            t += 0.1
        # Con el texto terminando ARRIBA de la cabeza se usa su punto más alto en la ventana: nunca se tocan
        if not ys:
            return None
        ys.sort()
        return ys[int(len(ys) * 0.15)]  # robusto: ignora un instante en que la cabeza sube de golpe

    # Captions al ritmo de la voz: ninguno empieza en un silencio (lo corre al final del silencio)
    sil_finos = silencios(os.path.join(BASE, b["audio_16k"]), b["captions"].get("silencio_db", -40), 0.12)
    # Tramos sin voz indicados a mano (p. ej. una toma con ruido de ambiente donde no se habla)
    unidos = []  # silencios que se tocan se fusionan en uno
    for a0, a1 in sorted(sil_finos + [tuple(x) for x in b["captions"].get("sin_voz", [])]):
        if unidos and a0 <= unidos[-1][1] + 0.05:
            unidos[-1] = (unidos[-1][0], max(unidos[-1][1], a1))
        else:
            unidos.append((a0, a1))
    sil_finos = unidos
    def reel_a_fuente(t):
        sg = next((x for x in tramos if x["t"] <= t < x["t"] + x["d"]), tramos[-1])
        return sg["src"] + t - sg["t"]
    # Inicio real de cada palabra: Whisper puede correrse ±0,3 s; se ajusta al ataque de voz más cercano
    import math as _math, struct as _struct, wave as _wave
    with _wave.open(os.path.join(BASE, b["audio_16k"])) as w_:
        sr_ = w_.getframerate()
        mu = _struct.unpack(f"<{w_.getnframes()}h", w_.readframes(w_.getnframes()))
    paso_ = int(sr_ * 0.02)
    nivel = [20 * _math.log10(_math.sqrt(sum(x * x for x in mu[i:i + paso_]) / paso_) / 32768 + 1e-9) for i in range(0, len(mu) - paso_, paso_)]
    ataques = [k * 0.02 for k in range(3, len(nivel)) if nivel[k] > -32 and nivel[k] - min(nivel[k - 3:k]) > 9]
    ventana = b["captions"].get("ajuste_ataque", (-0.25, 0.3))
    for cap_ in captions:
        src = reel_a_fuente(cap_["s"] + 0.01)
        cerca = [a for a in ataques if ventana[0] <= a - src <= ventana[1]]
        if cerca:
            a = min(cerca, key=lambda x: abs(x - src))
            cap_["s"] = fr(cap_["s"] + (a - src))
    for i in range(1, len(captions)):  # sin solapes tras el ajuste
        captions[i - 1]["e"] = min(captions[i - 1]["e"], captions[i]["s"])
        captions[i]["s"] = max(captions[i]["s"], captions[i - 1]["s"] + 0.1)

    # Una palabra que Whisper ubicó dentro de un silencio: si está más cerca del inicio del silencio, se dijo
    # antes (el caption se adelanta y termina con la voz); si está más cerca del final, todavía no se dijo
    # (el caption espera a que empiece a hablar; si queda muy corto, se une al siguiente).
    i = 0
    while i < len(captions):
        cap_ = captions[i]
        src = reel_a_fuente(cap_["s"] + 0.01)
        for a0, a1 in sil_finos:
            if not (a0 - 0.02 <= src < a1 - 0.05):
                continue
            if src - a0 < a1 - src:  # antes del silencio
                previo_s = captions[i - 1]["s"] if i > 0 else 0.0
                inicio = fr(max(previo_s + 0.12, cap_["s"] - (src - a0) - 0.22))
                if i > 0:
                    captions[i - 1]["e"] = min(captions[i - 1]["e"], inicio)
                corrimiento = cap_["s"] - inicio
                cap_["s"] = inicio
                fin_silencio_reel = cap_["s"] + corrimiento + (a0 - src)  # dónde empieza el silencio en el reel
                cap_["e"] = fr(max(cap_["s"] + 0.25, min(cap_["e"], fin_silencio_reel + 0.15)))
            else:  # después del silencio
                nuevo = fr(cap_["s"] + (a1 - src))
                if i > 0:
                    captions[i - 1]["e"] = min(captions[i - 1]["e"], fr(cap_["s"]))
                if nuevo < cap_["e"] - 0.1:
                    cap_["s"] = nuevo
                elif i + 1 < len(captions):
                    sig = captions[i + 1]
                    sig["texto"] = cap_["texto"] + " " + sig["texto"]
                    sig["clave"] = cap_["clave"] + sig["clave"]
                    sig["resaltar"] = cap_["resaltar"] or sig["resaltar"]
                    sig["s"] = nuevo
                    sig["e"] = max(sig["e"], fr(nuevo + 0.3))
                    captions.pop(i)
                    i -= 1
            break
        i += 1

    for i in range(len(captions) - 1):  # huecos chicos entre palabras: el caption sigue hasta la próxima
        if captions[i + 1]["s"] - captions[i]["e"] < 0.3:
            captions[i]["e"] = captions[i + 1]["s"]
    if f and f.get("fundido"):  # ningún caption durante el fundido a la firma
        for cap_ in captions:
            cap_["e"] = min(cap_["e"], fr(total - f["fundido"]))
    for a0, a1 in b["captions"].get("sin_voz", []):  # nunca un caption dentro de un tramo sin voz
        r0 = fr(mapa(a0))
        for cap_ in captions:
            if cap_["s"] < r0 < cap_["e"]:
                cap_["e"] = r0
    i = 0  # captions de menos de 0,2 s parpadean: se unen al siguiente si van pegados
    while i < len(captions) - 1:
        a, sig = captions[i], captions[i + 1]
        if a["e"] - a["s"] < 0.2 and sig["s"] - a["e"] < 0.05:
            sig.update(texto=a["texto"] + " " + sig["texto"], clave=a["clave"] + sig["clave"],
                       resaltar=a["resaltar"] or sig["resaltar"], s=a["s"])
            captions.pop(i)
        else:
            i += 1

    cp = b["captions"]
    alto_caption = cp.get("alto", 0.05)  # alto del caption en fracción de pantalla
    capa = cp.get("detras_de_la_cabeza", {})
    ocupado_arriba = [(d["s"], d["e"]) for d in destacados] + \
        [(g["s"], g["e"]) for g in graficos if g["tipo"] in ("etiqueta", "seguir", "escaneo", "cedula")]
    rangos_recorte = []
    usos_layering = [(d["s"], d["e"]) for d in destacados if d.get("recortar", True)]  # los destacados también cuentan
    for cap_ in captions:
        r = cara_en_reel(cap_["s"], cap_["e"])
        if r is None:
            continue
        arriba, abajo = r
        oculto = any(a0 <= cap_["s"] < a1 for a0, a1 in ocultar)
        libre_arriba = not any(cap_["s"] < e and cap_["e"] > s for s, e in ocupado_arriba)
        # Palabra clave detrás de la cabeza (layering): grande, apoyada sobre el pelo; una copia recortada
        # de la persona va encima en CapCut, así la parte baja de las letras queda detrás de la cabeza.
        permitida = not capa.get("solo") or any(re.sub(r"\W", "", k).lower() in
                                                 {re.sub(r"\W", "", x).lower() for x in capa["solo"]} for k in cap_["clave"])
        lejos = all(cap_["s"] - e >= capa.get("separacion_minima", 4.0) or s0 - cap_["e"] >= capa.get("separacion_minima", 4.0)
                    for s0, e in usos_layering)
        if (capa and cap_["clave"] and permitida and lejos and not oculto and libre_arriba and arriba is not None
                and cap_["e"] - cap_["s"] >= capa.get("duracion_minima", 0.3)):
            alto = capa.get("alto", 0.085)
            cabeza = cabeza_en_reel(cap_["s"], cap_["e"])  # punto más alto de la cabeza (máscara de persona)
            if cabeza is None:
                cabeza = arriba - capa.get("pelo", 0.06)
            # la base de las letras entra un poco en la cabeza: solo ~tapado de su alto queda detrás
            top = cabeza - alto * (1 - capa.get("tapado", 0.35)) - capa.get("margen", 0.0)
            if top >= capa.get("altura_minima", 0.1):
                cap_["detras"] = True
                cap_["top"] = round(100 * top, 1)
                cap_["e"] = min(cap_["e"], fr(cap_["s"] + capa.get("duracion_maxima", 0.9)))  # se va rápido
                rangos_recorte.append((cap_["s"], cap_["e"]))
                usos_layering.append((cap_["s"], cap_["e"]))
                continue
        cap_["_debajo"] = abajo + cp.get("separacion", 0.03)
        cap_["_arriba"] = (arriba - cp.get("pelo", 0.07) - alto_caption) if arriba is not None else None
    # Una sola altura por toma (zona): estable, sin saltos. Debajo del mentón si entra en toda la toma;
    # si no, arriba de la cabeza a la altura más segura de la toma.
    por_zona = {}
    for cap_ in captions:
        if "_debajo" in cap_:
            sg = next((x for x in tramos if x["t"] <= cap_["s"] < x["t"] + x["d"]), tramos[-1])
            src = sg["src"] + cap_["s"] - sg["t"]
            plano = sum(1 for x in cp.get("cambios_de_plano", []) if src >= x)  # p. ej. la toma se aleja
            por_zona.setdefault((id(zona(src)), plano), []).append(cap_)
    for grupo in por_zona.values():
        debajo = max(c["_debajo"] for c in grupo)
        arribas = [c["_arriba"] for c in grupo if c["_arriba"] is not None]
        if debajo + alto_caption <= cp.get("altura_maxima", 0.8):
            y = max(cp.get("altura_minima", 0.6), debajo)
        elif arribas and min(arribas) >= 0.1:
            y = min(arribas)
        else:
            y = cp.get("altura_arriba", 0.12)
        for c in grupo:
            c["top"] = round(100 * y, 1)
    for cap_ in captions:
        cap_.pop("_debajo", None)
        cap_.pop("_arriba", None)
    graficos.sort(key=lambda g: g["s"])
    for a, sig in zip(graficos, graficos[1:]):  # dos gráficos sobre la cara/cabeza nunca a la vez
        if a["tipo"] in ("escaneo", "cedula") and sig["tipo"] in ("escaneo", "cedula") and a["e"] > sig["s"]:
            a["e"] = fr(sig["s"] - 0.03)

    def tam_linea(l):  # mismo cálculo que Destacados.tsx (px en 1080x1920)
        if l["estilo"].startswith("titulo"):
            return min(150, 1000 / (len(l["texto"]) * 0.74)) * 1.02
        bold = l["estilo"] == "bold"
        return min(176 if bold else 128, 980 / (len(l["texto"]) * (0.68 if bold else 0.6))) * 0.98
    for d in destacados:  # apoyados sobre la cabeza hasta el último fotograma (~35 % de la última línea detrás)
        if d.get("recortar", True) and d.get("top_auto"):
            cab = cabeza_en_reel(d["s"], d["e"])
            if cab is not None:
                alturas = [tam_linea(l) / 1920 for l in d["lineas"]]
                visible = sum(alturas) - d.get("tapado", 0.35) * alturas[-1]
                disponible = cab - d.get("margen", 0.0) - 0.035  # entre el borde de arriba y la cabeza
                d["escala"] = round(min(1.0, disponible / visible), 3) if visible > 0 else 1.0  # si no entra, más chico
                d["top"] = round(100 * max(0.035, cab - visible * d["escala"] - d.get("margen", 0.0)), 1)
    for gr in graficos:
        if gr["tipo"] in ("cedula", "etiqueta", "seguir"):  # arriba: termina antes de que empiece un destacado
            for d in destacados:
                if gr["s"] < d["s"] < gr["e"]:
                    gr["e"] = fr(d["s"] - 0.05)
        if gr["tipo"] == "cedula" and gr.get("arriba_de_cabeza"):
            cab = cabeza_en_reel(gr["s"], gr["e"])
            if cab is not None:
                gr["lado"] = "centro"
                gr["top"] = round(100 * max(0.035, cab - 0.215 * 0.7 - 0.012), 1)
            continue
        if gr["tipo"] == "lista":  # debajo de los captions que se ven en su tramo
            tops = [c["top"] for c in captions if c.get("top") and not c.get("detras") and c["s"] < gr["e"] and c["e"] > gr["s"]]
            if tops:
                gr["top"] = round(min(84, max(tops) + 7.0), 1)
        if gr["tipo"] == "cedula" and detecciones:  # al costado de la cara, del lado con más espacio
            sg = next((x for x in tramos if x["t"] <= gr["s"] < x["t"] + x["d"]), tramos[-1])
            src = sg["src"] + gr["s"] - sg["t"]
            d = min(detecciones, key=lambda k: abs(k["t"] - src))
            x0, x1 = 0.5 + (d["x0"] - 0.5) * sg["escala"], 0.5 + (d["x1"] - 0.5) * sg["escala"]
            gr["lado"] = "izquierda" if x0 > 1 - x1 else "derecha"
            centro = 0.5 + ((d["arriba"] + d["abajo"]) / 2 - 0.5) * sg["escala"]
            gr["top"] = round(100 * (centro - 0.07), 1)
            gr["espacio_libre"] = round(max(x0, 1 - x1), 2)
        if gr.get("debajo_de_cara"):
            y = debajo_de_cara(gr["s"], 0.03, gr["e"])
            if y is not None:
                gr["top"] = round(100 * y, 1)

    props = {"duracion": total, "captions": captions, "ocultarCaptions": ocultar, "destacados": destacados,
             "graficos": graficos, "transiciones": transiciones}
    props["tramos"] = [{"t": round(x["t"], 4), "d": round(x["d"], 4), "src": round(x["src"], 4), "escala": x["escala"]} for x in tramos]
    if b.get("mascara_remotion"):
        props["mascara"] = {**b["mascara_remotion"], "total": len(personas)} if personas else b["mascara_remotion"]
    if detecciones:
        props["caras"] = [{k: round(v, 3) for k, v in d.items() if k in ("t", "arriba", "abajo", "x0", "x1")} for d in detecciones]
    if fundido:
        props["fundidoFinal"] = {"s": fr(total - fundido), "e": total, "video": f["video_remotion"]}
    props_path = os.path.join(graf, f"capas_{v}.json")
    nuevo = json.dumps(props, ensure_ascii=False, indent=1)
    if not os.path.exists(props_path) or open(props_path).read() != nuevo:
        open(props_path, "w").write(nuevo)
    json.dump({"keep": keep, "total": total}, open(os.path.join(graf, f"cortes_{v}.json"), "w"))
    if "--solo-datos" in sys.argv:
        print(props_path)
        return

    # 3. Capas transparentes de Remotion
    capas = {}
    for comp, nombre in (("ReelDelante", "delante"), ("ReelDetras", "detras")):
        salida = os.path.join(graf, f"capa-{nombre}_{v}.mov")
        capas[nombre] = salida
        if os.path.exists(salida) and os.path.getmtime(salida) > os.path.getmtime(props_path) and "--rehacer" not in sys.argv:
            continue  # ya exportada con estos mismos datos
        r = subprocess.run(["npx", "remotion", "render", comp, salida, f"--props={props_path}", "--codec=prores",
                            "--prores-profile=4444", "--image-format=png", "--pixel-format=yuva444p10le", "--log=error"],
                           cwd=MOTION, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"Falló el render de {comp}:\n{r.stdout}\n{r.stderr}")

    # 4. Proyecto de CapCut: video cortado
    if not os.path.exists(proj):
        cap("init", b["proyecto_capcut"], "--ratio", "9:16")
    o, segs = 0.0, []
    for x, y in keep:
        r = cap("add-video", proj, raw, f"{o:.3f}s", f"{dur:.3f}s", "--width", b["ancho"], "--height", b["alto"],
                "--track-name", "principal")
        cap("trim", proj, r["segment_id"], f"{x:.3f}s", f"{y - x:.3f}s")
        segs.append({"id": r["segment_id"], "t": o, "d": y - x, "src": x})
        o += y - x

    # 5. Microzooms fijos por corte (calculados antes, en el paso 2b)
    cambios = {}
    for sg, pre in zip(segs, tramos):
        sg["escala"] = pre["escala"]
        cambios[sg["id"]] = (pre["escala"], pre["ty"])

    # 6. Capa "detrás", persona recortada encima (solo durante los destacados) y capa "delante"
    cap("add-video", proj, capas["detras"], "0s", f"{total:.3f}s", "--width", 1080, "--height", 1920, "--track-name", "texto-detras")
    recortes_capcut = [] if b.get("mascara_remotion") else \
        [d for d in destacados if d["recortar"]] + [{"s": a0, "e": a1} for a0, a1 in rangos_recorte]
    for d in recortes_capcut:  # solo si no se recorta en Remotion
        for sg in segs:
            s, e = max(d["s"], sg["t"]), min(d["e"], sg["t"] + sg["d"])
            if e - s < 1 / fps:
                continue
            r = cap("add-video", proj, raw, f"{s:.3f}s", f"{dur:.3f}s", "--width", b["ancho"], "--height", b["alto"],
                    "--track-name", "persona-recortada")
            cap("trim", proj, r["segment_id"], f"{sg['src'] + s - sg['t']:.3f}s", f"{e - s:.3f}s")
            cap("matting", proj, r["segment_id"])
            cap("volume", proj, r["segment_id"], 0)
            cambios[r["segment_id"]] = cambios[sg["id"]]
    cap("add-video", proj, capas["delante"], "0s", f"{total:.3f}s", "--width", 1080, "--height", 1920, "--track-name", "texto-delante")

    # 7. Efectos de sonido sincronizados con los gráficos y destacados
    g_efectos = b.get("ganancia_efectos", 1.0)  # compensa cuando se cambia el nivel de la voz
    sonidos = [(t0, archivo, vol * g_efectos) for t0, archivo, vol in sonidos]
    pistas = []  # fin del último sonido en cada pista "sfx-N": los que se superponen van a otra pista
    for t0, archivo, vol in sorted(sonidos):
        import wave
        ruta = os.path.join(BASE, archivo)
        with wave.open(ruta) as w:
            dsfx = w.getnframes() / w.getframerate()
        t0 = fr(t0)
        n = next((i for i, fin in enumerate(pistas) if fin <= t0), None)
        if n is None:
            pistas.append(0.0)
            n = len(pistas) - 1
        pistas[n] = t0 + dsfx + 0.05
        cap("add-audio", proj, ruta, f"{t0:.3f}s", f"{dsfx:.3f}s", "--volume", vol, "--track-name", f"sfx-{n + 1}", "--no-probe")

    for k, (ms, md, ruta, vol) in enumerate(pistas_musica):
        cap("add-audio", proj, ruta, f"{ms:.3f}s", f"{md:.3f}s", "--volume", vol, "--track-name", f"musica-{k + 1}", "--no-probe")

    # 8. Firma sonora al final. Con fundido: la capa "delante" ya muestra la firma durante el fundido,
    #    así que aquí el video de la firma empieza donde terminó el fundido y su audio va aparte, completo.
    if f:
        fin = f.get("fin_reel", total + f["duracion"])
        r = cap("add-video", proj, os.path.join(BASE, f["archivo"]), f"{total:.3f}s", f"{f['duracion']:.3f}s",
                "--width", f["ancho"], "--height", f["alto"], "--track-name", "principal")
        cap("trim", proj, r["segment_id"], f"{fundido:.3f}s", f"{fin - total:.3f}s")
        if f.get("audio"):
            cap("volume", proj, r["segment_id"], 0)
            a = cap("add-audio", proj, os.path.join(BASE, f["audio"]), f"{total - fundido:.3f}s", f"{fin - total + fundido:.3f}s",
                    "--volume", f.get("volumen", 1.0), "--track-name", "firma-audio", "--no-probe")
            if f.get("desvanecer_audio"):
                cap("audio-fade", proj, a["segment_id"], "--fade-out", f["desvanecer_audio"])

    # 9. Revisión, duración correcta y escalas fijas
    cap("lint", proj, "--no-probe", "--fix", "--frame-grid", ok=(0, 1))
    tmp = cap("add-text", proj, "0s", "1s", "tmp", "--track-name", "tmp")
    cap("remove", proj, tmp["segment_id"])  # recalcula la duración del proyecto
    escribir_timelines(proj, cambios)

    print(json.dumps({"proyecto": b["proyecto_capcut"], "duracion_reel": round(f.get("fin_reel", total + f["duracion"]) if f else total, 2),
                      "cortes": len(keep), "captions": len(captions), "destacados": len(destacados),
                      "graficos": [g["tipo"] for g in graficos], "zooms": [sg["escala"] for sg in segs]}, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
