import { useId } from "react";
import type { Mode } from "../api";
import { classLabel } from "../lib";

interface Props {
  mode: Mode;
  onMode: (m: Mode) => void;
  threshold: number;
  onThreshold: (t: number) => void;
  defect: string;
  onDefect: (d: string) => void;
  defectClasses: string[];
}

const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: "auto", label: "Auto", hint: "picks single bean when one seed fills the photo" },
  { id: "single", label: "Single bean", hint: "one seed, close up" },
  { id: "batch", label: "Batch", hint: "a sample with many seeds" },
  { id: "bulk", label: "Bulk (experimental)", hint: "seeds packed edge to edge, as on a harvester camera; about 5 % count error" },
];

export default function Settings(p: Props) {
  const id = useId();
  const modeHint = MODES.find((m) => m.id === p.mode)?.hint;
  return (
    <section className="card settings" aria-labelledby={`${id}-t`}>
      <h2 id={`${id}-t`} className="card-title">
        Settings
      </h2>

      <fieldset className="field">
        <legend>Photo type</legend>
        <div className="segmented" role="radiogroup">
          {MODES.map((m) => (
            <label key={m.id} className={p.mode === m.id ? "is-on" : undefined}>
              <input
                type="radio"
                name={`${id}-mode`}
                value={m.id}
                checked={p.mode === m.id}
                onChange={() => p.onMode(m.id)}
              />
              <span>{m.label}</span>
            </label>
          ))}
        </div>
        <p className="field-hint">{modeHint}</p>
      </fieldset>

      <div className="field">
        <div className="field-row">
          <label htmlFor={`${id}-thr`}>Defect limit</label>
          <output htmlFor={`${id}-thr`} className="thr-value">
            {p.threshold} %
          </output>
        </div>
        <input
          id={`${id}-thr`}
          type="range"
          min={0.5}
          max={20}
          step={0.5}
          value={p.threshold}
          onChange={(e) => p.onThreshold(Number(e.target.value))}
          aria-describedby={`${id}-thr-h`}
          aria-valuetext={`${p.threshold} percent`}
          style={{ ["--fill" as string]: `${((p.threshold - 0.5) / 19.5) * 100}%` }}
        />
        <p className="field-hint" id={`${id}-thr-h`}>
          Illustrative: the highest share of defective seeds a lot may have and still pass. Real limits depend on the contract.
        </p>
      </div>

      <div className="field">
        <label htmlFor={`${id}-def`}>Which defect counts</label>
        <select id={`${id}-def`} value={p.defect} onChange={(e) => p.onDefect(e.target.value)}>
          <option value="any">Any defect (everything except sound)</option>
          {p.defectClasses.map((c) => (
            <option key={c} value={c}>
              {classLabel(c)} only
            </option>
          ))}
        </select>
      </div>
    </section>
  );
}
