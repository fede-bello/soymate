import { useId } from "react";
import type { AnalyzeResult } from "../api";
import { classColour, classHint, classLabel, prob } from "../lib";
import ProbBars from "./ProbBars";
import { largestSeed } from "./scale";

interface Props {
  result: AnalyzeResult;
  imageUrl: string;
}

/** One seed, shown large with the rest of the photo dimmed, plus its class probabilities. */
export default function SingleBean({ result, imageUrl }: Props) {
  const maskId = useId().replace(/:/g, "");
  const { width: W, height: H } = result.image;
  const seed = largestSeed(result);
  const [x1, y1, x2, y2] = seed.bbox;
  const pad = Math.max(x2 - x1, y2 - y1) * 0.35;
  const vx = Math.max(0, x1 - pad);
  const vy = Math.max(0, y1 - pad);
  const vw = Math.min(W, x2 + pad) - vx;
  const vh = Math.min(H, y2 + pad) - vy;
  const points = seed.polygon.map(([x, y]) => `${x},${y}`).join(" ");
  const colour = classColour(seed.class);
  const hint = classHint(seed.class);

  return (
    <div className="single">
      <div className="single-media">
        <svg viewBox={`${vx} ${vy} ${vw} ${vh}`} role="img" aria-label={`Close-up of the seed, judged ${classLabel(seed.class)}`}>
          <defs>
            <mask id={maskId}>
              <rect x={0} y={0} width={W} height={H} fill="white" />
              <polygon points={points} fill="black" />
            </mask>
          </defs>
          <image href={imageUrl} x={0} y={0} width={W} height={H} />
          <rect x={0} y={0} width={W} height={H} fill="#18301F" opacity={0.72} mask={`url(#${maskId})`} />
          <polygon points={points} fill="none" stroke={colour} strokeWidth={3} vectorEffect="non-scaling-stroke" />
        </svg>
      </div>
      <div className="single-info">
        <p className="eyebrow">Single bean</p>
        <p className="single-class">
          <span className="swatch swatch-lg" style={{ ["--c" as string]: colour }} aria-hidden="true" />
          {classLabel(seed.class)}
        </p>
        <p className="single-conf">
          {prob(seed.confidence)} sure{hint ? `: ${hint}` : ""}
        </p>
        <h3 className="sub-title">How likely each class is</h3>
        <ProbBars probs={seed.probs} large />
        {result.seeds.length > 1 && (
          <p className="muted small">
            {result.seeds.length} outlines were found; the largest one is shown. Use Batch mode to grade them all.
          </p>
        )}
      </div>
    </div>
  );
}
