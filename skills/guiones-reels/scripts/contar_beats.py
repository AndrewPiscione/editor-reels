"""Cuenta palabras y segundos por beat de un guion de reel (165 palabras/minuto).

Uso: python3 contar_beats.py guion.txt
Formato del archivo: una línea por beat, "Nombre del beat: texto que dice la persona en cámara".
Avisa si el hook pasa de 8 palabras o si alguna frase dura más de 4 s.
"""
import re, sys

PPM = 165

def segundos(palabras):
    return palabras * 60 / PPM

total = 0.0
for n, linea in enumerate(open(sys.argv[1], encoding="utf-8"), 1):
    if ":" not in linea.strip():
        continue
    beat, texto = linea.split(":", 1)
    palabras = len(re.findall(r"\w+", texto))
    s = segundos(palabras)
    total += s
    avisos = []
    if n == 1 and palabras > 8:
        avisos.append(f"hook de {palabras} palabras (máx. 8)")
    for frase in re.split(r"[.!?…]+", texto):
        p = len(re.findall(r"\w+", frase))
        if segundos(p) > 4:
            avisos.append(f"frase de {segundos(p):.1f} s sin corte: «{frase.strip()[:50]}…»")
    print(f"{beat.strip():<14} {palabras:>3} palabras  {s:5.1f} s   (acumulado {total:5.1f} s)"
          + ("   ⚠ " + "; ".join(avisos) if avisos else ""))
print(f"\nTotal ≈ {total:.0f} s")
