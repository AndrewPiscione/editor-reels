// Datos que genera herramientas/armar_reel.py (tiempos ya en la línea de tiempo del reel, en segundos).

// top: altura en % (debajo de la cara, la calcula el script); clave: palabras de la frase que se resaltan
export type Caption = {
  s: number;
  e: number;
  texto: string;
  resaltar: boolean;
  top?: number;
  clave?: string[];
  detras?: boolean; // palabra clave grande detrás de la cabeza (va en la capa "detrás")
};

export type Destacado = {
  s: number;
  e: number;
  // "titulo" / "titulo-verde": estilo portada (Montserrat Black itálica); "desde" = segundos tras el inicio
  lineas: { texto: string; estilo: "bold" | "italic" | "titulo" | "titulo-verde"; desde?: number }[];
  top: number; // porcentaje desde arriba del lienzo
  recortar?: boolean; // false: no pasa por la máscara de persona (p. ej. el título del gancho)
  escala?: number; // < 1 si hay que achicarlo para que entre arriba de la cabeza
};

// grupo "empresas" (quiénes piden) o "datos" (qué piden)
export type ItemLista = { texto: string; icono: "banco" | "escudo" | "edificio" | "huella" | "identidad"; s: number; grupo?: "empresas" | "datos" };

export type Grafico = {
  tipo: "comentario" | "familia" | "banco" | "seguir" | "lista" | "etiqueta" | "escaneo" | "cedula";
  lado?: "izquierda" | "derecha" | "centro"; // "cedula": dónde va respecto de la cara
  top?: number; // altura en % calculada por el script (p. ej. debajo de la cara)
  s: number;
  e: number;
  // "comentario": palabra grande (por defecto "VIDEO") y texto chico de arriba (por defecto "comentá")
  texto?: string;
  arriba?: string;
  // "lista": chips que aparecen en su tiempo; desde "alerta" se tiñen de rojo (algo no está preparado)
  items?: ItemLista[];
  alerta?: number;
  conector?: { texto: string; s: number }; // "te piden": une empresas con datos
};

export type Transicion = { s: number; e: number; corte: number; intensidad?: number; destello?: boolean };

export type ReelProps = {
  duracion: number;
  captions: Caption[];
  ocultarCaptions: [number, number][];
  destacados: Destacado[];
  graficos: Grafico[];
  transiciones: Transicion[];
  // Fundido cruzado hacia la firma: entre s y e se va mostrando la firma encima (CapCut sigue con la firma en e)
  fundidoFinal?: { s: number; e: number; video: string };
  // Tramos del reel (para saber qué fotograma de la fuente y qué zoom hay en cada instante)
  tramos?: { t: number; d: number; src: number; escala: number }[];
  // Máscaras de persona por fotograma de la fuente (herramientas/personas)
  mascara?: { carpeta: string; fps: number; total?: number };
  // Cara detectada en la fuente (herramientas/caras): para gráficos que siguen la cara
  caras?: { t: number; arriba: number; abajo: number; x0: number; x1: number }[];
};

import { MARCA } from "./marca";

// Color de acento de la marca (ver marca.ts)
export const VERDE = MARCA.acento;
