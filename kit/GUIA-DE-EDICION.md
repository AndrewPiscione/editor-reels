# Guía de edición de reels

Criterio de editor profesional aprendido en reels reales (16 versiones revisadas por un editor exigente).
La marca, los colores, el idioma y las reglas de cada persona están en `marca/perfil.md`: **leerlo también**.
**Leer completa antes de editar cualquier video.** El objetivo es editar como un editor profesional por
criterio propio: que la primera versión ya salga cerca de la final y cada reel necesite menos correcciones.
Si el usuario corrige algo nuevo, añadirlo aquí (si es de su marca o gusto, en `marca/perfil.md`) y, si se puede
comprobar, también a `revisar_reel.py`.

---

## 0. Cómo edito un reel de principio a fin (proceso de decisión)

1. **Mirar todo el material antes de cortar nada.** Hoja de contacto de cada clip (composición `Hoja`, con guías de
   altura) + transcripción. Preguntas: ¿qué cuenta la historia?, ¿qué tomas se muestran sin hablar (pantallas,
   objetos, gestos) y deben quedar?, ¿dónde hay trabas o repeticiones?, ¿dónde cambia la escena o el plano?
2. **Escribir el recorrido emocional** en el brief (`_recorrido_emocional`): gancho → intriga → choque → silencio →
   amenaza → lo más grave → salida. Cada efecto que agregue tiene que tener un "porque" en esa lista.
3. **Preparar la fuente:** unir clips (`Combinar`), igualar luz entre tomas, color, luz de rostro, voz (`voz.py`).
   Después medir sobre esa fuente final: cara (`herramientas/caras`), silueta (`herramientas/personas`),
   transcripción palabra por palabra (corregir cómo habla la persona y los nombres propios de `marca/perfil.md`).
4. **Decidir efectos con moderación** (ver 7b): 1 gancho, 2–3 destacados, 2–4 palabras con layering separadas ≥4 s,
   1 gráfico por idea concreta (lo que dura la frase), transición sutil en cada cambio fuerte de escena,
   1 riser con remate, música solo si la historia la pide.
5. **Ubicar según la cara real:** captions debajo del mentón o arriba de la cabeza (una altura por toma), gráficos
   donde no tapen la cara, layering que sale desde detrás y termina arriba de la cabeza.
6. **Verificar antes de entregar:** `armar_reel.py --solo-datos` → `revisar_reel.py` (0 errores) → vistas previas de
   los momentos clave **mirándolas de verdad** → render de capas → revisar un fotograma de cada capa exportada →
   armar en CapCut → `lint` y `diagnose` → respaldo.
7. **Entregar** con la tabla "pedido → qué hice", lo que no pude comprobar y una sola acción para el usuario.

---

## 1. Principio rector: la historia manda

Antes de tocar un efecto, leer la transcripción y escribir en el brief el **recorrido emocional**
del video. Cada efecto, sonido, zoom o silencio tiene que servir a un momento concreto de la historia.
El video es una montaña rusa de emociones que mantiene la atención visual y auditiva hasta el final.

Recorrido típico de un reel informativo de tono serio (ej.: identidad, fraude, IA, seguridad):

| Fase | Qué siente el espectador | Recursos |
|---|---|---|
| Gancho (0–3 s) | Curiosidad, "tengo que ver esto" | Título que aparece progresivamente; último fotograma = portada |
| Intriga | "¿Qué está pasando?" | Microzooms, transiciones sutiles en cambios de escena, riser lento |
| Choque | Golpe | El riser termina en un impacto fuerte y alarmante + zoom brusco |
| Miedo | Inquietud | **Silencio** después del golpe (pesa más que otro sonido) |
| Amenaza creciente | Tensión | Música de tensión grave, latido que crece, golpes "chan" en palabras clave, zoom que se va cerrando |
| Lo más grave | Seriedad | Zoom más cerrado (≈130 %), golpe/alarma grave, bordes oscurecidos, **música atenuada** |
| Salida | Alivio, confianza en la marca | Beat sobrio y seguro; caja de "seguir" cuando señala; fundido al cierre de marca |

Reglas:
- Todo riser necesita un **remate** (impacto, escalofrío). Un riser sin conclusión se siente incompleto.
- No acumular efectos: el exceso le quita seriedad y tensión. Menos es más.
- Pensar en la lógica de lo que dice: "perder la identidad" es lo más grave → tratamiento más serio.

## 2. Tono: serio, estético, profesional

Si el tema es serio (fraude, salud, finanzas…), **nunca** caricaturesco, juguetón ni infantil. El tono de cada marca
está en `marca/perfil.md`.

