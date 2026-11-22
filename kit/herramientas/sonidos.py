#!/usr/bin/env python3
"""Efectos de sonido y base musical generados por síntesis (sin licencias de terceros).

python3 herramientas/sonidos.py            -> crea los efectos fijos en audio/sfx/
musica_tension(ruta, duracion, golpes)     -> base dramática con golpes en tiempos dados (la usa armar_reel.py)
"""
import math, os, random, struct, wave

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(BASE, "audio", "sfx")


def guardar(ruta, muestras, sr=48000, pico_dest=0.89):
    pico = max(abs(x) for x in muestras) or 1
    with wave.open(ruta, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(32767 * pico_dest * x / pico)) for x in muestras))


def mezclar(dest, src, inicio):
    for i, x in enumerate(src):
        if 0 <= inicio + i < len(dest):
            dest[inicio + i] += x


class Paso:  # filtro paso bajo de un polo
    def __init__(self):
        self.y = 0.0

    def __call__(self, x, corte, sr):
        a = 1 - math.exp(-2 * math.pi * corte / sr)
        self.y += a * (x - self.y)
        return self.y


def pop(sr=48000, d=0.16, base=260, barrido=900):
    out, fase = [], 0.0
    for i in range(int(sr * d)):
        t = i / sr
        fase += 2 * math.pi * (base + barrido * math.exp(-t * 38)) / sr
        out.append(math.sin(fase) * math.exp(-t * 28) * min(1, t * 2000))
    return out


def whoosh(sr=48000, d=0.55, desde=300, hasta=4500, semilla=7):
    random.seed(semilla)
    out, f1, f2 = [], Paso(), Paso()
    for i in range(int(sr * d)):
        x = i / sr / d
        corte = desde + (hasta - desde) * math.sin(math.pi * x) ** 2
        a = f1(random.uniform(-1, 1), corte, sr)
        b = f2(a, corte, sr)
        out.append((a - 0.6 * b) * math.sin(math.pi * x) ** 1.5)
    return out


def boom(sr=48000, d=1.3, f0=55, f1=30, ruido=0.35, semilla=3):
    random.seed(semilla)
    out, fase, lp = [], 0.0, Paso()
    for i in range(int(sr * d)):
        t = i / sr
        fase += 2 * math.pi * (f1 + (f0 - f1) * math.exp(-t * 6)) / sr
        n = lp(random.uniform(-1, 1), 900, sr) * math.exp(-t * 14) * ruido
        out.append((math.sin(fase) * math.exp(-t * 3.2) + n) * min(1, t * 400))
    return out


def riser(sr=48000, d=0.95, semilla=11):
    random.seed(semilla)
    out, fase, f1, f2 = [], 0.0, Paso(), Paso()
    for i in range(int(sr * d)):
        x = i / sr / d
        fase += 2 * math.pi * (180 + 700 * x ** 2) / sr
        corte = 400 + 5000 * x ** 2
        a = f1(random.uniform(-1, 1), corte, sr)
        b = f2(a, corte, sr)
        env = x ** 2.2
        out.append((0.55 * (a - 0.5 * b) + 0.35 * math.sin(fase) + 0.15 * math.sin(2 * fase)) * env)
    return out


def campanita(sr=48000, d=0.6, notas=(1318.5, 1975.5), separacion=0.09):
    out = [0.0] * int(sr * d)
    for k, f in enumerate(notas):
        ini = int(k * separacion * sr)
        for i in range(len(out) - ini):
            t = i / sr
            out[ini + i] += (math.sin(2 * math.pi * f * t) + 0.25 * math.sin(4 * math.pi * f * t)) * math.exp(-t * 7) * min(1, t * 300)
    return out


def escaneo(sr=48000, d=1.6):
    """Tono suave que sube mientras se verifica el rostro y campanita de éxito a 1,15 s."""
    out, fase = [], 0.0
    for i in range(int(sr * d)):
        t = i / sr
        x = min(1, t / 1.1)
        fase += 2 * math.pi * (520 + 520 * x) / sr
        env = (0 if t > 1.12 else min(1, t * 6)) * (0.5 + 0.5 * math.sin(2 * math.pi * 9 * t) ** 2)
        out.append(0.22 * math.sin(fase) * env)
    mezclar(out, [0.5 * x for x in campanita(sr, 0.45, (1567.98, 2093.0), 0.07)], int(1.15 * sr))
    return out


