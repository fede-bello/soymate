// Client for the SoyMate demo API (contract: app/API.md). Relative URLs, same origin.

export type Mode = "auto" | "single" | "batch";
export type Status = "pass" | "fail" | "inconclusive";

export interface Seed {
  id: number;
  bbox: [number, number, number, number];
  polygon: [number, number][];
  n_est: number;
  class: string;
  confidence: number;
  probs: Record<string, number>;
}

export interface ClassShare {
  n: number;
  pct: number;
  ci95: [number, number];
}

export interface AnalyzeResult {
  mode: "single" | "batch";
  image: { width: number; height: number };
  model: { name: string; classes: string[]; trained_on: string[]; warnings: string[] };
  seeds: Seed[];
  summary: {
    n_seeds: number;
    classes: Record<string, ClassShare>;
    defect: ClassShare & { label: string };
  };
  verdict: {
    threshold_pct: number;
    status: Status;
    seeds_needed: number | null;
    explanation: string;
  };
  timing_ms: { segment?: number; classify?: number; total?: number; [k: string]: number | undefined };
}

export interface Example {
  id: string;
  label: string;
  kind: "batch" | "single";
  dataset: string;
  url: string;
  note?: string;
  source?: string;
  /** Batch: {n_seeds} hand count. Single seed: {class, n_seeds: 1} dataset label. Null when unknown. */
  ground_truth?: { n_seeds?: number; class?: string; [k: string]: unknown } | null;
}

export interface EvidenceCard {
  id: string;
  title: string;
  headline: string;
  numbers: { label: string; value: string; ci95?: string | null }[];
  caveat?: string;
  source?: string;
}

export interface Evidence {
  cards: EvidenceCard[];
  provenance_url?: string;
}

export interface Health {
  status: string;
  model: string;
  version: string;
}

export interface AnalyzeParams {
  file: File;
  mode: Mode;
  threshold_pct: number;
  defect: string;
}

export interface Api {
  health(): Promise<Health>;
  examples(): Promise<Example[]>;
  evidence(): Promise<Evidence>;
  analyze(p: AnalyzeParams, signal?: AbortSignal): Promise<AnalyzeResult>;
  fetchExampleFile(ex: Example): Promise<File>;
}

export const MAX_UPLOAD_BYTES = 15 * 1024 * 1024;

/** Error with a message that can be shown to the user as is. */
export class ApiError extends Error {
  constructor(
    message: string,
    public kind: "no_seed" | "too_large" | "bad_file" | "offline" | "server",
    public status?: number,
  ) {
    super(message);
  }
}

async function readDetail(res: Response): Promise<string | undefined> {
  try {
    const body = await res.json();
    if (typeof body?.detail === "string") return body.detail;
    if (Array.isArray(body?.detail)) return body.detail.map((d: { msg?: string }) => d.msg).join("; ");
  } catch {
    /* not JSON */
  }
  return undefined;
}

async function getJson<T>(url: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, { headers: { Accept: "application/json" } });
  } catch {
    throw new ApiError("Can't reach the SoyMate server. Check the connection and try again.", "offline");
  }
  if (!res.ok) {
    const detail = await readDetail(res);
    throw new ApiError(detail ?? `The server answered with an error (${res.status}).`, "server", res.status);
  }
  return res.json() as Promise<T>;
}

const realApi: Api = {
  health: () => getJson<Health>("/api/health"),
  examples: () => getJson<Example[]>("/api/examples"),
  evidence: () => getJson<Evidence>("/api/evidence"),

  async analyze({ file, mode, threshold_pct, defect }, signal) {
    const fd = new FormData();
    fd.append("file", file, file.name || "photo.jpg");
    fd.append("mode", mode);
    fd.append("threshold_pct", String(threshold_pct));
    fd.append("defect", defect);
    let res: Response;
    try {
      res = await fetch("/api/analyze", { method: "POST", body: fd, signal });
    } catch (e) {
      if ((e as Error).name === "AbortError") throw e;
      throw new ApiError("Can't reach the SoyMate server. Check the connection and try again.", "offline");
    }
    if (res.ok) return res.json() as Promise<AnalyzeResult>;
    const detail = await readDetail(res);
    if (res.status === 413) throw new ApiError("This photo is too large. The limit is 15 MB.", "too_large", 413);
    if (res.status === 400) {
      const noSeed = detail ? /no seed|no seeds|not find|found no/i.test(detail) : false;
      throw new ApiError(detail ?? "The server could not read this photo.", noSeed ? "no_seed" : "bad_file", 400);
    }
    if (res.status === 502 || res.status === 503 || res.status === 504)
      throw new ApiError("The analysis server is not responding right now. Try again in a moment.", "offline", res.status);
    throw new ApiError(detail ?? `The server answered with an error (${res.status}).`, "server", res.status);
  },

  async fetchExampleFile(ex) {
    let res: Response;
    try {
      res = await fetch(ex.url);
    } catch {
      throw new ApiError("Can't reach the SoyMate server to load this example.", "offline");
    }
    if (!res.ok) throw new ApiError(`Could not load this example (${res.status}).`, "server", res.status);
    const blob = await res.blob();
    const name = ex.url.split("/").pop() || `${ex.id}.jpg`;
    return new File([blob], name, { type: blob.type || "image/jpeg" });
  },
};

export const IS_MOCK = import.meta.env.VITE_MOCK === "1";

let apiPromise: Promise<Api> | undefined;

/** The real API, or the mock when built/run with VITE_MOCK=1 (the mock is not bundled otherwise). */
export function getApi(): Promise<Api> {
  if (!apiPromise) {
    apiPromise = IS_MOCK ? import("./mocks").then((m) => m.mockApi) : Promise.resolve(realApi);
  }
  return apiPromise;
}
