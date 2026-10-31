import type { AnalyzeResult } from "../api";
import { fmtInt, pct } from "../lib";
import { clamp01, niceMax } from "./scale";

const TITLES = { pass: "Pass", fail: "Fail", inconclusive: "Not sure yet" } as const;
const noDash = (s: string) => s.replace(/\s*\u2014\s*/g, ", ");

export default function Verdict({ result }: { result: AnalyzeResult }) {
  const { verdict, summary } = result;
  if (result.mode === "single") {
    return (
      <section className="card verdict verdict-neutral" aria-labelledby="verdict-title">
        <h2 id="verdict-title" className="card-title">
          A lot needs many seeds
        </h2>
        <p>
          One seed always gives a very wide interval, so there is no pass or fail here. Use a batch photo: a handful of
          seeds spread on a plain background.
        </p>
      </section>
    );
  }

  const d = summary.defect;
  const status = verdict.status in TITLES ? verdict.status : "inconclusive";
  const thr = verdict.threshold_pct;
  const max = niceMax(Math.max(d.ci95[1], thr, d.pct) * 1.25);
  const at = (v: number) => `${clamp01(v / max) * 100}%`;
  const more = verdict.seeds_needed != null ? Math.max(0, verdict.seeds_needed - summary.n_seeds) : null;

  return (
    <section className={`card verdict verdict-${status}`} aria-labelledby="verdict-title" aria-live="polite">
      <p className="eyebrow">
        Verdict for {d.label}, limit {pct(thr)}
      </p>
      <div className="verdict-head">
        <StatusIcon status={status} />
        <h2 id="verdict-title">{TITLES[status]}</h2>
      </div>

      <p className="verdict-figure">
        <span className="verdict-pct">{pct(d.pct)}</span>
        <span className="verdict-of">
          {d.label}
          <br />
          {fmtInt(d.n)} of {fmtInt(summary.n_seeds)} seeds
        </span>
      </p>

      <div className="interval" role="img" aria-label={`95 % interval from ${pct(d.ci95[0])} to ${pct(d.ci95[1])}; limit ${pct(thr)}`}>
        <div className="interval-track">
          <span className="interval-band" style={{ left: at(d.ci95[0]), width: `calc(${at(d.ci95[1])} - ${at(d.ci95[0])})` }} />
          <span className="interval-point" style={{ left: at(d.pct) }} />
          <span className="interval-limit" style={{ left: at(thr) }}>
            <span>limit {pct(thr)}</span>
          </span>
        </div>
        <div className="interval-axis" aria-hidden="true">
          <span>0 %</span>
          <span>{pct(max, 0)}</span>
        </div>
      </div>
      <p className="interval-caption">
        95 % interval: {pct(d.ci95[0])} to {pct(d.ci95[1])}. The true share for the whole lot is very likely in this
        range.
      </p>

      <p className="verdict-explain">{noDash(verdict.explanation)}</p>

      {status === "inconclusive" && (
        <p className="verdict-action">
          {more != null && verdict.seeds_needed != null ? (
            <>
              Add about <strong>{fmtInt(more)} more seeds</strong> ({fmtInt(verdict.seeds_needed)} in total) to be sure
              either way.
            </>
          ) : (
            <>Photograph more seeds to be sure either way.</>
          )}
        </p>
      )}
    </section>
  );
}

function StatusIcon({ status }: { status: "pass" | "fail" | "inconclusive" }) {
  return (
    <span className="verdict-icon" aria-hidden="true">
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
        {status === "pass" && <path d="M5 12.5l4.5 4.5L19 7.5" />}
        {status === "fail" && <path d="M6 6l12 12M18 6L6 18" />}
        {status === "inconclusive" && (
          <>
            <path d="M12 7v6" />
            <path d="M12 17.5v.01" />
          </>
        )}
      </svg>
    </span>
  );
}