def reverb(x, sr, mezcla=0.35, tamano=1.0):
    """Reverb sencilla (Schroeder): 4 filtros peine en paralelo + 2 pasa-todo."""
    largo = len(x) + int(sr * 2.5 * tamano)
    seco = list(x) + [0.0] * (largo - len(x))
    humedo = [0.0] * largo
    for ms, g in ((29.7, 0.80), (37.1, 0.78), (41.1, 0.76), (43.7, 0.74)):
        dl = int(sr * ms * tamano / 1000)
        buf = [0.0] * largo
        for i in range(largo):
            buf[i] = seco[i] + (g * buf[i - dl] if i >= dl else 0.0)
            humedo[i] += buf[i] * 0.25
    for ms, g in ((5.0, 0.7), (1.7, 0.7)):
        dl = int(sr * ms / 1000)
        ent, sal = humedo, [0.0] * largo
        for i in range(largo):
            xd = ent[i - dl] if i >= dl else 0.0
            yd = sal[i - dl] if i >= dl else 0.0
            sal[i] = -g * ent[i] + xd + g * yd
        humedo = sal
    return [(1 - mezcla) * a + mezcla * b for a, b in zip(seco, humedo)]


def escalofrio(sr=48000, d=3.2):
    """Remate oscuro y profesional: grave profundo + acorde disonante que se apaga + aire con reverb."""
    random.seed(13)
    out, lp = [0.0] * int(sr * d), Paso()
    mezclar(out, [1.0 * x for x in boom(sr, 2.6, 52, 26, 0.3)], 0)
    for f in (146.83, 155.56, 220.0, 293.66 * 1.0595):  # Re, Mib, La, Mib agudo: segunda menor inquietante
        for i in range(len(out)):
            t = i / sr
            out[i] += 0.12 * (math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t)) * math.exp(-t * 1.3) \
                      * min(1, t * 25) * (0.8 + 0.2 * math.sin(2 * math.pi * 5.5 * t))
    for i in range(int(sr * 1.5)):
        t = i / sr
        out[i] += 0.25 * lp(random.uniform(-1, 1), 2500, sr) * math.exp(-t * 2.5) * min(1, t * 60)
    return reverb(out, sr, 0.4, 1.2)[: int(sr * (d + 1.2))]


def revelacion(sr=48000):
    """Para "VIDEO": golpe tonal suave + soplo corto (variación del pop)."""
    out = [0.0] * int(sr * 0.9)
    mezclar(out, [0.8 * x for x in boom(sr, 0.7, 120, 70, 0.15)], 0)
    mezclar(out, [0.5 * x for x in whoosh(sr, 0.35, 1200, 6000, 21)], 0)
    for i in range(int(sr * 0.6)):
        t = i / sr
        out[i] += 0.25 * math.sin(2 * math.pi * 880 * t) * math.exp(-t * 9) * min(1, t * 500)
    return reverb(out, sr, 0.25, 0.6)[: int(sr * 1.4)]


def pluck(sr, f, d=0.5):
    """Cuerda pulsada (Karplus-Strong)."""
    random.seed(int(f))
    n = int(sr / f)
    buf = [random.uniform(-1, 1) for _ in range(n)]
    out = []
    for i in range(int(sr * d)):
        a = buf[i % n]
        b = buf[(i + 1) % n]
        buf[i % n] = 0.996 * 0.5 * (a + b)
        out.append(a)
    return out


def seguir(sr=48000):
    """Para "seguí a @marca": dos notas pulsadas que suben + destello suave."""
    out = [0.0] * int(sr * 1.0)
    mezclar(out, [0.6 * x for x in pluck(sr, 659.25, 0.7)], 0)
    mezclar(out, [0.6 * x for x in pluck(sr, 987.77, 0.7)], int(0.09 * sr))
    mezclar(out, [0.25 * x for x in campanita(sr, 0.5, (1975.5,), 0)], int(0.09 * sr))
    return reverb(out, sr, 0.3, 0.7)[: int(sr * 1.6)]


