import type React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { montserrat, openSans } from "./fuentes";
import { Destacado, VERDE } from "./tipos";

// Textos destacados grandes en mayúsculas.
// - "bold"/"italic": mezcla Open Sans ExtraBold + Light itálica, suben desde detrás de la persona
//   (en CapCut va encima una copia recortada de la persona).
// - "titulo"/"titulo-verde": estilo portada, Montserrat Black itálica; cada línea aparece en su momento.
export const Destacados: React.FC<{ destacados: Destacado[] }> = ({ destacados }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const d = destacados.find((x) => t >= x.s && t < x.e);
  if (!d) return null;

  const f0 = Math.round(d.s * fps);
  const salida = interpolate(t, [d.e - 0.18, d.e], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div style={{ position: "absolute", top: `${d.top}%`, display: "flex", flexDirection: "column", alignItems: "center", opacity: salida }}>
        {d.lineas.map((l, i) => {
          const titulo = l.estilo.startsWith("titulo");
          const inicio = f0 + Math.round((l.desde ?? i * 0.13) * fps);
          if (titulo) {
            const verde = l.estilo === "titulo-verde";
            const pop = spring({ frame: frame - inicio, fps, config: { damping: 11, stiffness: 190, mass: 0.8 } });
            const tamano = Math.min(150, 1000 / (l.texto.length * 0.74)) * (d.escala ?? 1);
            return (
              <div
                key={i}
                style={{
                  fontFamily: montserrat,
                  fontWeight: 900,
                  fontStyle: "italic",
                  fontSize: tamano,
                  lineHeight: 1.02,
                  letterSpacing: -2,
                  textTransform: "uppercase",
                  whiteSpace: "nowrap",
                  color: verde ? VERDE : "white",
                  textShadow: verde
                    ? `0 0 28px rgba(59,209,90,0.55), 0 6px 0 rgba(0,0,0,0.35), 0 12px 36px rgba(0,0,0,0.45)`
                    : "0 6px 0 rgba(0,0,0,0.30), 0 12px 36px rgba(0,0,0,0.45)",
                  opacity: frame < inicio ? 0 : interpolate(pop, [0, 0.35], [0, 1], { extrapolateRight: "clamp" }),
                  scale: String(interpolate(pop, [0, 1], [1.35, 1])),
                  filter: `blur(${interpolate(pop, [0, 0.7], [10, 0], { extrapolateRight: "clamp" })}px)`,
                }}
              >
                {l.texto}
              </div>
            );
          }
          const sube = spring({ frame: frame - inicio, fps, config: { damping: 16, stiffness: 140 } });
          const bold = l.estilo === "bold";
          // Ajuste al ancho: ~0.68 em por letra en ExtraBold, ~0.6 em en Light itálica
          const tamano = Math.min(bold ? 176 : 128, 980 / (l.texto.length * (bold ? 0.68 : 0.6))) * (d.escala ?? 1);
          return (
            <div
              key={i}
              style={{
                fontFamily: openSans,
                fontWeight: bold ? 800 : 300,
                fontStyle: bold ? "normal" : "italic",
                fontSize: tamano,
                letterSpacing: bold ? -4 : -1,
                lineHeight: 0.98,
                color: "white",
                textTransform: "uppercase",
                whiteSpace: "nowrap",
                textShadow: "0 6px 30px rgba(0,0,0,0.35)",
                translate: `0px ${interpolate(sube, [0, 1], [tamano * 1.6, 0])}px`, // sale desde detrás de la cabeza
                opacity: interpolate(sube, [0, 0.25], [0, 1], { extrapolateRight: "clamp" }),
              }}
            >
              {l.texto}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
