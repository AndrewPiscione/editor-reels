import type React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { ReelDelante, ReelDetras } from "./Reel";
import { ReelProps } from "./tipos";

// Solo para revisar: un fotograma del video de fondo con las dos capas encima (sin recorte de persona).
export const VistaPrevia: React.FC<ReelProps & { fondo: string; escala: number }> = (p) => (
  <AbsoluteFill style={{ backgroundColor: "black" }}>
    <Img src={staticFile(p.fondo)} style={{ width: "100%", height: "100%", objectFit: "cover", scale: String(p.escala) }} />
    <ReelDetras {...p} />
    <ReelDelante {...p} />
  </AbsoluteFill>
);