def impacto_alarmante(sr=48000, d=1.6):
    """Golpe fuerte para "o peor": grave que cae saturado, ráfaga de ruido que se cierra y timbre metálico
    disonante. Cola corta para que después quede silencio."""
    random.seed(17)
    n = int(sr * d)
    out, lp, fase = [0.0] * n, Paso(), 0.0
    for i in range(n):
        t = i / sr
        fase += 2 * math.pi * (30 + 90 * math.exp(-t * 9)) / sr
        grave = math.tanh(2.2 * math.sin(fase)) * math.exp(-t * 3.0)
        ruido = lp(random.uniform(-1, 1), 200 + 6000 * math.exp(-t * 7), sr) * math.exp(-t * 6) * 0.8
        metal = sum(math.sin(2 * math.pi * f * t) for f in (311.1, 440.0, 622.3, 987.8)) * 0.07 * math.exp(-t * 4.5)
        out[i] = (grave + ruido + metal) * min(1, t * 1500)
    return reverb(out, sr, 0.18, 0.7)[: int(sr * 1.9)]


def alarma_grave(sr=48000, d=2.6):
    """Para "ya perdimos nuestra identidad": golpe grave + acorde de tritono que late como una alarma lenta."""
    out = [0.0] * int(sr * d)
    mezclar(out, [0.9 * x for x in boom(sr, 2.2, 48, 26, 0.25)], 0)
    for i in range(len(out)):
        t = i / sr
        pulso = 0.55 + 0.45 * math.cos(2 * math.pi * 3.2 * t)  # late ~3 veces por segundo
        v = sum(math.sin(2 * math.pi * f * t) + 0.35 * math.sin(4 * math.pi * f * t) for f in (146.83, 207.65, 293.66))
        out[i] += 0.13 * v * pulso * math.exp(-t * 1.1) * min(1, t * 40)
    return reverb(out, sr, 0.3, 1.0)[: int(sr * (d + 0.8))]


def riser_oscuro(sr=48000, d=5.0, semilla=31):
    """Riser de miedo (variante sin ruido blanco ni glissando): racimo grave disonante que se abre
    poco a poco, con un trémolo que se acelera y un aire muy bajo. Para acompañar sin molestar."""
    random.seed(semilla)
    n = int(sr * d)
    out, lp, lp_aire = [0.0] * n, Paso(), Paso()
    fases = [0.0] * 4
    notas = (73.42, 77.78, 110.0, 155.56)  # Re, Mib, La, Mib: tensión sin melodía
    fase_trem = 0.0
    for i in range(n):
        t = i / sr
        x = t / d
        v = 0.0
        for k, f in enumerate(notas):
            fases[k] += 2 * math.pi * f / sr
            v += sum(math.sin(h * fases[k]) / h for h in range(1, 6))
        v = lp(v, 180 + 1400 * x ** 2, sr)
        fase_trem += 2 * math.pi * (1.5 + 8 * x ** 2) / sr
        trem = 0.7 + 0.3 * math.sin(fase_trem)
        aire = lp_aire(random.uniform(-1, 1), 900 + 3000 * x, sr) * 0.25 * x ** 3
        out[i] = (0.3 * v * trem + aire) * (x ** 1.6) * min(1, (d - t) * 40)
    return out


def golpe_miedo(sr=48000, d=3.0):
    """Golpe de tráiler de miedo para el remate del gancho: grave profundo + "braam" de metales graves
    filtrados + un pitido agudo muy tenue + cola oscura con reverb. Sin saturación ni metal."""
    out = [0.0] * int(sr * d)
    mezclar(out, [0.9 * x for x in boom(sr, 2.4, 50, 24, 0.15)], 0)
    lp = Paso()
    fases = [0.0] * 4
    for i in range(int(sr * 2.2)):
        t = i / sr
        v = 0.0
        for k, f in enumerate((36.71, 73.42, 77.78, 110.0)):
            fases[k] += 2 * math.pi * f * (1 - 0.01 * t) / sr
            v += sum(math.sin(h * fases[k]) / h for h in range(1, 9))
        env = min(1, t / 0.03) * math.exp(-t * 1.6)
        out[i] += 0.16 * lp(v, 160 + 900 * math.exp(-t * 3), sr) * env
    for i in range(int(sr * 2.5)):
        t = i / sr
        out[i] += 0.025 * math.sin(2 * math.pi * 2793 * t) * math.exp(-t * 1.2) * min(1, t * 8)
    return reverb(out, sr, 0.35, 1.3)[: int(sr * (d + 1.0))]


