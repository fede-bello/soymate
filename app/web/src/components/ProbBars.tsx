import { classColour, classLabel, prob } from "../lib";

interface Props {
  probs: Record<string, number>;
  top?: number;
  compact?: boolean;
  large?: boolean;
}

/** Class probabilities as horizontal bars, highest first. */
export default function ProbBars({ probs, top, compact, large }: Props) {
  const rows = Object.entries(probs)
    .sort((a, b) => b[1] - a[1])
    .slice(0, top ?? undefined);
  return (
    <ul className={`probs${compact ? " probs-compact" : ""}${large ? " probs-large" : ""}`}>
      {rows.map(([c, p]) => (
        <li key={c}>
          <span className="probs-label">{classLabel(c)}</span>
          <span className="probs-track" aria-hidden="true">
            <span className="probs-fill" style={{ width: `${Math.max(0, Math.min(1, p)) * 100}%`, background: classColour(c) }} />
          </span>
          <span className="probs-value">{prob(p)}</span>
        </li>
      ))}
    </ul>
  );
}
