import {textEm, textW} from '../src/common/textfit';

const em = textEm('Привет');
if (Math.abs(em - 3.443) > 0.08) {
  throw new Error(`Cyrillic em width mismatch: ${em}`);
}

const width = textW('Привет', 114.41649695);
if (Math.abs(width - 393.932) > 0.5) {
  throw new Error(`Cyrillic pixel width mismatch: ${width}`);
}

console.log('russian textfit ok', {em, width});
