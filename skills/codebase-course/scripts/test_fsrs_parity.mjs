// Differential test: emits reference FSRS-6 outputs from the real ts-fsrs so the
// Python port in study.py can be checked against them.
//
// Run from any repo that has ts-fsrs installed (e.g. arboreus-api):
//     node path/to/test_fsrs_parity.mjs > /tmp/fsrs-ref.jsonl
//     python3 path/to/test_fsrs_parity.py /tmp/fsrs-ref.jsonl
//
// If study.py's port ever drifts from the reference, this is what catches it.

import { existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

// Resolve ts-fsrs from the CWD's node_modules — this script lives outside the
// repo under test, so bare-specifier resolution would look in the wrong tree.
const local = path.resolve(process.cwd(), 'node_modules/ts-fsrs/dist/index.mjs');
const { FSRSAlgorithm, generatorParameters, FSRSVersion } =
  await import(existsSync(local) ? pathToFileURL(local).href : 'ts-fsrs');

console.error(`reference impl: ${FSRSVersion}`);
const algo = new FSRSAlgorithm(generatorParameters({ enable_fuzz: false }));

const out = [];

// New cards: no memory state, every grade.
for (const g of [1, 2, 3, 4]) {
  const st = algo.next_state({ difficulty: 0, stability: 0 }, 0, g);
  out.push({ kind: 'new', d: 0, s: 0, t: 0, g,
             ed: st.difficulty, es: st.stability, ei: algo.next_interval(st.stability, 0) });
}

// Existing states across the plausible space.
for (const d of [1, 3.5, 5.2, 7.2, 10]) {
  for (const s of [0.1, 1, 3.17, 15, 100, 1000]) {
    for (const t of [0, 1, 3, 10, 365]) {
      for (const g of [1, 2, 3, 4]) {
        const st = algo.next_state({ difficulty: d, stability: s }, t, g);
        out.push({ kind: 'review', d, s, t, g,
                   ed: st.difficulty, es: st.stability, ei: algo.next_interval(st.stability, t) });
      }
    }
  }
}

// Forgetting curve directly.
for (const s of [0.1, 1, 3.17, 15, 100, 1000]) {
  for (const t of [0, 1, 3, 10, 365]) {
    out.push({ kind: 'curve', s, t, er: algo.forgetting_curve(t, s) });
  }
}

for (const row of out) console.log(JSON.stringify(row));
