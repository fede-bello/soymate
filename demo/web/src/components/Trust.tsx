import { useEffect, useState } from "react";
import { getApi, type Evidence } from "../api";

const GLOSSARY: { term: string; text: string }[] = [
  { term: "95 % interval", text: "the range the true value very likely falls in; a narrow range means a sure answer." },
  { term: "F1 score", text: "how well a class is found, from 0 to 1: it drops both for missed seeds and for false alarms." },
  { term: "Macro F1", text: "the F1 score averaged over all classes, so rare classes count as much as common ones." },
  { term: "pp (percentage points)", text: "the gap between two percentages: from 5 % to 8 % is 3 pp." },
  { term: "Wilson interval", text: "a standard way to compute the 95 % interval of a share from a count of seeds." },
  { term: "Burst / session", text: "photos shot within seconds of each other, or on the same day; kept together so tests are fair." },
  { term: "Probe", text: "a small test model trained on top of the image features to see what they contain." },
  { term: "MAE", text: "mean absolute error: the average size of the mistake, ignoring its direction." },
  { term: "Held-out", text: "photos kept aside and never shown to the model while it learned." },
  { term: "Leakage", text: "when test photos are near copies of training photos, which makes a model look better than it is." },
];

const noDash = (s?: string | null) => (s ?? "").replace(/\s*\u2014\s*/g, ", ");

export default function Trust() {
  const [data, setData] = useState<Evidence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let live = true;
    setError(null);
    getApi()
      .then((api) => api.evidence())
      .then((d) => live && setData(d))
      .catch((e: Error) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [attempt]);

  return (
    <div className="page">
      <section className="intro" aria-labelledby="trust-title">
        <p className="eyebrow">Evidence</p>
        <h1 id="trust-title">How much to trust it</h1>
        <p>
          Every number below was measured at the event by a script in our repository, on photos the model never saw
          while learning. Each card says what we tested, what we found, and what it does not prove.
        </p>
      </section>

      <details className="glossary card">
        <summary>Words used on this page</summary>
        <dl>
          {GLOSSARY.map((g) => (
            <div key={g.term}>
              <dt>{g.term}</dt>
              <dd>{g.text}</dd>
            </div>
          ))}
        </dl>
      </details>

      {error && (
        <div className="error-card" role="alert">
          <h2>Evidence could not be loaded</h2>
          <p>{error}</p>
          <button className="btn btn-primary" onClick={() => setAttempt((a) => a + 1)}>
            Try again
          </button>
        </div>
      )}

      {!data && !error && (
        <div className="evidence-grid" aria-busy="true" aria-label="Loading evidence">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="card evidence skeleton skeleton-tall" />
          ))}
        </div>
      )}

      {data && (
        <>
          <ul className="evidence-grid">
            {data.cards.map((c) => (
              <li key={c.id} className="card evidence">
                <h2 className="evidence-title">{noDash(c.title)}</h2>
                <p className="evidence-headline">{noDash(c.headline)}</p>
                {c.numbers?.length > 0 && (
                  <dl className="evidence-numbers">
                    {c.numbers.map((n, i) => (
                      <div key={i}>
                        <dt>{noDash(n.label)}</dt>
                        <dd>
                          <span className="evidence-value">{n.value}</span>
                          {n.ci95 && <span className="evidence-ci">95 % interval {n.ci95}</span>}
                        </dd>
                      </div>
                    ))}
                  </dl>
                )}
                {c.caveat && (
                  <p className="evidence-caveat">
                    <strong>Caveat:</strong> {noDash(c.caveat)}
                  </p>
                )}
                {c.source && (
                  <p className="evidence-source">
                    Source: <code>{c.source}</code>
                  </p>
                )}
              </li>
            ))}
          </ul>
          {data.provenance_url && (
            <p className="provenance">
              <a href={data.provenance_url} target="_blank" rel="noreferrer">
                How each number was produced (provenance)
              </a>
            </p>
          )}
        </>
      )}
    </div>
  );
}
