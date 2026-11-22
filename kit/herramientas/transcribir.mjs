import {transcribe, toCaptions} from '@remotion/install-whisper-cpp';
import fs from 'node:fs';
// Uso: node transcribir.mjs <wav 16 kHz, ruta absoluta> <salida.json> [idioma, por defecto es]
const [,, wav, out, idioma = 'es'] = process.argv;
const dir = new URL('./whisper.cpp', import.meta.url).pathname;
const r = await transcribe({inputPath: wav, whisperPath: dir, whisperCppVersion: '1.5.5', model: 'medium', modelFolder: dir, tokenLevelTimestamps: true, language: idioma, printOutput: false});
const {captions} = toCaptions({whisperCppOutput: r});
fs.writeFileSync(out, JSON.stringify(captions, null, 1));
console.log(captions.map(c => c.text).join(''));
