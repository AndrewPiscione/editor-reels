import { Composition } from "remotion";
import { metadatosReel, propsEjemplo, ReelDelante, ReelDetras } from "./reel/Reel";
import { VistaPrevia } from "./reel/VistaPrevia";
import { Gradeo, gradeoEjemplo, metadatosGradeo } from "./reel/Gradeo";
import { Combinar, combinarEjemplo, metadatosCombinar } from "./reel/Combinar";
import { Hoja } from "./reel/Hoja";

// Composiciones del editor de reels:
// - ReelDelante / ReelDetras: las dos capas transparentes (captions, gráficos, textos detrás de la persona)
// - Combinar: une los clips en orden + color + igualar tomas + luz de rostro
// - Gradeo: color sobre una sola toma
// - VistaPrevia: un fotograma del video con las capas encima (para revisar)
// - Hoja: hoja de contacto con guías de altura
export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="ReelDelante" component={ReelDelante} fps={30} width={1080} height={1920} defaultProps={propsEjemplo} calculateMetadata={metadatosReel} />
      <Composition id="ReelDetras" component={ReelDetras} fps={30} width={1080} height={1920} defaultProps={propsEjemplo} calculateMetadata={metadatosReel} />
      <Composition
        id="VistaPrevia"
        component={VistaPrevia}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ ...propsEjemplo, fondo: "vista-previa/fondo.jpg", escala: 1 }}
        calculateMetadata={({ props }) => ({ durationInFrames: Math.max(1, Math.round(props.duracion * 30)) })}
      />
      <Composition id="Gradeo" component={Gradeo} fps={30} width={1080} height={1920} defaultProps={gradeoEjemplo} calculateMetadata={metadatosGradeo} />
      <Composition id="Combinar" component={Combinar} fps={30} width={1080} height={1920} defaultProps={combinarEjemplo} calculateMetadata={metadatosCombinar} />
      <Composition id="Hoja" component={Hoja} durationInFrames={1} fps={30} width={1512} height={1152} defaultProps={{ imagenes: [], etiquetas: [] }} />
    </>
  );
};