def musica_cierre(ruta, duracion, sr=24000, bpm=112, entrada=0.4, salida=1.6):
    """Beat tech sobrio y seguro (estilo presentación de producto) en Re menor moderno
    (Dm9 - Bbmaj7 - Fmaj7 - C): bombo seco, sub-bajo con bombeo, acordes cortos sincopados y filtrados,
    hi-hats en semicorcheas con dinámica y chasquido en 2 y 4. Sin melodías alegres."""
    random.seed(9)
    n = int(duracion * sr)
    negra = 60 / bpm
    compas = 4 * negra
    acordes = [(174.61, 220.0, 261.63, 329.63), (174.61, 220.0, 233.08, 293.66),
               (174.61, 220.0, 261.63, 329.63), (164.81, 196.0, 261.63, 293.66)]
    raices = [36.71, 29.14, 43.65, 32.70]  # Re1, Sib0, Fa1, Do1 (sub)
    out = [0.0] * n
    # Sub-bajo senoidal en corcheas, bombeado por el bombo
    fase = 0.0
    for i in range(n):
        t = i / sr
        c = int(t / compas) % 4
        fase += 2 * math.pi * raices[c] * 2 / sr
        pos = (t % (negra / 2)) / (negra / 2)
        bombeo = 1 - 0.75 * math.exp(-(t % negra) * 10)
        out[i] = 0.42 * (math.sin(fase) + 0.2 * math.sin(2 * fase)) * math.exp(-pos * 2.5) * bombeo
    # Acordes cortos sincopados (en "y" del 1, en el 2 y en "y" del 3), sierra filtrada
    patron = [0.5, 1.0, 2.5]
    for bar in range(int(duracion / compas) + 1):
        ac = acordes[bar % 4]
        for p in patron:
            t0 = bar * compas + p * negra
            if t0 >= duracion:
                continue
            stab, lp = [], Paso()
            for i in range(int(0.22 * sr)):
                tt = i / sr
                v = sum(sum(math.sin(2 * math.pi * f * h * tt) / h for h in range(1, 6)) for f in ac)
                stab.append(0.05 * lp(v, 600 + 2600 * math.exp(-tt * 14), sr) * math.exp(-tt * 9) * min(1, tt * 400))
            mezclar(out, stab, int(t0 * sr))
    # Batería
    bombo = boom(sr, 0.28, 105, 45, 0.0)
    for k in range(int(0.003 * sr)):
        bombo[k] += 0.5 * random.uniform(-1, 1) * (1 - k / (0.003 * sr))
    def agudo(d, caida):
        x = [random.uniform(-1, 1) * math.exp(-k / sr * caida) for k in range(int(d * sr))]
        return [v - 0.97 * (x[k - 1] if k else 0) for k, v in enumerate(x)]
    hat = agudo(0.035, 110)
    chasquido = [x * 1.0 for x in agudo(0.09, 45)]
    t, k = 0.0, 0
    while t < duracion:
        if k % 4 == 0:
            mezclar(out, [0.8 * x for x in bombo], int(t * sr))
        if k % 16 in (4, 12):  # tiempos 2 y 4
            mezclar(out, [0.30 * x for x in chasquido], int(t * sr))
        dinamica = (0.10, 0.04, 0.07, 0.04)[k % 4]
        mezclar(out, [dinamica * x for x in hat], int(t * sr))
        t += negra / 4
        k += 1
    for i in range(n):
        tt = i / sr
        out[i] *= min(1, tt / entrada) * min(1, max(0.0, (duracion - tt) / salida))
    guardar(ruta, reverb(out, sr, 0.10, 0.5)[:n], sr, 0.85)