Rechazado por el editor en reels reales (no repetir salvo que el perfil diga lo contrario):
- Flashes de luz en las transiciones (solo se aceptó uno en el corte del gancho).
- Tarjetas que entran de costado e inclinadas, con rebote.
- Pops repetidos (pop.wav en todo); pops en el título del gancho.
- Tarjetas blancas opacas que tapan la cara; gráficos "básicos".
- Gráficos genéricos que no vienen al caso (la credencial que se convertía en un check).
- Música de cierre con arpegios tipo arpa o alegre/infantil.
- Captions con estilo pobre (fuente por defecto de CapCut, resaltados que parecen otro caption).
- Cortar demasiado: perder las pausas naturales.
- Motion graphics encima de la cabeza en los últimos fotogramas.

## 3. Cortes y ritmo

- Cortes por silencios **por zonas** del original (ver brief):
  - Partes con efectos de IA o momentos de impacto: **no cortar pausas** (dan naturalidad y tensión).
  - Parte dramática: conservar pausas, ritmo menos acelerado.
  - Partes explicativas normales: cortar solo pausas > 0,5 s, con margen ≈ 0,15–0,18 s.
- Tramos largos se parten en el inicio de una palabra (corte invisible) para cambiar el encuadre.

## 4. Microzooms

- Cambio de encuadre en cada corte, bien visible: 100 / 106 / 114 / 122 %. Dos cortes seguidos nunca iguales.
- Parte dramática: zoom progresivo que se va cerrando (100 → 125 %).
- Golpes dramáticos ("o peor"): zoom brusco ≈125 %. Frase más grave: ≈130 %.
- Zoom desde el centro **sin desplazamiento** (`zoom.compensar: false`): así la posición de la cara es predecible
  y los captions/gráficos se ubican bien con la cara detectada.
- **Técnico:** CapCut 9.6 guarda pero NO muestra los fotogramas clave de escala de capcut-cli; usar escala fija por segmento.

## 5. Gancho y portada

- Título corto derivado de lo que dice (no inventar hechos), p. ej. "¿REAL / O IA?".
- Estilo portada: Montserrat Black itálica, mayúsculas, línea blanca + línea en el color de acento de la marca.
- Las líneas aparecen una a una; el último fotograma del gancho (antes de la transición) es la portada.
- Texto dentro de la zona segura del recorte 3:4 de la cuadrícula de Instagram (y 240–1680 px en 1080×1920),
  sin tapar la cara, sin captions en ese momento. Exportar la portada a `finales/portada_vNN.jpg`.
- Si el video empieza con algo llamativo (escena de IA), usarlo como fondo del gancho.

## 6. Captions

- **Nunca sobre la cara ni la boca.** Detectar la cara fotograma a fotograma con `herramientas/caras`
  (Vision de macOS) sobre la fuente final; el script usa el peor caso de cada caption, con el zoom del corte.
  **Una sola altura por toma** (sin saltos): debajo del mentón si entra en toda la toma; si no, arriba de la cabeza.
  Si la toma cambia de plano a mitad de clip (se aleja), indicarlo en `captions.cambios_de_plano`.
- Zoom sin desplazamiento (`zoom.compensar: false`) para que la posición de la cara sea exacta.
- Estilo: **un solo caption limpio y legible**. Montserrat Bold 74 px blanco; palabra clave en Montserrat
  ExtraBold acento suave, un poco más grande; entrada suave (crece levemente), sombra corta.
- **Layering:** las palabras clave van **grandes, en mayúsculas**, salen desde detrás de la cabeza y terminan
  arriba de ella (ver 7b). Se hace **en Remotion** con la máscara de persona de macOS (`herramientas/personas` → `motion/public/mascaras/<reel>`,
  brief `mascara_remotion` + `personas_archivo`), aplicando el zoom de cada corte. **No usar el recorte de CapCut**
  (`matting`): en CapCut 9.6 la copia tapaba todo. Verificar en la vista previa y en un fotograma de la capa exportada.
  No usar layering cuando arriba ya hay un destacado, la etiqueta, la caja de seguir, el escaneo o la cédula.
- **Al ritmo de la voz:** Whisper a veces ubica palabras dentro de un silencio. Ningún caption se muestra en un
  silencio: si la palabra está al inicio del silencio se adelanta; si está al final, espera a que empiece a hablar.
  Captions de menos de 0,2 s se unen al siguiente.
