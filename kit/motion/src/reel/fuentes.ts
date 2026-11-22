import { loadFont as loadMontserrat } from "@remotion/google-fonts/Montserrat";
import { loadFont as loadOpenSans } from "@remotion/google-fonts/OpenSans";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadInstrumentSerif } from "@remotion/google-fonts/InstrumentSerif";

export const montserrat = loadMontserrat("normal", {
  weights: ["700", "800"],
  subsets: ["latin", "latin-ext"],
}).fontFamily;

loadMontserrat("italic", { weights: ["900"], subsets: ["latin", "latin-ext"] });

export const openSans = loadOpenSans("normal", {
  weights: ["800"],
  subsets: ["latin", "latin-ext"],
}).fontFamily;
loadOpenSans("italic", { weights: ["300"], subsets: ["latin", "latin-ext"] });

export const inter = loadInter("normal", {
  weights: ["500", "600", "700"],
  subsets: ["latin", "latin-ext"],
}).fontFamily;

// Serif editorial para resaltar palabras clave en los captions
export const instrumentSerif = loadInstrumentSerif("italic", { weights: ["400"], subsets: ["latin", "latin-ext"] }).fontFamily;
