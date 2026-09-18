const fs = require('node:fs');
const path = require('node:path');
const {createRequire} = require('node:module');

const requireFromTemplate = createRequire(
  path.join(__dirname, '../package.json'),
);
const ts = requireFromTemplate('typescript');

require.extensions['.ts'] = (module, filename) => {
  const source = fs.readFileSync(filename, 'utf8');
  const output = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
    },
    fileName: filename,
  }).outputText;
  module._compile(output, filename);
};

require('./test_russian_textfit.ts');
