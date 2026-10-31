// Display helpers: class names, colours and number formatting.

const LABELS: Record<string, string> = {
  sound: "Sound",
  broken: "Broken",
  stained: "Stained",
  immature: "Immature (green)",
  insect_hole: "Insect hole",
  impurity: "Impurity",
  crushed: "Crushed",
  intact: "Intact",
};

const HINTS: Record<string, string> = {
  sound: "no visible defect",
  broken: "split, cracked or damaged seed coat",
  stained: "spots or discoloured coat",
  immature: "picked unripe, greenish",
  insect_hole: "exit hole of a storage beetle",
  impurity: "not a seed: soil, stem, stone",
};

// Bright outline colours chosen to stand out on photos (drawn over a dark halo).
const COLOURS: Record<string, string> = {
  sound: "#43C35E",
  broken: "#FF8A1F",
  stained: "#B47CFF",
  immature: "#F5DC3A",
  insect_hole: "#FF4D57",
  impurity: "#2EC4D6",
};
const FALLBACK = ["#F06EB0", "#9BD3A0", "#FFFFFF", "#C0A080"];

export function classLabel(c: string): string {
  return LABELS[c] ?? c.replace(/_/g, " ").replace(/^./, (m) => m.toUpperCase());
}

export function classHint(c: string): string | undefined {
  return HINTS[c];
}

export function classColour(c: string): string {
  if (COLOURS[c]) return COLOURS[c];
  let h = 0;
  for (const ch of c) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return FALLBACK[h % FALLBACK.length];
}

/** "8.5 %" with a thin space-free style matching the contract ("5 %"). */
export function pct(v: number, digits = 1): string {
  return `${Number.isInteger(v) && digits === 0 ? v : v.toFixed(digits).replace(/\.0$/, "")} %`;
}

export function prob(v: number): string {
  return `${Math.round(v * 100)} %`;
}

export function seconds(ms: number | undefined): string | undefined {
  if (ms == null) return undefined;
  return ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(1)} s`;
}

export function fmtInt(n: number): string {
  return n.toLocaleString("en-GB");
}
