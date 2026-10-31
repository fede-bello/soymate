import { useCallback, useEffect, useRef, useState } from "react";
import {
  ApiError,
  getApi,
  MAX_UPLOAD_BYTES,
  type AnalyzeResult,
  type Example,
  type Mode,
} from "../api";
import Dropzone from "./Dropzone";
import Examples from "./Examples";
import Settings from "./Settings";
import SeedViewer from "./SeedViewer";
import SingleBean from "./SingleBean";
import Verdict from "./Verdict";
import Breakdown from "./Breakdown";
import ResultFacts from "./ResultFacts";
import Progress from "./Progress";

interface Source {
  file: File;
  url: string;
  example?: Example;
}

type Phase =
  | { kind: "idle" }
  | { kind: "loading"; started: number; rerun: boolean }
  | { kind: "done" }
  | { kind: "error"; error: ApiError; retry?: () => void };

const DEFAULT_DEFECT_CLASSES = ["broken", "stained", "immature", "insect_hole", "impurity"];

export default function Analyze() {
  const [mode, setMode] = useState<Mode>("auto");
  const [threshold, setThreshold] = useState(5);
  const [defect, setDefect] = useState("any");
  const [source, setSource] = useState<Source | null>(null);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [resultExample, setResultExample] = useState<Example | undefined>();
  const [phase, setPhase] = useState<Phase>({ kind: "idle" });
  const [loadingExample, setLoadingExample] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const stageRef = useRef<HTMLDivElement>(null);
  const settingsRef = useRef({ mode, threshold, defect });
  settingsRef.current = { mode, threshold, defect };
  const skipRerun = useRef(false); // set when picking an example switches the mode itself

  const run = useCallback(async (src: Source, rerun: boolean) => {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    setPhase({ kind: "loading", started: performance.now(), rerun });
    const { mode, threshold, defect } = settingsRef.current;
    try {
      const api = await getApi();
      const r = await api.analyze({ file: src.file, mode, threshold_pct: threshold, defect }, ac.signal);
      if (ac.signal.aborted) return;
      if (!r.seeds?.length || !r.summary?.n_seeds) {
        throw new ApiError("No seed found in this photo. Try a plain background with the seeds spread out.", "no_seed");
      }
      setResult(r);
      setResultUrl(src.url);
      setResultExample(src.example);
      setPhase({ kind: "done" });
    } catch (e) {
      if ((e as Error).name === "AbortError") return;
      const err =
        e instanceof ApiError ? e : new ApiError("Something went wrong while reading the answer from the server.", "server");
      setPhase({ kind: "error", error: err, retry: () => run(src, false) });
    }
  }, []);

  const startWith = useCallback(
    (file: File, example?: Example) => {
      if (!file.type.startsWith("image/") && !/\.(jpe?g|png)$/i.test(file.name)) {
        setPhase({ kind: "error", error: new ApiError("This is not a photo. Use a JPEG or PNG image.", "bad_file") });
        return;
      }
      if (file.size > MAX_UPLOAD_BYTES) {
        setPhase({ kind: "error", error: new ApiError("This photo is too large. The limit is 15 MB.", "too_large") });
        return;
      }
      const src = { file, url: URL.createObjectURL(file), example };
      setSource(src);
      setResult(null);
      run(src, false);
      requestAnimationFrame(() => stageRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
    },
    [run],
  );

  const pickExample = useCallback(
    async (ex: Example) => {
      setLoadingExample(ex.id);
      try {
        const api = await getApi();
        const file = await api.fetchExampleFile(ex);
        // Bulk examples only make sense in bulk mode; other examples leave bulk mode for auto.
        const want: Mode | null =
          ex.kind === "bulk" ? "bulk" : settingsRef.current.mode === "bulk" ? "auto" : null;
        if (want && want !== settingsRef.current.mode) {
          settingsRef.current = { ...settingsRef.current, mode: want };
          skipRerun.current = true;
          setMode(want);
        }
        startWith(file, ex);
      } catch (e) {
        setPhase({
          kind: "error",
          error: e instanceof ApiError ? e : new ApiError("Could not load this example.", "server"),
          retry: () => pickExample(ex),
        });
      } finally {
        setLoadingExample(null);
      }
    },
    [startWith],
  );

  // Changing a setting re-grades the current photo (debounced so the slider can be dragged).
  const firstRun = useRef(true);
  useEffect(() => {
    if (firstRun.current) {
      firstRun.current = false;
      return;
    }
    if (skipRerun.current) {
      skipRerun.current = false;
      return;
    }
    if (!source) return;
    const t = setTimeout(() => run(source, true), 450);
    return () => clearTimeout(t);
  }, [mode, threshold, defect]);

  const loading = phase.kind === "loading";
  const rerunning = loading && phase.rerun && !!result;
  const defectClasses = (result?.model.classes ?? DEFAULT_DEFECT_CLASSES).filter((c) => c !== "sound");

  return (
    <div className="page">
      <section className="intro" aria-labelledby="analyze-title">
        <h1 id="analyze-title">Grade a seed sample from one photo</h1>
        <p>
          Upload or take a photo of soybeans on a plain background. SoyMate finds every seed, checks each one, and tells
          you how much damage there is and how sure it is.
        </p>
      </section>

      <div className="workspace">
        <div className="stage" ref={stageRef}>
          {!source && phase.kind !== "error" && <Dropzone onFile={(f) => startWith(f)} big />}

          {phase.kind === "error" && (
            <div className="error-card" role="alert">
              <h2>{errorTitle(phase.error)}</h2>
              <p>{phase.error.message}</p>
              <div className="row gap">
                {phase.retry && phase.error.kind !== "too_large" && phase.error.kind !== "bad_file" && (
                  <button className="btn btn-primary" onClick={phase.retry}>
                    Try again
                  </button>
                )}
                {result && (
                  <button className="btn" onClick={() => setPhase({ kind: "done" })}>
                    Back to the last result
                  </button>
                )}
              </div>
              {phase.error.kind === "no_seed" && (
                <ul className="tips">
                  <li>Put the seeds on a plain, contrasting background (blue or dark paper works well).</li>
                  <li>Spread them out so most do not touch.</li>
                  <li>Shoot from above with even light, filling the frame.</li>
                </ul>
              )}
              <Dropzone onFile={(f) => startWith(f)} />
            </div>
          )}

          {loading && !rerunning && source && (
            <Progress imageUrl={source.url} started={phase.started} label={source.example?.label ?? source.file.name} />
          )}

          {result && resultUrl && (phase.kind === "done" || rerunning) && (
            <>
              {result.mode === "bulk" && (
                <div className="notice notice-warn bulk-banner" role="note">
                  <span>
                    <strong>Experimental bulk mode.</strong>{" "}
                    {result.model.warnings?.find((w) => w.startsWith("Experimental bulk mode"))?.replace(/^Experimental bulk mode:\s*/, "") ??
                      "Packed seeds found with FastSAM; treat counts and shares as indicative."}
                  </span>
                </div>
              )}
              {result.mode === "single" ? (
                <SingleBean result={result} imageUrl={resultUrl} />
              ) : (
                <SeedViewer result={result} imageUrl={resultUrl} />
              )}
            </>
          )}
        </div>

        <aside className="panel" aria-label="Settings and result">
          <Settings
            mode={mode}
            onMode={setMode}
            threshold={threshold}
            onThreshold={setThreshold}
            defect={defect}
            onDefect={setDefect}
            defectClasses={defectClasses}
          />
          {result && (phase.kind === "done" || rerunning) && (
            <div className={rerunning ? "panel-results is-updating" : "panel-results"} aria-busy={rerunning}>
              {rerunning && (
                <p className="updating" role="status">
                  <span className="spinner" aria-hidden="true" /> Updating the grade with the new settings...
                </p>
              )}
              <Verdict result={result} />
              <ResultFacts result={result} example={resultExample} part="warnings" />
            </div>
          )}
          {!result && phase.kind !== "loading" && (
            <div className="panel-empty">
              <p>
                The verdict appears here: <strong className="t-pass">pass</strong>,{" "}
                <strong className="t-warn">add more seeds</strong> or <strong className="t-fail">fail</strong>, against the
                defect limit you set above.
              </p>
            </div>
          )}
        </aside>

        {result && resultUrl && (phase.kind === "done" || rerunning) && (
          <div className={rerunning ? "details result-grid is-updating" : "details result-grid"}>
            <Breakdown result={result} />
            <div className="result-side">
              <ResultFacts result={result} example={resultExample} part="truth" />
              <ResultFacts result={result} example={resultExample} part="facts" />
              <Dropzone onFile={(f) => startWith(f)} compact />
            </div>
          </div>
        )}
      </div>

      <Examples onPick={pickExample} loadingId={loadingExample} disabled={loading && !rerunning} />
    </div>
  );
}

function errorTitle(e: ApiError): string {
  switch (e.kind) {
    case "no_seed":
      return "No seeds found";
    case "too_large":
      return "Photo too large";
    case "bad_file":
      return "Can't read this file";
    case "offline":
      return "Server not reachable";
    default:
      return "Something went wrong";
  }
}
