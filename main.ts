// News-image entrypoint (Node 22, standard library only). The front page
// is drawn ahead of time and stored next to this file as entry.png; all
// this program does is copy that file to the grader's output directory.
// Run it locally with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
