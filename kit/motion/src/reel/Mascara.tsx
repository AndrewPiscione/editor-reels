import type React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ReelProps } from "./tipos";

// Qué fotograma del video fuente se ve en este instante del reel y con qué zoom (CapCut escala desde el centro).
export const useFuente = (tramos: NonNullable<ReelProps["tramos"]>) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const tr = tramos.find((x) => t >= x.t && t < x.t + x.d) ?? tramos[tramos.length - 1];
  return { src: tr.src + (t - tr.t), escala: tr.escala };
};

// Lo que va "detrás de la persona": solo se ve fuera de su silueta (máscara de Vision por fotograma,
// transparente donde está la persona), con el mismo zoom que el video en ese corte.
export const MascaraPersona: React.FC<{ p: ReelProps; children: React.ReactNode }> = ({ p, children }) => {
  const { src, escala } = useFuente(p.tramos ?? [{ t: 0, d: 1e9, src: 0, escala: 1 }]);
  if (!p.mascara) return <AbsoluteFill>{children}</AbsoluteFill>;
  // nunca pedir una máscara que no existe (el video puede tener un fotograma más que las máscaras)
  const n = Math.min(Math.max(0, Math.round(src * p.mascara.fps)), (p.mascara.total ?? 1e9) - 1);
  const archivo = staticFile(`${p.mascara.carpeta}/m_${String(n).padStart(5, "0")}.png`);
  return (
    <AbsoluteFill>
      {/* Carga la máscara antes de dibujar el fotograma (Img espera a que esté lista) */}
      <Img src={archivo} style={{ position: "absolute", width: 1, height: 1, opacity: 0 }} />
      <AbsoluteFill
        style={{
          maskImage: `url(${archivo})`,
          WebkitMaskImage: `url(${archivo})`,
          maskSize: `${escala * 100}% ${escala * 100}%`,
          WebkitMaskSize: `${escala * 100}% ${escala * 100}%`,
          maskPosition: "center",
          WebkitMaskPosition: "center",
          maskRepeat: "no-repeat",
          WebkitMaskRepeat: "no-repeat",
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
