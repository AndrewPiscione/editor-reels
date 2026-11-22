import type React from "react";
import { AbsoluteFill, CalculateMetadataFunction, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from "remotion";

// Une varios clips en orden (recortando inicio/fin de cada uno), los lleva a 1080x1920 y 30 fps
// y aplica la misma corrección de color que Gradeo. Los originales no se modifican.
// brillo: multiplicador para igualar tomas; temperatura: + más cálido / - más frío (≈ -1..1)
export type ClipCombinado = { video: string; desde: number; hasta: number; brillo?: number; temperatura?: number };

// Cara detectada (herramientas/caras) en el tiempo del video unido: centro y alto en fracción de pantalla
export type CaraLuz = { t: number; cx: number; cy: number; alto: number };

export type CombinarProps = {
  clips: ClipCombinado[];
  contraste: number;
  saturacion: number;
  brillo: number;
  sombrasFrias: number;
  lucesCalidas: number;
  vineta: number;
  luzRostro?: number; // 0–1: luz suave sobre la cara que sigue su posición
  caras?: CaraLuz[];
};

const FPS = 30;
const fotogramas = (c: ClipCombinado) => Math.round((c.hasta - c.desde) * FPS);

// Luz de rostro: un "rebote" blanco suave centrado en la cara (sigue a la cara detectada más cercana en el tiempo)
const LuzRostro: React.FC<{ caras: CaraLuz[]; intensidad: number }> = ({ caras, intensidad }) => {
  const t = useCurrentFrame() / FPS;
  if (!caras.length) return null;
  const c = caras.reduce((a, b) => (Math.abs(b.t - t) < Math.abs(a.t - t) ? b : a));
  if (Math.abs(c.t - t) > 0.5) return null;
  const radio = Math.round(c.alto * 1920 * 0.9);
  return (
    <AbsoluteFill
      style={{
        mixBlendMode: "soft-light",
        opacity: intensidad,
        background: `radial-gradient(circle ${radio}px at ${c.cx * 100}% ${c.cy * 100}%, rgba(255,246,236,1) 0%, rgba(255,246,236,0.5) 45%, rgba(255,246,236,0) 100%)`,
      }}
    />
  );
};

export const Combinar: React.FC<CombinarProps> = (p) => {
  let inicio = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {p.clips.map((c, i) => {
        const desde = inicio;
        inicio += fotogramas(c);
        return (
          <Sequence key={i} from={desde} durationInFrames={fotogramas(c)}>
            <OffthreadVideo
              src={staticFile(c.video)}
              startFrom={Math.round(c.desde * FPS)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                filter: `contrast(${p.contraste}) saturate(${p.saturacion}) brightness(${p.brillo * (c.brillo ?? 1)})`,
              }}
            />
            {/* Igualar temperatura entre tomas */}
            {c.temperatura ? (
              <AbsoluteFill
                style={{
                  backgroundColor: c.temperatura > 0 ? "#ff9a4a" : "#4a86ff",
                  mixBlendMode: "soft-light",
                  opacity: Math.min(0.35, Math.abs(c.temperatura) * 0.3),
                }}
              />
            ) : null}
          </Sequence>
        );
      })}
      {p.luzRostro ? <LuzRostro caras={p.caras ?? []} intensidad={p.luzRostro} /> : null}
      <AbsoluteFill style={{ backgroundColor: "#1d4f5c", mixBlendMode: "soft-light", opacity: p.sombrasFrias }} />
      <AbsoluteFill style={{ backgroundColor: "#ffb36b", mixBlendMode: "overlay", opacity: p.lucesCalidas * 0.35 }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(0,0,0,${p.vineta}) 100%)` }} />
    </AbsoluteFill>
  );
};

export const metadatosCombinar: CalculateMetadataFunction<CombinarProps> = ({ props }) => ({
  durationInFrames: props.clips.reduce((n, c) => n + fotogramas(c), 0),
});

export const combinarEjemplo: CombinarProps = {
  clips: [
    { video: "fuentes/mi-reel/c1.mp4", desde: 0.45, hasta: 8.95 },
    { video: "fuentes/mi-reel/c2.mov", desde: 1.15, hasta: 12.4 },
    { video: "fuentes/mi-reel/c3.mov", desde: 0.5, hasta: 9.3 },
    { video: "fuentes/mi-reel/c4.mov", desde: 0.85, hasta: 9.9 },
  ],
  contraste: 1.08,
  saturacion: 0.84,
  brillo: 0.97,
  sombrasFrias: 0.22,
  lucesCalidas: 0.18,
  vineta: 0.32,
};
