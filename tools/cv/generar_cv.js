// Genera los PDF de la hoja de vida: node tools/cv/generar_cv.js
const { chromium } = require('playwright');
const path = require('path');
const raiz = path.resolve(__dirname, '../..');
const salidas = [
  ['cv.html', 'Santiago_Rodriguez_CV.pdf'],
  ['cv_ats.html', 'Santiago_Rodriguez_CV_ATS.pdf'],
];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  for (const [src, out] of salidas) {
    await p.goto('file://' + path.join(__dirname, src));
    await p.evaluate(() => document.fonts.ready);
    const desborde = await p.evaluate(() => {
      const m = [...document.querySelectorAll('main, aside, .page')];
      return m.map(e => e.scrollHeight - e.clientHeight);
    });
    console.log(src, 'desborde(px):', desborde.join(','));
    await p.pdf({ path: path.join(raiz, out), format: 'A4', printBackground: true, preferCSSPageSize: true });
  }
  await b.close();
})();