- **Rechazado (caso real):** contorno grande de fondo + serif con brillo verde → "un mamarracho", ilegible.
  En CapCut los efectos semitransparentes grandes (brillos, contornos finos translúcidos) se ven gruesos y sucios:
  evitarlos en las capas de Remotion.
- 1–2 palabras a la vez, minúsculas. Un caption no se queda colgado en los silencios (máx. 0,45 s tras la palabra).
- Deben estar en **todas** las partes normales del video (pero no duplicados: ver 7b).
  Solo se ocultan en el gancho (hasta la primera palabra después del título, sin caption en ese silencio)
  y cuando un gráfico de texto los reemplaza (p. ej. "comentá VIDEO").
- Ortografía: conservar ¿ ? en las preguntas; tildes correctas ("este", no "éste").
  Respetar cómo habla la persona (p. ej. voseo: podés, comentás, seguí): Whisper suele "corregirlo" → revisar.
  Los nombres propios y de marca suelen transcribirse mal: corregirlos (`captions.correcciones`, `nombres_propios`,
  `no_separar` en el brief).

## 6b. Trabas y final

- Si el usuario se traba o repite ("de eso, de robar"), quitar ese tramo (`cortes.quitar`). Probar candidatos
  transcribiendo el audio empalmado y elegir el que suene natural sin cortar palabras.
- **Nunca cortar la última palabra**: sin cortes en los últimos segundos y el fundido a la firma empieza después
  de que termina de hablar.

## 7. Textos destacados (frases clave)

- Estilo "¿TU DINERO ESTÁ SEGURO?": mayúsculas, mezcla de Open Sans ExtraBold y Light itálica, distintos tamaños.
- Arriba de la cabeza; **salen desde detrás de la persona** (máscara de persona en Remotion, `top_auto`) y terminan
  arriba sin tocar el pelo. Si no entran, se achican o se baja el zoom de ese corte.
- Usar en 2–3 frases fuertes del guion, con sus palabras exactas. Mientras están, se oculta el caption de abajo
  (si no, sale repetido).

## 7b. Reglas de uso de efectos (layering y motion graphics) — aprendidas en reels reales

**Menos es más: cada efecto tiene que leerse y relacionarse con lo que se está diciendo en ese instante.**

Layering (texto detrás de la persona):
- Que **se vea**: el texto **sale desde detrás de la cabeza** (sube ~1,1–1,6 veces su alto) y su posición final
  queda **arriba de la cabeza, sin tocarla** (`tapado: 0`, margen ~1,5 %). Así se ve el efecto al entrar y no hay
  pelo "intercalado" con las letras (la detección de pelo nunca es perfecta). Altura de la cabeza: el valor robusto
  (percentil 15 de la ventana). Si no entra, achicar el texto (`escala`) o bajar el zoom de ese corte.
- Las palabras detrás de la cabeza duran como máximo ~0,9 s y se van con fundido rápido (0,12 s).
- Títulos que no van detrás (gancho/portada) **no** pasan por la máscara de persona (si no, se borran).
- **Silueta limpia**: máscara en calidad alta, huecos de pelo rellenos y borde suavizado; si el pelo queda
  "intercalado" con las letras, se ve feo.
- **Espaciado**: nunca dos layering seguidos ("de robar" + "identidad" = cargado y raro). Mínimo ~4 s entre usos,
  contando también los destacados. Solo en 2–4 palabras fuertes del video (`detras_de_la_cabeza.solo`).
- **Sin repetir**: si arriba (layering o destacado) ya se lee la frase, se oculta el caption de abajo.
- **Sincronía exacta** con la voz: ajustar el inicio al ataque real de la palabra (Whisper se corre hasta 0,3 s).

Motion graphics:
- **Duración = lo que dura la frase que lo justifica (+0,3 s).** Si ya estoy diciendo otra cosa, el gráfico ya no
  tiene sentido y se ve raro.
- **Nunca dos gráficos a la vez** en la misma zona (ni superpuestos en el tiempo si recargan el cuadro):
  primero el escaneo de biometría, después la cédula. Los gráficos de arriba terminan antes de que entre un destacado.
- La cédula/objetos de "identidad" van **arriba de la cabeza**, no al costado de la cara.
- No llenar el cuadro: si hay lista abajo + caption + gráfico arriba, no agregar layering en ese momento.

## 8. Motion graphics

