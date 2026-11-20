// main.ts — entrypoint for the news-image-20261120 bounty.
//
// Copies the pre-rendered front page (entry.png) to the output directory
// the grader provides through MAKEFUN_OUTPUT_DIR. Node 22, standard
// library only; it runs offline, twice, and writes identical bytes
// on every run because it only copies a fixed file.
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR;
if (!outDir) {
  throw new Error("MAKEFUN_OUTPUT_DIR is not set");
}

const repoRoot = dirname(fileURLToPath(import.meta.url));
mkdirSync(outDir, { recursive: true });
copyFileSync(join(repoRoot, "entry.png"), join(outDir, "entry.png"));
