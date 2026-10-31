import type { AnalyzeResult, ClassShare } from "../api";
import { classColour, classHint, classLabel, fmtInt, pct } from "../lib";
import { clamp01, niceMax } from "./scale";

/** Count, share and 95 % interval per class. Sound has its own 0-100 % scale; defects share a zoomed scale. */
export default function Breakdown({ result }: { result: AnalyzeResult }) {
  if (result.mode === "single") return null;
  const all = result.summary.classes;
  const order = [...result.model.classes, ...Object.keys(all).filter((c) => !result.model.classes.includes(c))].filter(
    (c) => all[c],
  );
  const sound = order.filter((c) => c === "sound");
  const defects = order.filter((c) => c !== "sound");
  const defMax = niceMax(Math.max(1, ...defects.map((c) => all[c].ci95[1])) * 1.1);

  return (
    <section className="card breakdown" aria-labelledby="bd-title">
      <h2 id="bd-title" className="card-title">
        What is in the sample
      </h2>
      <p className="muted small">
        {fmtInt(result.summary.n_seeds)} seeds. Bars show the 95 % interval; the dot is the measured share.
      </p>
      {sound.length > 0 && (
        <table className="bd-table">
          <caption className="visually-hidden">Sound seeds</caption>
          <tbody>
            {sound.map((c) => (
              <Row key={c} c={c} s={all[c]} max={100} />
            ))}
          </tbody>
        </table>
      )}
      {defects.length > 0 && (
        <>
          <div className="bd-subhead">
            <span>Defects</span>
            <span className="muted small">scale 0 to {pct(defMax, 0)}</span>
          </div>
          <table className="bd-table">
            <caption className="visually-hidden">Defect classes, on a scale from 0 to {pct(defMax, 0)}</caption>
            <thead className="visually-hidden">
              <tr>
                <th>Class</th>
                <th>Seeds</th>
                <th>Share</th>
                <th>95 % interval</th>
              </tr>
            </thead>
            <tbody>
              {defects.map((c) => (
                <Row key={c} c={c} s={all[c]} max={defMax} />
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}

function Row({ c, s, max }: { c: string; s: ClassShare; max: number }) {
  const at = (v: number) => clamp01(v / max) * 100;
  const hint = classHint(c);
  return (
    <tr className={s.n === 0 ? "is-zero" : undefined}>
      <th scope="row">
        <span className="swatch" style={{ ["--c" as string]: classColour(c) }} aria-hidden="true" />
        <span className="bd-name">
          {classLabel(c)}
          {hint && <span className="bd-hint">{hint}</span>}
        </span>
      </th>
      <td className="bd-n">{fmtInt(s.n)}</td>
      <td className="bd-pct">{pct(s.pct)}</td>
      <td className="bd-bar">
        <span className="visually-hidden">
          {pct(s.ci95[0])} to {pct(s.ci95[1])}
        </span>
        <span className="ci-track" aria-hidden="true" title={`95 % interval ${pct(s.ci95[0])} to ${pct(s.ci95[1])}`}>
          <span
            className="ci-band"
            style={{ left: `${at(s.ci95[0])}%`, width: `${Math.max(0.8, at(s.ci95[1]) - at(s.ci95[0]))}%`, background: classColour(c) }}
          />
          <span className="ci-dot" style={{ left: `${at(s.pct)}%` }} />
        </span>
      </td>
    </tr>
  );
}
