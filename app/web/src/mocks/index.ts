// Dev-only mock of the SoyMate API (loaded only when VITE_MOCK=1; never in the production build).
// Seed outlines come from our training-free segmenter run on a local Ghana photo; the classes and
// probabilities are RANDOM placeholders, so nothing here is a result. Evidence cards come from app/api/evidence.py.
import type { AnalyzeParams, AnalyzeResult, Api, ClassShare, Evidence, Example, Seed } from "../api";
import { ApiError } from "../api";
import batchImg from "./ghana_batch.jpg";
import batchSeeds from "./ghana_batch.seeds.json";
import singleImg from "./single_bean.jpg";
import singleSeed from "./single_bean.seed.json";
import evidenceJson from "./evidence.json";

const CLASSES = ["sound", "broken", "stained", "immature", "insect_hole", "impurity"];
const MODEL = {
  name: "soymate-pooled-v1 (mock)",
  classes: CLASSES,
  trained_on: ["soybean d97rjyk2tz", "soybean Lin v6vzvfszj6", "harvest hwdtghttp7"],
  warnings: [
    "Classes come from different datasets; on photos from a new camera setup the class shares are uncalibrated (dataset-ID check: 100 %).",
  ],
};

const sleep = (ms: number, signal?: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const t = setTimeout(resolve, ms);
    signal?.addEventListener("abort", () => {
      clearTimeout(t);
      reject(new DOMException("Aborted", "AbortError"));
    });
  });

const Z = 1.959964;
function wilson(k: number, n: number): [number, number] {
  if (n === 0) return [0, 100];
  const p = k / n;
  const d = 1 + (Z * Z) / n;
  const c = (p + (Z * Z) / (2 * n)) / d;
  const h = (Z * Math.sqrt((p * (1 - p)) / n + (Z * Z) / (4 * n * n))) / d;
  return [+(100 * Math.max(0, c - h)).toFixed(1), +(100 * Math.min(1, c + h)).toFixed(1)];
}

function seedsNeeded(p: number, t: number): number | null {
  if (p === t) return null;
  for (let n = 10; n < 200000; n = Math.ceil(n * 1.05)) {
    const [lo, hi] = wilson(Math.round(p * n), n).map((v) => v / 100);
    if (hi < t || lo > t) return n;
  }
  return null;
}

function share(k: number, n: number): ClassShare {
  return { n: k, pct: +((100 * k) / Math.max(1, n)).toFixed(1), ci95: wilson(k, n) };
}

function summarise(seeds: Seed[], mode: "single" | "batch", threshold: number, defect: string): AnalyzeResult {
  const n = seeds.reduce((a, s) => a + s.n_est, 0);
  const counts: Record<string, number> = Object.fromEntries(CLASSES.map((c) => [c, 0]));
  for (const s of seeds) counts[s.class] += s.n_est;
  const classes = Object.fromEntries(CLASSES.map((c) => [c, share(counts[c], n)]));
  const kDef = defect === "any" ? n - counts.sound : counts[defect] ?? 0;
  const def = { ...share(kDef, n), label: defect === "any" ? "any defect" : defect.replace("_", " ") };
  const [lo, hi] = def.ci95;
  const status = hi < threshold ? "pass" : lo > threshold ? "fail" : "inconclusive";
  const range = `${lo}-${hi} %`;
  const explanation =
    status === "pass"
      ? `The 95 % interval (${range}) is below ${threshold} %: pass.`
      : status === "fail"
        ? `The 95 % interval (${range}) is above ${threshold} %: fail.`
        : `The 95 % interval (${range}) contains ${threshold} %: photograph more seeds to decide.`;
  return {
    mode,
    image: { width: 0, height: 0 },
    model: MODEL,
    seeds,
    summary: { n_seeds: n, classes, defect: def },
    verdict: {
      threshold_pct: threshold,
      status,
      seeds_needed: status === "inconclusive" ? seedsNeeded(kDef / n, threshold / 100) : null,
      explanation,
    },
    timing_ms: { segment: 38, classify: 3050, total: 3140 },
  };
}