- Sincronizados con la palabra y con el **gesto** (cuando termina de señalar con la mano, no antes).
- Estilos aprobados:
  - Palabra/URL grande en verde claro entre las manos (estilo "HaveIBeenPwned.com"), con un sonido de revelación.
  - Caja blanca flotante con ícono de Instagram + usuario de la marca, donde apunta el dedo; sale antes del final.
  - Notificaciones de **vidrio oscuro semitransparente** tipo sistema (mensajes, banco), detalladas y realistas:
    entran con fundido y leve subida, sin inclinación; debajo de la cara, nunca encima.
- B-roll o gráfico en ejemplos concretos ("hablarle a mis familiares", "mi cuenta bancaria").
- Enumeraciones ("los bancos, los seguros, tu biometría…"): chips de vidrio que aparecen al nombrar cada uno;
  si después dice que fallan ("no están listas"), se tiñen de rojo apagado.
- La cara cambia de lugar según la toma (cámara más alta/baja): revisar la vista previa de **cada clip** y
  colocar los gráficos donde no la tapen (en un reel real los chips fueron a ~75 % de altura, bajo los captions).
- Si la primera toma es un primer plano que llena la pantalla, el título del gancho va abajo (≈72 %),
  sobre mentón/remera, dejando la boca libre.
- Los gráficos tienen que mostrar la **lógica** de lo que dice, no una lista plana: "bancos, seguros… que te piden
  biometría e identidad" = empresas arriba → "te piden" → datos abajo (en verde).
- Partes hechas con IA: etiqueta discreta "Este no soy yo" (vidrio oscuro con punto rojo) cuando lo pida la historia.
- "comentá X" y similares: debajo de la cara (`debajo_de_cara`), nunca encima.
- Aprobados en reels reales: **escaneo facial** sobre la cara al decir "biometría" (esquinas, línea de escaneo, malla de
  puntos, "Biometría capturada ✓", sigue la cara detectada) y **cédula de identidad arriba de la cabeza**
  al decir "identidad", después del escaneo (nunca a la vez).
- Más gráficos en la segunda mitad, cuando ya no hay efectos de IA en la grabación.

## 9. Transiciones

- Transición sutil (bordes que se oscurecen levemente + whoosh muy bajo) en **cada cambio fuerte de escena**.
  Detectar cambios automáticamente (diferencia entre fotogramas) además de los que marque el usuario.
- Gancho → resto: suspenso creciente (oscurecimiento 0,8 s + subida sonora + golpe grave suave).
- Final: **fundido cruzado** (0,6 s) entre los últimos fotogramas y la firma.

## 10. Sonido

- **Voz:** siempre procesar con `herramientas/voz.py` (EQ de claridad + nivelador + −14 LUFS). La voz debe sonar
  clara, nítida, fuerte y pareja en todo el video. Todo lo demás se mezcla por debajo.
- Efectos sutiles y profesionales, con variación (no repetir el mismo sonido). Volúmenes bajos:
  la notificación y el escaneo deben ser discretos.
- Riser largo desde la intriga hasta el choque → impacto → silencio. Preferir el **riser oscuro** (racimo grave
  que se abre, sin ruido blanco) y **bajo** (≈0,07). En un gancho de miedo, el remate es `golpe-miedo.wav`
  (grave + "braam" de tráiler + cola oscura), no el impacto saturado/metálico (sonó "raro").
- Escalofrío sutil (grave + acorde disonante + reverb) para un remate oscuro.
- Golpe/alarma grave para la frase más seria.
- Todo se sintetiza en `herramientas/sonidos.py` (sin licencias). Si el usuario aporta música o efectos
  con licencia, usar los suyos.

## 11. Música

- No elegir música si no se pide; cuando se pidió, funcionó así:
  - **Tensión** (Re menor, dron grave, latido creciente, golpes "chan" en palabras clave) en la parte dramática;
    unos 8 dB por debajo de la voz; **atenuada** en la frase más grave.
  - **Cierre** desde el llamado a seguir: beat **tech sobrio y seguro** (estilo presentación de producto,
    ≈112 BPM, bombo seco, sub-bajo con bombeo, acordes cortos filtrados, hi-hats finos). Sin melodías alegres.
    Se mezcla con la firma hasta el último fotograma y se desvanece al final.

## 12. Color e iluminación

- Look cinematográfico sobrio (composición `Gradeo` de Remotion): saturación ≈0,84, contraste ≈1,08,
  sombras frías, luces apenas cálidas, viñeta suave. Sutil, serio, profesional.
- **Iluminación profesional (pedido por el editor):** si hay varias tomas, medir brillo y calidez de la cara en cada
  una e igualarlas (`brillo` y `temperatura` por clip en `Combinar`), y agregar una **luz de rostro** suave que sigue
  la cara detectada (`luzRostro` ≈0,35) + viñeta ≈0,4 para separar a la persona del fondo.

