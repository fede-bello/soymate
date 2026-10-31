import { useEffect, useState } from "react";
import { getApi, type Example } from "../api";

interface Props {
  onPick: (ex: Example) => void;
  loadingId: string | null;
  disabled?: boolean;
}

export default function Examples({ onPick, loadingId, disabled }: Props) {
  const [items, setItems] = useState<Example[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let live = true;
    setError(null);
    getApi()
      .then((api) => api.examples())
      .then((xs) => live && setItems(xs))
      .catch((e: Error) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [attempt]);

  return (
    <section className="examples" aria-labelledby="examples-title">
      <div className="section-head">
        <h2 id="examples-title">Or try a sample photo</h2>
        <p>Held-out photos the model never trained on.</p>
      </div>
      {error && (
        <div className="notice notice-warn" role="alert">
          <span>Sample photos could not be loaded: {error}</span>
          <button className="btn btn-small" onClick={() => setAttempt((a) => a + 1)}>
            Retry
          </button>
        </div>
      )}
      {!items && !error && (
        <div className="example-grid" aria-hidden="true">
          {[0, 1, 2].map((i) => (
            <div key={i} className="example-card skeleton" />
          ))}
        </div>
      )}
      {items && items.length === 0 && <p className="muted">No sample photos on this server.</p>}
      {items && items.length > 0 && (
        <ul className="example-grid">
          {items.map((ex) => (
            <li key={ex.id}>
              <button
                className="example-card"
                onClick={() => onPick(ex)}
                disabled={disabled || loadingId !== null}
                aria-busy={loadingId === ex.id}
              >
                <span className="example-thumb">
                  <img
                    src={ex.thumb_url ?? ex.url}
                    alt=""
                    loading="lazy"
                    decoding="async"
                    onError={(e) => (e.currentTarget.style.visibility = "hidden")}
                  />
                  <span className={`badge badge-${ex.kind}`}>{ex.kind === "single" ? "Single bean" : ex.kind === "bulk" ? "Bulk" : "Batch"}</span>
                  {loadingId === ex.id && (
                    <span className="example-loading">
                      <span className="spinner" aria-hidden="true" /> Loading
                    </span>
                  )}
                </span>
                <span className="example-body">
                  <span className="example-label">{ex.label}</span>
                  {ex.note && <span className="example-note">{ex.note}</span>}
                  <span className="example-dataset">{ex.dataset}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
