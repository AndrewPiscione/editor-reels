import type React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { Transicion } from "./tipos";

// Transición de suspenso: el borde se oscurece poco a poco hasta el corte y vuelve a la normalidad.
// El destello en el corte es opcional (solo el gancho): en el resto quita seriedad.
export const Transiciones: React.FC<{ transiciones: Transicion[] }> = ({ transiciones }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const tr = transiciones.find((x) => t >= x.s && t < x.e);
  if (!tr) return null;
  const sube = interpolate(t, [tr.s, tr.corte], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.quad) });
  const baja = interpolate(t, [tr.corte, tr.e], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const k = (t < tr.corte ? sube : baja) * (tr.intensidad ?? 1);
  const destello = !tr.destello ? 0 : interpolate(t, [tr.corte, tr.corte + 2 / fps, tr.corte + 6 / fps], [0, 0.18, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) ${62 - 30 * k}%, rgba(0,0,0,${0.85 * k}) 100%)` }} />
      <AbsoluteFill style={{ backgroundColor: `rgba(0,0,0,${0.28 * k})` }} />
      <AbsoluteFill style={{ backgroundColor: `rgba(255,255,255,${destello})` }} />
    </AbsoluteFill>
  );
};