def musica_tension(ruta, duracion, golpes, sr=24000, semilla=5, salida=1.8, atenuar=()):
    """Base oscura en Re menor: dron grave que se abre poco a poco, latido que crece
    y golpes ("chan") en los tiempos indicados (segundos desde el inicio)."""
    random.seed(semilla)
    n = int(duracion * sr)
    out = [0.0] * n
    lp, lp2 = Paso(), Paso()
    notas = (73.42, 110.0, 146.83)
    fases = [random.random() * 6.28 for _ in range(len(notas) * 5)]
    for i in range(n):
        t = i / sr
        x = t / duracion
        v = 0.0
        k = 0
        for f in notas:
            for h in range(1, 6):
                fases[k] += 2 * math.pi * f * h * (1 + 0.0015 * (k % 3 - 1)) / sr
                v += math.sin(fases[k]) / h
                k += 1
        corte = 260 + 900 * x ** 1.5
        v = lp2(lp(v, corte, sr), corte * 1.4, sr)
        trem = 0.85 + 0.15 * math.sin(2 * math.pi * 0.25 * t)
        sub = 0.6 * math.sin(2 * math.pi * 36.71 * t)
        env = min(1, t / 1.5) * min(1, (duracion - t) / salida)
        out[i] = (0.55 * v * trem + sub * (0.4 + 0.6 * x)) * env * 0.5
    # Latido (72 ppm) que gana fuerza hacia el final
    latido = boom(sr, 0.35, 70, 45, 0.0)
    periodo = 60 / 72
    t = 1.0
    while t < duracion - 1.5:
        g = 0.15 + 0.35 * (t / duracion)
        mezclar(out, [g * s for s in latido], int(t * sr))
        mezclar(out, [0.6 * g * s for s in latido], int((t + 0.22) * sr))
        t += periodo
    # Golpes "chan": boom grave + acorde menor corto
    for tg in golpes:
        mezclar(out, [0.9 * s for s in boom(sr, 1.4, 60, 32, 0.5)], int(tg * sr))
        acorde = []
        for i in range(int(0.9 * sr)):
            tt = i / sr
            s = sum(math.sin(2 * math.pi * f * tt) + 0.4 * math.sin(4 * math.pi * f * tt) for f in (146.83, 174.61, 220.0))
            acorde.append(0.22 * s * math.exp(-tt * 4.5) * min(1, tt * 200))
        mezclar(out, acorde, int(tg * sr))
    # Atenuaciones: (inicio, fin, ganancia) en segundos desde el inicio, con rampas de 0,25 s
    for a0, a1, g in atenuar:
        for i in range(n):
            t = i / sr
            if a0 - 0.25 < t < a1 + 0.25:
                k = min(1, max(0, (t - (a0 - 0.25)) / 0.25), max(0, ((a1 + 0.25) - t) / 0.25))
                out[i] *= 1 - (1 - g) * k
    guardar(ruta, out, sr, 0.85)


if __name__ == "__main__":
    guardar(os.path.join(SFX, "pop.wav"), pop())
    guardar(os.path.join(SFX, "whoosh.wav"), whoosh())
    guardar(os.path.join(SFX, "whoosh-suave.wav"), whoosh(d=0.4, desde=200, hasta=2500))
    guardar(os.path.join(SFX, "riser-suspenso.wav"), riser())
    guardar(os.path.join(SFX, "impacto-suave.wav"), boom(d=1.2, f0=58, f1=34, ruido=0.25))
    guardar(os.path.join(SFX, "notificacion-suave.wav"), campanita())
    guardar(os.path.join(SFX, "escaneo-facial.wav"), escaneo())
    guardar(os.path.join(SFX, "pop-grave.wav"), pop(base=170, barrido=600))
    guardar(os.path.join(SFX, "escalofrio.wav"), escalofrio())
    guardar(os.path.join(SFX, "revelacion.wav"), revelacion())
    guardar(os.path.join(SFX, "seguir.wav"), seguir())
    guardar(os.path.join(SFX, "impacto-alarmante.wav"), impacto_alarmante())
    guardar(os.path.join(SFX, "alarma-grave.wav"), alarma_grave())
    guardar(os.path.join(SFX, "golpe-miedo.wav"), golpe_miedo())
    print("ok")
