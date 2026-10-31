import type { AnalyzeResult, Example } from "../api";
import { classLabel, fmtInt, seconds } from "../lib";
import { largestSeed } from "./scale";

/** Ground truth (when the example has one), model warnings, timing and model details. */
export default function ResultFacts({
  result,
  example,
  part,
}: {
  result: AnalyzeResult;
  example?: Example;
  part: "truth" | "warnings" | "facts";
}) {
  const hand = example?.ground_truth?.n_seeds;
  const label = example?.ground_truth?.class;
  const predicted = result.mode === "single" ? largestSeed(result)?.class : undefined;
  const found = result.summary.n_seeds;
  const t = result.timing_ms ?? {};
  const timing = [
    seconds(t.segment) && `found seeds in ${seconds(t.segment)}`,
    seconds(t.classify) && `checked them in ${seconds(t.classify)}`,
    seconds(t.total) && `total ${seconds(t.total)}`,
  ].filter(Boolean);

  return (
    <>
      {part === "truth" && typeof hand === "number" && result.mode === "batch" && (
        <section className="card truth" aria-labelledby="truth-title">
          <h2 id="truth-title" className="card-title">
            Checked against a hand count
          </h2>
          <div className="truth-figures">
            <div>
              <span className="truth-n">{fmtInt(hand)}</span>
              <span className="truth-l">counted by hand</span>
            </div>
            <div>
              <span className="truth-n">{fmtInt(found)}</span>
              <span className="truth-l">found by SoyMate</span>
            </div>
          </div>
          <p className="muted small">
            {found === hand
              ? "Same count."
              : `${fmtInt(Math.abs(found - hand))} ${found > hand ? "more" : "fewer"} than the hand count.`}{" "}
            Reference from {example?.dataset}.
          </p>
        </section>
      )}

      {part === "truth" && result.mode === "single" && typeof label === "string" && predicted && (
        <section className="card truth" aria-labelledby="truth-title">
          <h2 id="truth-title" className="card-title">
            Checked against the dataset label
          </h2>
          <div className="truth-figures">
            <div>
              <span className="truth-n truth-class">{classLabel(label)}</span>
              <span className="truth-l">label in the dataset</span>
            </div>
            <div>
              <span className="truth-n truth-class">{classLabel(predicted)}</span>
              <span className="truth-l">predicted by SoyMate</span>
            </div>
          </div>
          <p className={`small ${label === predicted ? "t-pass" : "t-fail"}`}>
            <strong>{label === predicted ? "Match." : "No match."}</strong>{" "}
            <span className="muted">Label from {example?.dataset}.</span>
          </p>
        </section>
      )}

      {part === "warnings" && result.model.warnings?.length > 0 && (
        <section className="notice notice-warn warnings" aria-labelledby="warn-title">
          <h2 id="warn-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true">
              <path d="M12 3l10 18H2L12 3z" />
              <path d="M12 10v5M12 18v.01" />
            </svg>
            Read before trusting this result
          </h2>
          <ul>
            {result.model.warnings.map((w, i) => (
              <li key={i}>{w.replace(/\s*\u2014\s*/g, ", ")}</li>
            ))}
          </ul>
        </section>
      )}

      {part === "facts" && (
      <section className="facts" aria-label="Model and timing">
        {timing.length > 0 && <p>Speed: {timing.join(", ")}.</p>}
        <p>
          Model <code>{result.model.name}</code>
          {result.model.trained_on?.length ? `, trained on ${result.model.trained_on.join(", ")}` : ""}.
        </p>
      </section>
      )}
    </>
  );
}
