import type React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { inter, montserrat } from "./fuentes";
import { MARCA } from "./marca";
import { useFuente } from "./Mascara";
import { Grafico, ItemLista, ReelProps, VERDE } from "./tipos";

const VERDE_CLARO = MARCA.acentoClaro;

// Entrada con resorte y salida rápida, comunes a todas las tarjetas.
const useAparicion = (g: Grafico) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - Math.round(g.s * fps);
  const entra = spring({ frame: local, fps, config: { damping: 15, stiffness: 170 } });
  const sale = interpolate(frame / fps, [g.e - 0.2, g.e], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { local, fps, entra, sale };
};

// A) "Si me comentás video, te digo cómo lo hice": palabra grande en verde que aparece entre las manos
const Comentario: React.FC<{ g: Grafico }> = ({ g }) => {
  const { local, fps, sale } = useAparicion(g);
  const pop = spring({ frame: local, fps, config: { damping: 9, stiffness: 210, mass: 0.7 } });
  const sub = spring({ frame: local - 5, fps, config: { damping: 14, stiffness: 180 } });
  return (
    <AbsoluteFill style={{ alignItems: "center", opacity: sale }}>
      <div style={{ position: "absolute", top: `${g.top ?? 50}%`, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div
          style={{
            fontFamily: montserrat,
            fontWeight: 800,
            fontSize: 64,
            color: "white",
            letterSpacing: -1,
            textShadow: "0 4px 22px rgba(0,0,0,0.55)",
            opacity: sub,
            translate: `0px ${interpolate(sub, [0, 1], [20, 0])}px`,
          }}
        >
          {g.arriba ?? "comentá"}
        </div>
        <div
          style={{
            fontFamily: montserrat,
            fontWeight: 800,
            fontSize: 210,
            lineHeight: 1,
            letterSpacing: -6,
            color: VERDE_CLARO,
            textShadow: "0 8px 40px rgba(0,0,0,0.45)",
            scale: String(interpolate(pop, [0, 1], [0.35, 1])),
            opacity: interpolate(pop, [0, 0.3], [0, 1], { extrapolateRight: "clamp" }),
            filter: `blur(${interpolate(pop, [0, 0.6], [12, 0], { extrapolateRight: "clamp" })}px)`,
          }}
        >
          {g.texto ?? "VIDEO"}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Entrada sobria para las notificaciones: fundido, leve subida y escala, sin rebote.
const useRefinado = (g: Grafico) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - Math.round(g.s * fps);
  const entra = interpolate(local, [0, 0.45 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const sale = interpolate(frame / fps, [g.e - 0.28, g.e], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.cubic) });
  return { local, fps, estilo: { opacity: entra * sale, translate: `0px ${(1 - entra) * 34 + (1 - sale) * 14}px`, scale: String(0.97 + 0.03 * entra) } };
};

// Panel de vidrio oscuro tipo notificación del sistema (debajo de la cara, no la tapa).
const Vidrio: React.FC<{ estilo: React.CSSProperties; children: React.ReactNode }> = ({ estilo, children }) => (
  <div
    style={{
      position: "absolute",
      left: 110,
      right: 110,
      top: "41%",
      borderRadius: 46,
      background: "linear-gradient(180deg, rgba(44,44,48,0.70), rgba(22,22,26,0.62))",
      border: "1.5px solid rgba(255,255,255,0.16)",
      boxShadow: "0 30px 70px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.10)",
      padding: "30px 34px",
      fontFamily: inter,
      color: "white",
      ...estilo,
    }}
  >
    {children}
  </div>
);

const Cabecera: React.FC<{ icono: React.ReactNode; app: string }> = ({ icono, app }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 22 }}>
    {icono}
    <div style={{ flex: 1, fontSize: 27, fontWeight: 500, letterSpacing: 1.5, textTransform: "uppercase", color: "rgba(255,255,255,0.62)" }}>{app}</div>
    <div style={{ fontSize: 26, color: "rgba(255,255,255,0.5)" }}>ahora</div>
  </div>
);

// B) "...para hablarle a mis familiares": notificación de un mensaje de voz
const Familia: React.FC<{ g: Grafico }> = ({ g }) => {
  const { local, fps, estilo } = useRefinado(g);
  const avance = interpolate(local, [0.35 * fps, 1.6 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const barras = [0.35, 0.6, 0.9, 0.5, 0.75, 1, 0.65, 0.4, 0.8, 0.55, 0.95, 0.45, 0.7, 0.3, 0.6, 0.85, 0.5, 0.35, 0.7, 0.4, 0.55, 0.3];
  return (
    <Vidrio estilo={estilo}>
      <Cabecera
        app="Mensajes"
        icono={
          <div style={{ width: 54, height: 54, borderRadius: 14, background: "linear-gradient(180deg,#5ef08a,#22b14c)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="white"><path d="M12 3C6.5 3 2 6.8 2 11.5c0 2.5 1.3 4.8 3.4 6.3L4.6 21l3.9-1.9c1.1.3 2.3.4 3.5.4 5.5 0 10-3.8 10-8.5S17.5 3 12 3z" /></svg>
          </div>
        }
      />
      <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <div style={{ width: 92, height: 92, borderRadius: 46, background: "linear-gradient(135deg,#f9a8d4,#c084fc)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, fontWeight: 700 }}>M</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 40, fontWeight: 700, marginBottom: 12 }}>Mamá</div>
          <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
            <svg width="30" height="30" viewBox="0 0 24 24" fill="rgba(255,255,255,0.9)"><path d="M8 5v14l11-7z" /></svg>
            <div style={{ display: "flex", alignItems: "center", gap: 5, height: 46, flex: 1 }}>
              {barras.map((h, i) => (
                <div key={i} style={{ width: 7, borderRadius: 4, height: 46 * h, background: i / barras.length < avance ? VERDE : "rgba(255,255,255,0.35)" }} />
              ))}
            </div>
            <div style={{ fontSize: 28, color: "rgba(255,255,255,0.6)", fontVariantNumeric: "tabular-nums" }}>0:{String(Math.round(avance * 12)).padStart(2, "0")}</div>
          </div>
        </div>
      </div>
    </Vidrio>
  );
};

// C) "O entrar a mi cuenta bancaria": verificación facial de una app bancaria
const Banco: React.FC<{ g: Grafico }> = ({ g }) => {
  const { local, fps, estilo } = useRefinado(g);
  const progreso = interpolate(local, [0.25 * fps, 1.15 * fps], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const ok = progreso >= 1;
  const check = spring({ frame: local - Math.round(1.15 * fps), fps, config: { damping: 14, stiffness: 200 } });
  const marcas = 48;
  // Malla de puntos del rostro (estilo reconocimiento facial)
  const puntos: [number, number][] = [];
  for (let fy = -3; fy <= 3; fy++) {
    const ancho = Math.round(4 - Math.abs(fy) * 0.6);
    for (let fx = -ancho; fx <= ancho; fx++) puntos.push([fx * 11, fy * 14]);
  }
  return (
    <Vidrio estilo={estilo}>
      <Cabecera
        app="Banca móvil"
        icono={
          <div style={{ width: 54, height: 54, borderRadius: 14, background: "linear-gradient(180deg,#3b82f6,#1e40af)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 10l9-6 9 6M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18" /></svg>
          </div>
        }
      />
      <div style={{ display: "flex", alignItems: "center", gap: 36 }}>
        <svg width="200" height="200" viewBox="-100 -100 200 200">
          {Array.from({ length: marcas }).map((_, i) => {
            const a = (i / marcas) * Math.PI * 2 - Math.PI / 2;
            const on = i / marcas < progreso;
            return (
              <line key={i} x1={Math.cos(a) * 80} y1={Math.sin(a) * 80} x2={Math.cos(a) * 94} y2={Math.sin(a) * 94} stroke={on ? VERDE : "rgba(255,255,255,0.22)"} strokeWidth="5" strokeLinecap="round" />
            );
          })}
          {!ok &&
            puntos.map(([x, y], i) => (
              <circle key={i} cx={x} cy={y - 4} r="2.6" fill="white" opacity={0.25 + 0.6 * Math.abs(Math.sin(local / 5 + i * 0.7)) * (1 - progreso * 0.4)} />
            ))}
          {ok && (
            <path d="M-30 2 L-8 24 L32 -20" fill="none" stroke={VERDE} strokeWidth="11" strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - check} />
          )}
        </svg>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 40, fontWeight: 700, marginBottom: 10 }}>{ok ? "Identidad verificada" : "Verificando identidad"}</div>
          <div style={{ fontSize: 30, color: "rgba(255,255,255,0.62)", marginBottom: 22 }}>{ok ? "Acceso concedido" : `Reconocimiento facial · ${Math.round(progreso * 100)}%`}</div>
          <div style={{ display: "flex", alignItems: "center", gap: 14, fontSize: 28, color: "rgba(255,255,255,0.8)", opacity: ok ? check : 0.35 }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={ok ? VERDE : "white"} strokeWidth="2.2" strokeLinecap="round"><rect x="4" y="11" width="16" height="10" rx="2.5" /><path d="M8 11V7a4 4 0 0 1 7.5-2" /></svg>
            Cuenta •••• 4821
          </div>
        </div>
      </div>
    </Vidrio>
  );
};

// Ícono genérico de cámara con degradado (estilo Instagram)
const IconoInstagram: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 48 48">
    <defs>
      <linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">
        <stop offset="0" stopColor="#FEDA75" />
        <stop offset="0.3" stopColor="#FA7E1E" />
        <stop offset="0.6" stopColor="#D62976" />
        <stop offset="1" stopColor="#4F5BD5" />
      </linearGradient>
    </defs>
    <rect x="4" y="4" width="40" height="40" rx="12" fill="none" stroke="url(#ig)" strokeWidth="4.5" />
    <circle cx="24" cy="24" r="9" fill="none" stroke="url(#ig)" strokeWidth="4.5" />
    <circle cx="35" cy="13" r="2.8" fill="url(#ig)" />
  </svg>
);

// D) "Seguí a @marca" (señala arriba a la izquierda): caja flotante blanca
const Seguir: React.FC<{ g: Grafico }> = ({ g }) => {
  const { local, entra, sale } = useAparicion(g);
  const flota = Math.sin(local / 11) * 8;
  return (
    <div
      style={{
        position: "absolute",
        left: 110,
        top: "12%",
        display: "flex",
        alignItems: "center",
        gap: 30,
        background: "linear-gradient(180deg,#ffffff,#f1f1f1)",
        borderRadius: 999,
        padding: "34px 64px 34px 46px",
        boxShadow: "0 24px 60px rgba(0,0,0,0.30)",
        fontFamily: inter,
        opacity: sale * interpolate(entra, [0, 0.4], [0, 1], { extrapolateRight: "clamp" }),
        scale: String(interpolate(entra, [0, 1], [0.5, 1])),
        translate: `0px ${interpolate(entra, [0, 1], [60, 0]) + flota}px`,
        filter: `blur(${interpolate(entra, [0, 0.5], [8, 0], { extrapolateRight: "clamp" })}px)`,
      }}
    >
      <IconoInstagram size={92} />
      <div style={{ fontSize: 76, fontWeight: 700, color: "#6b6b6b", letterSpacing: -1 }}>{g.texto ?? MARCA.usuario}</div>
    </div>
  );
};

// "Las empresas, como los bancos, los seguros y todos los que te piden tu biometría y tu identidad":
// arriba las EMPRESAS (chips que aparecen al nombrarlas), una línea "te piden" que baja y abajo los DATOS
// que piden (biometría, identidad) en verde. Con "no están listas", las empresas se tiñen de rojo apagado.
// Va debajo de los captions, nunca sobre la cara.
const iconos: Record<string, React.ReactNode> = {
  banco: <path d="M3 10l9-6 9 6M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18" />,
  escudo: <path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" />,
  edificio: <path d="M5 21V5l7-2v18M12 7l7 2v12M8 8v.01M8 12v.01M8 16v.01M15.5 12v.01M15.5 16v.01M3 21h18" />,
  huella: (
    <>
      <path d="M12 11v3a6 6 0 0 1-1.5 4" />
      <path d="M8.5 9.5A4 4 0 0 1 16 11v2.5a10 10 0 0 1-1 4.5" />
      <path d="M5.5 8.5A7 7 0 0 1 19 11v1.5" />
      <path d="M8 13a10 10 0 0 1-1 5" />
    </>
  ),
  identidad: (
    <>
      <rect x="3" y="5" width="18" height="14" rx="2.5" />
      <circle cx="9" cy="11" r="2.2" />
      <path d="M5.8 16c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4M14.5 10h4M14.5 13.5h3" />
    </>
  ),
};

const Chip: React.FC<{ it: ItemLista; t: number; rojo: number; datos: boolean }> = ({ it, t, rojo, datos }) => {
  const entra = interpolate(t, [it.s, it.s + 0.4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.bezier(0.16, 1, 0.3, 1) });
  const k = datos ? 0 : rojo;
  const icono = datos ? VERDE : `rgb(${Math.round(200 + 40 * k)}, ${Math.round(205 - 125 * k)}, ${Math.round(212 - 132 * k)})`;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "15px 24px 15px 18px",
        borderRadius: 999,
        background: datos
          ? "linear-gradient(180deg, rgba(30,70,44,0.72), rgba(18,40,26,0.66))"
          : "linear-gradient(180deg, rgba(44,44,48,0.70), rgba(22,22,26,0.62))",
        border: datos
          ? "1.5px solid rgba(92,222,120,0.45)"
          : `1.5px solid rgba(${Math.round(255 - 15 * k)},${Math.round(255 - 175 * k)},${Math.round(255 - 175 * k)},${0.16 + 0.3 * k})`,
        boxShadow: "0 18px 44px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.10)",
        opacity: entra * (1 - 0.3 * k),
        translate: `0px ${(1 - entra) * 22}px`,
      }}
    >
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={icono} strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
        {iconos[it.icono]}
      </svg>
      <div style={{ fontSize: 33, fontWeight: 600, color: "white", letterSpacing: -0.5 }}>{it.texto}</div>
    </div>
  );
};

const Lista: React.FC<{ g: Grafico }> = ({ g }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const sale = interpolate(t, [g.e - 0.3, g.e], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const rojo = g.alerta === undefined ? 0 : interpolate(t, [g.alerta, g.alerta + 0.35], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const items = g.items ?? [];
  const empresas = items.filter((i) => i.grupo !== "datos");
  const datos = items.filter((i) => i.grupo === "datos");
  const primero = (lista: ItemLista[]) => (lista.length ? lista[0].s : 1e9);
  const etiqueta = (texto: string, s: number, color: string) => (
    <div
      style={{
        fontSize: 22,
        fontWeight: 700,
        letterSpacing: 4,
        textTransform: "uppercase",
        color,
        opacity: interpolate(t, [s, s + 0.4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }}
    >
      {texto}
    </div>
  );
  const con = g.conector;
  const baja = con ? interpolate(t, [con.s, con.s + 0.45], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : 0;
  return (
    <div
      style={{
        position: "absolute",
        left: 40,
        right: 40,
        top: `${g.top ?? 71.5}%`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 12,
        opacity: sale,
        fontFamily: inter,
      }}
    >
      {etiqueta("Empresas", primero(empresas), `rgba(255,${Math.round(255 - 150 * rojo)},${Math.round(255 - 150 * rojo)},0.7)`)}
      <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
        {empresas.map((it, i) => (
          <Chip key={i} it={it} t={t} rojo={rojo} datos={false} />
        ))}
      </div>
      {con && (
        <div style={{ display: "flex", alignItems: "center", gap: 14, height: 46 }}>
          <div style={{ width: 2, height: 40 * baja, background: "rgba(255,255,255,0.45)", borderRadius: 1 }} />
          <div style={{ fontSize: 26, fontWeight: 500, fontStyle: "italic", color: "rgba(255,255,255,0.75)", opacity: baja }}>{con.texto}</div>
        </div>
      )}
      <div style={{ display: "flex", gap: 14, justifyContent: "center" }}>
        {datos.map((it, i) => (
          <Chip key={i} it={it} t={t} rojo={rojo} datos />
        ))}
      </div>
    </div>
  );
};

// Etiqueta discreta (p. ej. "Este no soy yo" sobre la parte hecha con IA): vidrio oscuro con punto rojo que late.
const Etiqueta: React.FC<{ g: Grafico }> = ({ g }) => {
  const { local, fps, estilo } = useRefinado(g);
  const pulso = 0.55 + 0.45 * Math.abs(Math.sin((local / fps) * Math.PI * 1.2));
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: `${g.top ?? 9.5}%`, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          padding: "16px 30px 16px 24px",
          borderRadius: 999,
          background: "linear-gradient(180deg, rgba(44,44,48,0.72), rgba(22,22,26,0.64))",
          border: "1.5px solid rgba(255,255,255,0.16)",
          boxShadow: "0 18px 44px rgba(0,0,0,0.30), inset 0 1px 0 rgba(255,255,255,0.10)",
          fontFamily: inter,
          ...estilo,
        }}
      >
        <div style={{ width: 16, height: 16, borderRadius: 8, background: "#ff4d4f", opacity: pulso, boxShadow: "0 0 14px rgba(255,77,79,0.8)" }} />
        <div style={{ fontSize: 36, fontWeight: 600, color: "white", letterSpacing: -0.3 }}>{g.texto}</div>
      </div>
    </div>
  );
};

// Escaneo biométrico sobre la cara (sigue la cara detectada y el zoom del corte): esquinas, línea de escaneo
// y una malla de puntos que se va completando; al final, "Biometría capturada". Trazos opacos y finos.
const Escaneo: React.FC<{ g: Grafico; p: ReelProps }> = ({ g, p }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const { src, escala } = useFuente(p.tramos ?? [{ t: 0, d: 1e9, src: t, escala: 1 }]);
  const caras = p.caras ?? [];
  if (!caras.length) return null;
  const c = caras.reduce((a, b) => (Math.abs(b.t - src) < Math.abs(a.t - src) ? b : a));
  const z = (v: number) => 0.5 + (v - 0.5) * escala;
  const W = 1080, H = 1920;
  const x0 = z(c.x0) * W, x1 = z(c.x1) * W, y0 = z(c.arriba) * H, y1 = z(c.abajo) * H;
  const mx = (x1 - x0) * 0.12, my = (y1 - y0) * 0.1;
  const L = { x0: x0 - mx, x1: x1 + mx, y0: y0 - my, y1: y1 + my };
  const local = t - g.s;
  const dur = g.e - g.s;
  const entra = interpolate(local, [0, 0.25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sale = interpolate(local, [dur - 0.25, dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  // el escaneo ocupa ~70 % del tiempo y el resto muestra "capturada" (dura lo que dura la palabra)
  const barrido = interpolate(local, [0.1, dur * 0.7], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
  const listo = local > dur * 0.72;
  const brazo = Math.min(L.x1 - L.x0, L.y1 - L.y0) * 0.22;
  const esquina = (x: number, y: number, dx: number, dy: number) => `M ${x + dx * brazo} ${y} L ${x} ${y} L ${x} ${y + dy * brazo}`;
  const puntos: [number, number][] = [];
  const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = (x1 - x0) / 2, ry = (y1 - y0) / 2;
  for (let i = -5; i <= 5; i++) for (let j = -6; j <= 6; j++) {
    const px = cx + (i / 5.5) * rx * 0.9, py = cy + (j / 6.5) * ry * 0.95;
    if (((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 0.8) puntos.push([px, py]);
  }
  const lineaY = L.y0 + (L.y1 - L.y0) * barrido;
  return (
    <AbsoluteFill style={{ opacity: entra * sale }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ position: "absolute", inset: 0 }}>
        <g fill="none" stroke={VERDE} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round">
          <path d={esquina(L.x0, L.y0, 1, 1)} />
          <path d={esquina(L.x1, L.y0, -1, 1)} />
          <path d={esquina(L.x0, L.y1, 1, -1)} />
          <path d={esquina(L.x1, L.y1, -1, -1)} />
        </g>
        {puntos.map(([px, py], i) =>
          py <= lineaY ? <circle key={i} cx={px} cy={py} r={3.2} fill={VERDE} opacity={listo ? 0.55 : 0.9} /> : null,
        )}
        {!listo && <rect x={L.x0 + 10} y={lineaY - 2} width={L.x1 - L.x0 - 20} height={4} rx={2} fill={VERDE} />}
      </svg>
      <div
        style={{
          position: "absolute",
          left: L.x0,
          width: L.x1 - L.x0,
          top: L.y0 - 74,
          display: "flex",
          justifyContent: "center",
          fontFamily: inter,
        }}
      >
        <div
          style={{
            padding: "10px 22px",
            borderRadius: 999,
            background: "rgba(14,22,16,0.82)",
            border: `2px solid ${VERDE}`,
            color: "white",
            fontSize: 28,
            fontWeight: 600,
            whiteSpace: "nowrap",
          }}
        >
          {listo ? "Biometría capturada ✓" : `Escaneando rostro · ${Math.round(barrido * 100)}%`}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Cédula de identidad (arriba de la cabeza, o al costado si se pide), estilo documento realista en vidrio oscuro.
const Cedula: React.FC<{ g: Grafico }> = ({ g }) => {
  const { local, fps, estilo } = useRefinado(g);
  const brillo = interpolate(local, [0.3 * fps, 1.1 * fps], [-0.4, 1.4], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const izquierda = g.lado === "izquierda";
  const centro = g.lado === "centro";
  const linea = (w: number, op = 0.75) => <div style={{ height: 9, width: w, borderRadius: 5, background: `rgba(255,255,255,${op})` }} />;
  return (
    <div
      style={{
        position: "absolute",
        top: `${g.top ?? 40}%`,
        ...(centro ? { left: (1080 - 330) / 2 } : izquierda ? { left: 18 } : { right: 18 }),
        width: 330,
        transformOrigin: centro ? "center top" : izquierda ? "left top" : "right top",
        borderRadius: 26,
        overflow: "hidden",
        background: "linear-gradient(160deg, rgba(40,58,72,0.92), rgba(18,26,34,0.92))",
        border: "1.5px solid rgba(255,255,255,0.22)",
        boxShadow: "0 24px 60px rgba(0,0,0,0.40)",
        fontFamily: inter,
        color: "white",
        ...estilo,
        scale: String((centro ? 0.7 : 0.82) * Number(estilo.scale)), // más chica para no rozar la cara/pelo
      }}
    >
      <div style={{ padding: "16px 20px 10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: 2.4, color: "rgba(255,255,255,0.8)" }}>CÉDULA DE IDENTIDAD</div>
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke={VERDE} strokeWidth="2.2" strokeLinecap="round"><path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" /><path d="M8.5 12.5l2.4 2.4 4.6-4.8" /></svg>
      </div>
      <div style={{ display: "flex", gap: 16, padding: "4px 20px 14px" }}>
        <div style={{ width: 92, height: 112, borderRadius: 12, background: "linear-gradient(180deg,#4b6070,#2b3a46)", display: "flex", alignItems: "flex-end", justifyContent: "center", overflow: "hidden" }}>
          <svg width="80" height="96" viewBox="0 0 80 96"><circle cx="40" cy="36" r="18" fill="rgba(255,255,255,0.55)" /><path d="M8 96c2-22 16-32 32-32s30 10 32 32z" fill="rgba(255,255,255,0.55)" /></svg>
        </div>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 11, paddingTop: 8 }}>
          {linea(150)}
          {linea(110, 0.5)}
          {linea(130, 0.5)}
          <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
            <div style={{ width: 34, height: 26, borderRadius: 5, background: "linear-gradient(135deg,#e9d38a,#b4913f)" }} />
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.6" strokeLinecap="round"><path d="M12 11v3a6 6 0 0 1-1.5 4" /><path d="M8.5 9.5A4 4 0 0 1 16 11v2.5a10 10 0 0 1-1 4.5" /><path d="M5.5 8.5A7 7 0 0 1 19 11v1.5" /></svg>
          </div>
        </div>
      </div>
      <div style={{ padding: "8px 20px 14px", fontFamily: "monospace", fontSize: 15, letterSpacing: 1.5, color: "rgba(255,255,255,0.55)", background: "rgba(0,0,0,0.18)" }}>
        IDARG&lt;&lt;••••••••&lt;&lt;&lt;&lt;&lt;&lt;
        <br />
        ••••••••&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;&lt;
      </div>
      {/* Reflejo que cruza la tarjeta */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(115deg, transparent ${(brillo - 0.15) * 100}%, rgba(255,255,255,0.16) ${brillo * 100}%, transparent ${(brillo + 0.15) * 100}%)`,
        }}
      />
    </div>
  );
};

export const Graficos: React.FC<{ graficos: Grafico[]; p: ReelProps }> = ({ graficos, p }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  return (
    <AbsoluteFill>
      {graficos
        .filter((g) => t >= g.s && t < g.e)
        .map((g, i) =>
          g.tipo === "comentario" ? <Comentario key={i} g={g} /> : g.tipo === "familia" ? <Familia key={i} g={g} /> : g.tipo === "banco" ? <Banco key={i} g={g} /> : g.tipo === "lista" ? <Lista key={i} g={g} /> : g.tipo === "etiqueta" ? <Etiqueta key={i} g={g} /> : g.tipo === "escaneo" ? <Escaneo key={i} g={g} p={p} /> : g.tipo === "cedula" ? <Cedula key={i} g={g} /> : <Seguir key={i} g={g} />,
        )}
    </AbsoluteFill>
  );
};
