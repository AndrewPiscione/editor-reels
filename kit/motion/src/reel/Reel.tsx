import type React from "react";
import { AbsoluteFill, CalculateMetadataFunction } from "remotion";
import { Captions } from "./Captions";
import { Destacados } from "./Destacados";
import { Graficos } from "./Graficos";
import { Transiciones } from "./Transiciones";
import { FundidoFinal } from "./FundidoFinal";
import { MascaraPersona } from "./Mascara";
import { ReelProps } from "./tipos";

// Capa que va DELANTE de todo en CapCut: captions y motion graphics.
export const ReelDelante: React.FC<ReelProps> = (p) => (
  <AbsoluteFill>
    <Transiciones transiciones={p.transiciones ?? []} />
    <Graficos graficos={p.graficos} p={p} />
    <Captions captions={p.captions} ocultar={p.ocultarCaptions} capa="delante" />
    {p.fundidoFinal && <FundidoFinal f={p.fundidoFinal} />}
  </AbsoluteFill>
);

// Capa que va DETRÁS de la persona recortada: textos destacados y palabras clave detrás de la cabeza.
export const ReelDetras: React.FC<ReelProps> = (p) => (
  <AbsoluteFill>
    <MascaraPersona p={p}>
      <Destacados destacados={p.destacados.filter((d) => d.recortar !== false)} />
      <Captions captions={p.captions} ocultar={p.ocultarCaptions} capa="detras" />
    </MascaraPersona>
    {/* Títulos que no van detrás de la persona (gancho/portada): sin máscara */}
    <Destacados destacados={p.destacados.filter((d) => d.recortar === false)} />
  </AbsoluteFill>
);

export const metadatosReel: CalculateMetadataFunction<ReelProps> = ({ props }) => ({
  durationInFrames: Math.max(1, Math.round(props.duracion * 30)),
  defaultCodec: "prores",
  defaultProResProfile: "4444",
  defaultVideoImageFormat: "png",
  defaultPixelFormat: "yuva444p10le",
});

export const propsEjemplo: ReelProps = {
  duracion: 6,
  captions: [
    { s: 0, e: 0.6, texto: "ya no sabes", resaltar: false },
    { s: 0.6, e: 1.2, texto: "quién", resaltar: false },
    { s: 1.2, e: 2, texto: "IA", resaltar: true },
  ],
  ocultarCaptions: [[2, 3.5]],
  destacados: [{ s: 2, e: 3.5, top: 14, lineas: [{ texto: "Mi voz", estilo: "bold" }, { texto: "o mi cara", estilo: "italic" }] }],
  graficos: [{ tipo: "seguir", s: 3.5, e: 6 }],
  transiciones: [],
};
