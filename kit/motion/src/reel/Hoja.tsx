import type React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";

// Solo para revisar: hoja de contacto con fotogramas y su tiempo, con líneas guía de altura (cada 10 %).
export const Hoja: React.FC<{ imagenes: string[]; etiquetas: string[] }> = ({ imagenes, etiquetas }) => (
  <AbsoluteFill style={{ backgroundColor: "#111", flexDirection: "row", flexWrap: "wrap", alignContent: "flex-start" }}>
    {imagenes.map((src, i) => (
      <div key={i} style={{ position: "relative", width: 216, height: 384, border: "1px solid #000" }}>
        <Img src={staticFile(src)} style={{ width: 216, height: 384 }} />
        {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((k) => (
          <div key={k} style={{ position: "absolute", left: 0, right: 0, top: k * 38.4, borderTop: "1px solid rgba(255,0,0,0.55)" }}>
            <span style={{ color: "red", fontSize: 11, fontFamily: "monospace" }}>{k * 10}</span>
          </div>
        ))}
        <div style={{ position: "absolute", bottom: 2, right: 4, color: "yellow", fontSize: 16, fontFamily: "monospace" }}>{etiquetas[i]}</div>
      </div>
    ))}
  </AbsoluteFill>
);
