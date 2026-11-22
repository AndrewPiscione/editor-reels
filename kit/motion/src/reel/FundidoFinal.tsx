import type React from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ReelProps } from "./tipos";

// Transparencia cruzada entre los últimos fotogramas del video y la firma sonora (fondo negro).
// La firma va centrada como en CapCut (1080x1350 dentro de 1080x1920, resto negro).
export const FundidoFinal: React.FC<{ f: NonNullable<ReelProps["fundidoFinal"]> }> = ({ f }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacidad = interpolate(frame / fps, [f.s, f.e], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <Sequence from={Math.round(f.s * fps)}>
      <AbsoluteFill style={{ backgroundColor: "black", opacity: opacidad, justifyContent: "center" }}>
        <OffthreadVideo src={staticFile(f.video)} muted style={{ width: 1080, height: 1350 }} />
      </AbsoluteFill>
    </Sequence>
  );
};