## 13. Final

- Nada tapando la cabeza en los últimos fotogramas.
- Firma de cierre de la marca (video con logo, si existe en `marca/`) con fundido cruzado; cortarla cuando el logo ya está completo
  (≈3,9 s después del fundido), no dejarla de más. Audio de la firma limpio, con desvanecimiento al final.

---

## Proceso de trabajo con el usuario

- Español, claro y breve. El usuario no es técnico pero es un editor exigente: hablar de resultados, no de código.
- Hacer las pruebas técnicas uno mismo. Al usuario solo: cerrar/abrir CapCut, revisar, dejar archivos.
- Revisar con vistas previas (`vista_previa.py`) antes de entregar; mirar las imágenes de verdad.
- Cada entrega: tabla corta "pedido → qué hice", lo que no está comprobado, y una sola acción para el usuario.
- Versionar todo: proyecto de CapCut "reel-NN vXX" nuevo por versión, brief_vXX.json, respaldo en `respaldos/`.
- Cambiar solo lo pedido; si un cambio afecta otra parte, avisar.
- Los tiempos que da el usuario vienen del timecode de CapCut `ss:ff` (segundos:fotogramas a 30 fps):
  "37:25" = 37 s + 25 fotogramas = 37,83 s.

## Checklist antes de entregar una versión

Automático (obligatorio, **0 errores**): `python3 herramientas/revisar_reel.py proyectos/<reel>/briefs/brief_vNN.json`.
Revisa: captions sobre la cara, superpuestos, que parpadean, en silencios, repetidos con el texto de arriba,
saltos de altura en una toma, fuera de zona segura; layering que toca el pelo, muy largo o muy seguido;
gráficos que tapan la cara, dos a la vez, arriba junto a un destacado o demasiado largos; última palabra pisada
por el fundido; captions o máscara en el gancho.

A ojo (vistas previas y fotogramas de las capas exportadas):
- [ ] Recorrido emocional escrito en el brief y cada efecto justificado por la historia.
- [ ] Gancho progresivo, portada exportada (con su texto) y dentro de la zona segura.
- [ ] Captions con signos ¿? y voseo correcto; ninguna palabra de una traba quitada.
- [ ] Tomas importantes sin voz conservadas (pantallas, objetos, gestos).
- [ ] Transición sutil en cada cambio fuerte de escena; sin flashes salvo el del gancho.
- [ ] Riser con remate; silencio después del golpe.
- [ ] Voz procesada (−14 LUFS, pareja); música por debajo de la voz; efectos variados y discretos.
- [ ] Color/luz parejos entre tomas; fundido a la firma; duración final ajustada.
- [ ] `capcut lint` sin errores, `diagnose` sin divergencias, respaldo hecho.

## Para empezar un reel nuevo

1. Pedir: grabación original en `proyectos/<reel>/originales/` (y referencias nuevas si las hay).
2. Transcribir (`transcribir.mjs`), corregir voseo y nombres, detectar cambios de escena.
3. Copiar `plantillas/brief-reel.json` a `proyectos/<reel>/briefs/brief_v01.json` y adaptarlo a la historia.
4. Color (`Gradeo`) + voz (`voz.py`) → fuente procesada.
   Si el usuario manda **varios clips numerados** (orden = número del nombre): unirlos con la composición
   `Combinar` (recorta el silencio de inicio/fin de cada uno, lleva todo a 1080×1920 30 fps y aplica el color;
   config en `proyectos/<reel>/briefs/clips.json`). Cada unión de clips es un cambio de escena → transición sutil.
   Dejar ~0,5 s de pausa natural al inicio del clip que sigue a un golpe (silencio dramático).
   **Antes de recortar el inicio/fin de un clip, mirar qué se ve ahí**: puede haber tomas que el usuario quiere
   mostrar sin hablar (ej.: la pantalla de la compu con la edición hecha con IA + giro de cámara). Esas tomas
   se conservan, no se cortan como "silencio" (zona sin cortes) y van sin captions (`captions.sin_voz`).
5. Medir sobre la fuente final: `herramientas/caras <video> <json> 0.1` y
   `herramientas/personas <video> motion/public/mascaras/<reel> <json> 30`.
6. `armar_reel.py --solo-datos` → `revisar_reel.py` → `vista_previa.py` → render de capas → armar en CapCut.
   Plantilla más completa (varios clips, layering, máscaras, cara detectada): `plantillas/brief-reel-clips.json`.
