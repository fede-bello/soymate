import { useEffect, useState } from "react";

interface Props {
  imageUrl: string;
  started: number;
  label: string;
}

/** Preview of the photo with a scanning animation and an honest elapsed-time counter. */
export default function Progress({ imageUrl, started, label }: Props) {
  const [now, setNow] = useState(performance.now());
  useEffect(() => {
    const t = setInterval(() => setNow(performance.now()), 250);
    return () => clearInterval(t);
  }, []);
  const s = Math.max(0, (now - started) / 1000);
  return (
    <div className="progress" role="status" aria-live="polite">
      <div className="progress-media">
        <img src={imageUrl} alt={`Photo being analysed: ${label}`} />
        <div className="scan" aria-hidden="true" />
      </div>
      <div className="progress-info">
        <span className="spinner" aria-hidden="true" />
        <div>
          <p className="progress-step">Finding and checking every seed...</p>
          <p className="progress-time">
            {s.toFixed(0)} s elapsed. Usually 3 to 10 s on this server.
          </p>
        </div>
      </div>
      <div className="bar-indeterminate" aria-hidden="true" />
    </div>
  );
}
