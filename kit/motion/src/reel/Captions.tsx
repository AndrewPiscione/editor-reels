import type React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { montserrat } from "./fuentes";
import { Caption } from "./tipos";

import { MARCA } from "./marca";

const VERDE_SUAVE = MARCA.acentoSuave;
const limpiar = (w: string) => w.toLowerCase().replace(/[^\p{L}\p{N}]/gu, "");

// Captions limpios y legibles: 1–2 palabras, Montserrat, a la altura "top" que calcula el script
// (debajo del mentón o arriba de la cabeza según la cara detectada; nunca encima de la cara).
// La palabra clave va en verde y un poco más grande. Entrada suave (crece levemente). Sin contornos ni brillos:
// sobre video, los efectos semitransparentes grandes se ven sucios en CapCut.
export const Captions: React.FC<{ captions: Caption[]; ocultar: [number, number][]; capa: "delante" | "detras" }> = ({
  captions,
  ocultar,
  capa,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const c = captions.find((x) => t >= x.s && t < x.e);
  if (!c || ocultar.some(([a, b]) => t >= a && t < b) || Boolean(c.detras) !== (capa === "detras")) return null;

  const entrada = spring({ frame: frame - Math.round(c.s * fps), fps, config: { damping: 20, stiffness: 240 }, durationInFrames: 7 });
  const clave = new Set((c.clave ?? []).map(limpiar));

  if (capa === "detras") {
    // Detrás de la cabeza: mayúsculas grandes que salen desde atrás de la cabeza y quedan arriba de ella
    const largo = c.texto.length;
    const tamano = Math.min(150, 1000 / (largo * 0.72));
    const sube = spring({ frame: frame - Math.round(c.s * fps), fps, config: { damping: 18, stiffness: 160 } });
    return (
      <AbsoluteFill style={{ alignItems: "center" }}>
        <div
          style={{
            position: "absolute",
            top: `${c.top ?? 20}%`,
            display: "flex",
            gap: 22,
            whiteSpace: "nowrap",
            fontFamily: montserrat,
            fontWeight: 800,
            fontSize: tamano,
            letterSpacing: -3,
            lineHeight: 1,
            textTransform: "uppercase",
            textShadow: "0 3px 10px rgba(0,0,0,0.35)",
            // sale desde detrás de la cabeza (sube ~el alto de las letras) y termina arriba, sin tocarla
            translate: `0px ${interpolate(sube, [0, 1], [tamano * 1.1, 0])}px`,
            opacity:
              interpolate(sube, [0, 0.15], [0, 1], { extrapolateRight: "clamp" }) *
              interpolate(t, [c.e - 0.12, c.e], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          {c.texto.split(" ").map((w, i) => (
            <span key={i} style={{ color: clave.has(limpiar(w)) ? VERDE_SUAVE : "white" }}>
              {w}
            </span>
          ))}
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div
        style={{
          position: "absolute",
          top: `${c.top ?? 66}%`,
          display: "flex",
          alignItems: "baseline",
          gap: 16,
          whiteSpace: "nowrap",
          fontFamily: montserrat,
          letterSpacing: -1.5,
          lineHeight: 1,
          textShadow: "0 2px 8px rgba(0,0,0,0.45)",
          scale: String(interpolate(entrada, [0, 1], [0.88, 1])),
          opacity: interpolate(entrada, [0, 0.4], [0, 1], { extrapolateRight: "clamp" }),
        }}
      >
        {c.texto.split(" ").map((w, i) =>
          clave.has(limpiar(w)) ? (
            <span key={i} style={{ fontWeight: 800, fontSize: 84, color: VERDE_SUAVE }}>
              {w}
            </span>
          ) : (
            <span key={i} style={{ fontWeight: 700, fontSize: 74, color: "white" }}>
              {w}
            </span>
          ),
        )}
      </div>
    </AbsoluteFill>
  );
};
