import type React from "react";
import { AbsoluteFill, CalculateMetadataFunction, OffthreadVideo, staticFile } from "remotion";

// Corrección de color "cinematográfica sobria" sobre la grabación completa.
// Se exporta como un video nuevo; la grabación original no se modifica.
export type GradeoProps = {
  video: string; // ruta dentro de public/
  duracion: number; // segundos
  contraste: number;
  saturacion: number;
  brillo: number;
  sombrasFrias: number; // 0–1: tinte azul petróleo en sombras
  lucesCalidas: number; // 0–1: tinte ámbar en luces
  vineta: number; // 0–1
};

export const Gradeo: React.FC<GradeoProps> = (p) => (
  <AbsoluteFill style={{ backgroundColor: "black" }}>
    <OffthreadVideo
      src={staticFile(p.video)}
      style={{ width: "100%", height: "100%", filter: `contrast(${p.contraste}) saturate(${p.saturacion}) brightness(${p.brillo})` }}
    />
    {/* Sombras frías: el color se multiplica sobre todo en las zonas oscuras */}
    <AbsoluteFill style={{ backgroundColor: "#1d4f5c", mixBlendMode: "soft-light", opacity: p.sombrasFrias }} />
    {/* Luces cálidas suaves */}
    <AbsoluteFill style={{ backgroundColor: "#ffb36b", mixBlendMode: "overlay", opacity: p.lucesCalidas * 0.35 }} />
    <AbsoluteFill
      style={{ background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,${p.vineta}) 100%)` }}
    />
  </AbsoluteFill>
);

export const metadatosGradeo: CalculateMetadataFunction<GradeoProps> = ({ props }) => ({
  durationInFrames: Math.round(props.duracion * 30),
});

export const gradeoEjemplo: GradeoProps = {
  video: "fuentes/mi-video.mp4",
  duracion: 41.014,
  contraste: 1.08,
  saturacion: 0.84,
  brillo: 0.97,
  sombrasFrias: 0.22,
  lucesCalidas: 0.18,
  vineta: 0.32,
};
