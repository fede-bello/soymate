import type { AnalyzeResult } from "../api";

/** A round axis maximum (1, 2, 2.5, 5 x 10^n) at or above v. */
export function niceMax(v: number): number {
  if (!(v > 0)) return 10;
  const e = Math.pow(10, Math.floor(Math.log10(v)));
  for (const m of [1, 2, 2.5, 5, 10]) if (m * e >= v) return Math.min(100, m * e);
  return 100;
}

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));

const area = (b: number[]) => (b[2] - b[0]) * (b[3] - b[1]);

/** The seed judged in a single-bean result: the largest outline. */
export function largestSeed(r: AnalyzeResult) {
  return [...r.seeds].sort((a, b) => area(b.bbox) - area(a.bbox))[0];
}
