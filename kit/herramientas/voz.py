#!/usr/bin/env python3
"""Deja la voz clara, nítida y con el mismo volumen en todo el video.

Uso: python3 herramientas/voz.py <video de entrada> <video de salida>

1. Ecualización: quita graves (<90 Hz), baja un poco el "barro" (300 Hz), realza presencia (3,5 kHz) y aire (10 kHz).
2. Nivelador: sube las partes bajas y baja las altas hacia un mismo nivel (solo donde hay voz).
3. Limitador suave y normalización final a -14 LUFS (estándar de Instagram/Reels).
El video no se recodifica: solo se reemplaza el audio. La entrada no se modifica.
"""
import math, os, struct, subprocess, sys, wave

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTION = os.path.join(BASE, "motion")
SR = 48000


def ffmpeg(*args):
    r = subprocess.run(["npx", "remotion", "ffmpeg", "-v", "error", "-y", *args], cwd=MOTION, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)


class Biquad:  # fórmulas del "Audio EQ Cookbook" (R. Bristow-Johnson)
    def __init__(self, tipo, f, q=0.707, db=0.0):
        A, w = 10 ** (db / 40), 2 * math.pi * f / SR
        al, c = math.sin(w) / (2 * q), math.cos(w)
        if tipo == "pasaaltos":
            b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
        elif tipo == "pico":
            b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
        else:  # estante agudo
            s = 2 * math.sqrt(A) * al
            b = [A * ((A + 1) + (A - 1) * c + s), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - s)]
            a = [(A + 1) - (A - 1) * c + s, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - s]
        self.b = [x / a[0] for x in b]
        self.a = [x / a[0] for x in a]

    def procesar(self, x):
        b0, b1, b2 = self.b
        _, a1, a2 = self.a
        x1 = x2 = y1 = y2 = 0.0
        out = []
        for v in x:
            y = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            x2, x1, y2, y1 = x1, v, y1, y
            out.append(y)
        return out


def nivelar(x, objetivo_db=-20.0, max_subir=10.0, max_bajar=8.0, puerta_db=-42.0):
    """Ganancia que sigue el nivel de la voz en ventanas de 60 ms, suavizada (ataque 80 ms, relajación 400 ms)."""
    v = int(0.06 * SR)
    ganancias = []
    previa = 0.0
    for i in range(0, len(x), v):
        bloque = x[i:i + v]
        rms = math.sqrt(sum(s * s for s in bloque) / max(1, len(bloque))) or 1e-9
        nivel = 20 * math.log10(rms)
        g = 0.0 if nivel < puerta_db else max(-max_bajar, min(max_subir, objetivo_db - nivel))
        if nivel < puerta_db:
            g = previa  # en silencios se mantiene la última ganancia (no sube el ruido)
        coef = 0.55 if g < previa else 0.15  # baja rápido, sube despacio
        previa = previa + coef * (g - previa)
        ganancias.append(previa)
    out = []
    for i, s in enumerate(x):
        k = i / v
        j = min(int(k), len(ganancias) - 1)
        j2 = min(j + 1, len(ganancias) - 1)
        g = ganancias[j] + (ganancias[j2] - ganancias[j]) * (k - j)
        out.append(s * 10 ** (g / 20))
    return out


def limitar(x, techo=0.89):
    return [techo * math.tanh(s / techo) if abs(s) > 0.6 * techo else s for s in x]


def main(entrada, salida):
    tmp = os.path.splitext(salida)[0]
    crudo, tratado, final = tmp + "_voz-cruda.wav", tmp + "_voz-tratada.wav", tmp + "_voz-final.wav"
    ffmpeg("-i", entrada, "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", crudo)
    with wave.open(crudo) as w:
        n = w.getnframes()
        x = [s / 32768 for s in struct.unpack(f"<{n}h", w.readframes(n))]
    for f in (Biquad("pasaaltos", 90), Biquad("pico", 300, 1.0, -2.0), Biquad("pico", 3500, 0.9, 3.0), Biquad("agudos", 10000, 0.7, 2.0)):
        x = f.procesar(x)
    x = limitar(nivelar(x))
    with wave.open(tratado, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32767)) for s in x))
    ffmpeg("-i", tratado, "-af", "loudnorm=I=-14:LRA=5:TP=-1.5", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", final)
    ffmpeg("-i", entrada, "-i", final, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", salida)
    for f in (crudo, tratado, final):
        os.remove(f)
    print(salida)


if __name__ == "__main__":
    main(*sys.argv[1:3])
