// Differential test for the browser reviewer's FSRS port.
//
// Extracts the FSRS block from references/review.html between the
// ---FSRS-START--- / ---FSRS-END--- markers (so we test the exact code that
// ships, no drift), then checks it against the ts-fsrs reference fixture.
//
//     node test_fsrs_parity.mjs > /tmp/fsrs-ref.jsonl   # from a repo with ts-fsrs
//     node test_fsrs_parity_js.mjs /tmp/fsrs-ref.jsonl
//
// Exits non-zero on any mismatch.

import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const htmlPath = path.resolve(here, '../references/review.html');
const fixturePath = process.argv[2] || '/tmp/fsrs-ref.jsonl';

const html = readFileSync(htmlPath, 'utf8');
const m = html.match(/---FSRS-START---\s*\*\/\s*([\s\S]*?)\/\* ---FSRS-END---/);
if (!m) { console.error('could not find FSRS block markers in review.html'); process.exit(1); }

// The block declares `const FSRS = (function(){...})();` — eval it, return FSRS.
const FSRS = new Function(m[1] + '\nreturn FSRS;')();

const rows = readFileSync(fixturePath, 'utf8').trim().split('\n').filter(Boolean).map((l) => JSON.parse(l));
if (!rows.length) { console.error('no reference rows — run the node generator first'); process.exit(1); }

const TOL = 1e-8;
const fails = [];
let maxDD = 0, maxDS = 0, maxDR = 0;

for (const r of rows) {
  if (r.kind === 'curve') {
    const got = FSRS.forgettingCurve(r.t, r.s);
    const diff = Math.abs(got - r.er);
    maxDR = Math.max(maxDR, diff);
    if (diff > TOL) fails.push(`curve t=${r.t} s=${r.s}: got ${got}, want ${r.er}`);
    continue;
  }
  const [gd, gs] = FSRS.nextState(r.d, r.s, r.t, r.g);
  const gi = FSRS.nextInterval(gs);
  const dd = Math.abs(gd - r.ed), ds = Math.abs(gs - r.es);
  maxDD = Math.max(maxDD, dd); maxDS = Math.max(maxDS, ds);
  const ctx = `${r.kind} d=${r.d} s=${r.s} t=${r.t} g=${r.g}`;
  if (dd > TOL) fails.push(`${ctx}: difficulty got ${gd}, want ${r.ed}`);
  if (ds > TOL) fails.push(`${ctx}: stability got ${gs}, want ${r.es}`);
  if (gi !== r.ei) fails.push(`${ctx}: interval got ${gi}, want ${r.ei}`);
}

console.log(`${rows.length} reference cases`);
console.log(`max abs diff — difficulty ${maxDD.toExponential(2)}, stability ${maxDS.toExponential(2)}, retrievability ${maxDR.toExponential(2)}`);
if (fails.length) {
  console.log(`\nFAIL (${fails.length} mismatches):`);
  fails.slice(0, 20).forEach((f) => console.log('  ' + f));
  if (fails.length > 20) console.log(`  … and ${fails.length - 20} more`);
  process.exit(1);
}
console.log('PASS — browser FSRS port matches ts-fsrs on every case');
