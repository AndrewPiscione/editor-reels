// Descarga y compila whisper.cpp 1.5.5 en herramientas/whisper.cpp (transcripción local, sin internet después).
import {installWhisperCpp} from '@remotion/install-whisper-cpp';
const dir = new URL('./whisper.cpp', import.meta.url).pathname;
await installWhisperCpp({to: dir, version: '1.5.5', printOutput: false});
console.log('OK', dir);