// Same shape as app/api/examples/examples.json; images are local stand-ins.
const GHANA = "Ghana soybean seeds t94nzy4ptz, Mendeley Data (CC BY 4.0)";
const SOY = "Soybean seed defects d97rjyk2tz v2, Mendeley Data (CC BY 4.0)";
const examples: Example[] = [
  {
    id: "ghana_g17",
    label: "Ghana farmer-saved lot (164 seeds)",
    kind: "batch",
    dataset: GHANA,
    url: batchImg,
    note: "Mock: outlines are real, classes are random.",
    ground_truth: { n_seeds: 164 },
    source: "seed_data/Soyabean/group_capture/FarmerSaved/PXL_20260315_135711992.jpg",
  },
  {
    id: "ghana_afayak_shadow",
    label: "Ghana Afayak lot in hard shadow (mock)",
    kind: "batch",
    dataset: GHANA,
    url: batchImg,
    note: "Mock: no complete reference count, so no hand-count card.",
    ground_truth: null,
  },
  {
    id: "soy_broken_single",
    label: "Single soybean seed, labelled broken (mock)",
    kind: "single",
    dataset: SOY,
    url: singleImg,
    note: "Mock single-bean result: label matches.",
    ground_truth: { class: "broken", n_seeds: 1 },
  },
  {
    id: "soy_sound_single",
    label: "Single soybean seed, labelled sound (mock)",
    kind: "single",
    dataset: SOY,
    url: singleImg,
    note: "Mock single-bean result: label does not match.",
    ground_truth: { class: "sound", n_seeds: 1 },
  },
  {
    id: "missing",
    label: "Broken example link (mock)",
    kind: "batch",
    dataset: "Mock",
    url: "/api/examples/files/does-not-exist.jpg",
    note: "Tests the error state.",
  },
];

// Generated by app/api/evidence.py build() from results/*.json (the same cards the server returns).
const evidence = evidenceJson as Evidence;


export const mockApi: Api = {
  async health() {
    await sleep(150);
    return { status: "ok", model: MODEL.name, version: "mock" };
  },
  async examples() {
    await sleep(300);
    return examples;
  },
  async evidence() {
    await sleep(300);
    return evidence;
  },
  async fetchExampleFile(ex) {
    const res = await fetch(ex.url);
    if (!res.ok || !(res.headers.get("content-type") ?? "").startsWith("image/"))
      throw new ApiError("Could not load this example (404).", "server", 404);
    const blob = await res.blob();
    return new File([blob], `${ex.id}.jpg`, { type: blob.type });
  },
  async analyze({ file, mode, threshold_pct, defect }: AnalyzeParams, signal) {
    await sleep(2600, signal);
    const name = file.name.toLowerCase();
    if (name.includes("noseed")) throw new ApiError("No seed found in this photo.", "no_seed", 400);
    if (name.includes("down")) throw new ApiError("Can't reach the SoyMate server. Check the connection and try again.", "offline");
    if (file.size > 15 * 1024 * 1024) throw new ApiError("This photo is too large. The limit is 15 MB.", "too_large", 413);
    const single = mode === "single" || (mode === "auto" && name.includes("single"));
    if (single) {
      const probs = { sound: 0.12, broken: 0.71, stained: 0.09, immature: 0.05, insect_hole: 0.02, impurity: 0.01 };
      const seed: Seed = {
        id: 1,
        bbox: singleSeed.bbox as Seed["bbox"],
        polygon: singleSeed.polygon as Seed["polygon"],
        n_est: 1,
        class: "broken",
        confidence: 0.71,
        probs,
      };
      const r = summarise([seed], "single", threshold_pct, defect);
      r.image = singleSeed.image;
      r.timing_ms = { segment: 6, classify: 410, total: 450 };
      return r;
    }
    const r = summarise(batchSeeds.seeds as unknown as Seed[], "batch", threshold_pct, defect);
    r.image = batchSeeds.image;
    return r;
  },
};
