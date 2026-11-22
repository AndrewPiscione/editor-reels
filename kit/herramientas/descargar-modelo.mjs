import {downloadWhisperModel} from '@remotion/install-whisper-cpp';
await downloadWhisperModel({model: 'medium', folder: new URL('./whisper.cpp', import.meta.url).pathname, printOutput: false});
console.log('OK');
