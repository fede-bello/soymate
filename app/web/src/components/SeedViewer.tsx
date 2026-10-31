import { useCallback, useEffect, useMemo, useRef, useState, type KeyboardEvent, type PointerEvent, type ReactNode } from "react";
import type { AnalyzeResult, Seed } from "../api";
import { classColour, classLabel, prob } from "../lib";
import ProbBars from "./ProbBars";

interface Props {
  result: AnalyzeResult;
  imageUrl: string;
}

/** The photo with every seed outlined, a class filter, zoom/pan, and an enlarged view. */
export default function SeedViewer({ result, imageUrl }: Props) {
  const [only, setOnly] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [big, setBig] = useState(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const enlargeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    setSelected(null);
    setOnly(null);
  }, [result]);

  useEffect(() => {
    const d = dialogRef.current;
    if (!d) return;
    if (big && !d.open) d.showModal();
    if (!big && d.open) d.close();
  }, [big]);

  const classes = useMemo(() => {
    const present = result.model.classes.filter((c) => (result.summary.classes[c]?.n ?? 0) > 0);
    const extra = Object.keys(result.summary.classes).filter((c) => !present.includes(c) && result.summary.classes[c].n > 0);
    return [...present, ...extra];
  }, [result]);

  const seed = selected != null ? result.seeds.find((s) => s.id === selected) : undefined;
  const nBlobs = result.seeds.filter((s) => s.n_est > 1).length;

  const pane = (inDialog: boolean) => (
    <ZoomPane
      result={result}
      imageUrl={imageUrl}
      only={only}
      selected={selected}
      onSelect={setSelected}
      inDialog={inDialog}
      extra={
        !inDialog && (
          <button
            ref={enlargeRef}
            className="icon-btn"
            onClick={() => setBig(true)}
            aria-label="Enlarge photo"
            title="Enlarge"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />
            </svg>
          </button>
        )
      }
    />
  );

  const legend = (
    <div className="legend" role="group" aria-label="Show one class only">
      <button className="chip" aria-pressed={only === null} onClick={() => setOnly(null)}>
        All seeds
      </button>
      {classes.map((c) => (
        <button
          key={c}
          className="chip"
          aria-pressed={only === c}
          onClick={() => setOnly(only === c ? null : c)}
          style={{ ["--c" as string]: classColour(c) }}
        >
          <span className="swatch" aria-hidden="true" />
          {classLabel(c)} <span className="chip-n">{result.summary.classes[c]?.n}</span>
        </button>
      ))}
    </div>
  );

  return (
    <figure className="viewer-fig">
      {legend}
      {pane(false)}
      <figcaption className="viewer-caption" aria-live="polite">
        {seed ? (
          <SeedDetails seed={seed} onClose={() => setSelected(null)} />
        ) : (
          <p className="muted">
            {result.seeds.length} outlines, {result.summary.n_seeds} seeds counted
            {nBlobs > 0 ? `; ${nBlobs} outlines marked xN are touching seeds counted as N` : ""}. Hover or tap a seed for
            details. Pinch, Ctrl + scroll or the + button to zoom.
          </p>
        )}
      </figcaption>

      <dialog
        ref={dialogRef}
        className="viewer-dialog"
        onClose={() => {
          setBig(false);
          enlargeRef.current?.focus();
        }}
        aria-label="Enlarged photo"
      >
        {big && (
          <div className="viewer-dialog-inner">
            <div className="viewer-dialog-head">
              {legend}
              <button className="btn" onClick={() => setBig(false)} autoFocus>
                Close
              </button>
            </div>
            {pane(true)}
            {seed && (
              <div className="viewer-dialog-foot">
                <SeedDetails seed={seed} onClose={() => setSelected(null)} />
              </div>
            )}
          </div>
        )}
      </dialog>
    </figure>
  );
}

function SeedDetails({ seed, onClose }: { seed: Seed; onClose: () => void }) {
  return (
    <div className="seed-details">
      <div className="seed-details-head">
        <span className="swatch" style={{ ["--c" as string]: classColour(seed.class) }} aria-hidden="true" />
        <strong>{classLabel(seed.class)}</strong>
        <span className="muted">
          seed #{seed.id}, {prob(seed.confidence)} sure
          {seed.n_est > 1 ? `, counted as ${seed.n_est} touching seeds` : ""}
        </span>
        <button className="btn btn-small" onClick={onClose}>
          Clear
        </button>
      </div>
      <ProbBars probs={seed.probs} top={4} />
    </div>
  );
}

interface PaneProps {
  result: AnalyzeResult;
  imageUrl: string;
  only: string | null;
  selected: number | null;
  onSelect: (id: number | null) => void;
  inDialog: boolean;
  extra?: ReactNode;
}

type View = { k: number; x: number; y: number };
const MAX_K = 8;

function ZoomPane({ result, imageUrl, only, selected, onSelect, inDialog, extra }: PaneProps) {
  const { width: W, height: H } = result.image;
  const ref = useRef<HTMLDivElement>(null);
  const [view, setView] = useState<View>({ k: 1, x: 0, y: 0 });
  const [hover, setHover] = useState<{ id: number; x: number; y: number } | null>(null);
  const pointers = useRef(new Map<number, { x: number; y: number }>());
  const gesture = useRef<{ moved: number; targetId: number | null; pinch?: number } | null>(null);

  const shapes = useMemo(() => {
    const hs = result.seeds.map((s) => s.bbox[3] - s.bbox[1]).sort((a, b) => a - b);
    const median = hs[Math.floor(hs.length / 2)] || Math.min(W, H) / 20;
    return {
      font: Math.max(10, median * 0.55),
      seeds: result.seeds.map((s) => ({
        s,
        points: s.polygon.map(([x, y]) => `${x},${y}`).join(" "),
        cx: (s.bbox[0] + s.bbox[2]) / 2,
        cy: (s.bbox[1] + s.bbox[3]) / 2,
        colour: classColour(s.class),
      })),
    };
  }, [result, W, H]);

  useEffect(() => setView({ k: 1, x: 0, y: 0 }), [result]);

  const clamp = useCallback((v: View): View => {
    const el = ref.current;
    if (!el) return v;
    const k = Math.min(MAX_K, Math.max(1, v.k));
    const cw = el.clientWidth;
    const ch = el.clientHeight;
    return { k, x: Math.min(0, Math.max(cw - cw * k, v.x)), y: Math.min(0, Math.max(ch - ch * k, v.y)) };
  }, []);

  const zoomAt = useCallback(
    (factor: number, px?: number, py?: number) => {
      const el = ref.current;
      if (!el) return;
      const cx = px ?? el.clientWidth / 2;
      const cy = py ?? el.clientHeight / 2;
      setView((v) => {
        const k = Math.min(MAX_K, Math.max(1, v.k * factor));
        const r = k / v.k;
        return clamp({ k, x: cx - (cx - v.x) * r, y: cy - (cy - v.y) * r });
      });
    },
    [clamp],
  );

  // Ctrl/Cmd + wheel (and trackpad pinch) zooms; a plain wheel keeps scrolling the page.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      if (!(e.ctrlKey || e.metaKey) && !inDialog) return;
      e.preventDefault();
      const r = el.getBoundingClientRect();
      zoomAt(Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.002)), e.clientX - r.left, e.clientY - r.top);
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [zoomAt, inDialog]);

  const local = (e: PointerEvent) => {
    const r = ref.current!.getBoundingClientRect();
    return { x: e.clientX - r.left, y: e.clientY - r.top };
  };
  const seedIdOf = (t: EventTarget | null) => {
    const id = (t as Element | null)?.getAttribute?.("data-id");
    return id ? Number(id) : null;
  };

  const onPointerDown = (e: PointerEvent) => {
    if (e.button !== 0) return;
    pointers.current.set(e.pointerId, local(e));
    if (pointers.current.size === 1) gesture.current = { moved: 0, targetId: seedIdOf(e.target) };
    if (pointers.current.size === 2) {
      const [a, b] = [...pointers.current.values()];
      gesture.current = { moved: 99, targetId: null, pinch: Math.hypot(a.x - b.x, a.y - b.y) };
    }
    (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
  };

  const onPointerMove = (e: PointerEvent) => {
    const p = local(e);
    const prev = pointers.current.get(e.pointerId);
    if (!prev) {
      // Hover (mouse or pen, no button down).
      const id = seedIdOf(e.target);
      if (e.pointerType !== "touch") setHover(id != null ? { id, x: p.x, y: p.y } : null);
      return;
    }
    pointers.current.set(e.pointerId, p);
    const g = gesture.current;
    if (!g) return;
    if (pointers.current.size === 2 && g.pinch) {
      const [a, b] = [...pointers.current.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      zoomAt(d / g.pinch, (a.x + b.x) / 2, (a.y + b.y) / 2);
      g.pinch = d;
      return;
    }
    const dx = p.x - prev.x;
    const dy = p.y - prev.y;
    g.moved += Math.abs(dx) + Math.abs(dy);
    if (g.moved > 4) {
      setHover(null);
      setView((v) => clamp({ ...v, x: v.x + dx, y: v.y + dy }));
    }
  };

  const onPointerUp = (e: PointerEvent) => {
    const g = gesture.current;
    pointers.current.delete(e.pointerId);
    if (pointers.current.size === 0) {
      if (g && g.moved <= 4 && e.type === "pointerup") {
        const id = g.targetId;
        onSelect(id === selected ? null : id);
      }
      gesture.current = null;
    }
  };

  const onKeyDown = (e: KeyboardEvent) => {
    const step = 40;
    const keys: Record<string, () => void> = {
      "+": () => zoomAt(1.4),
      "=": () => zoomAt(1.4),
      "-": () => zoomAt(1 / 1.4),
      "0": () => setView({ k: 1, x: 0, y: 0 }),
      ArrowLeft: () => setView((v) => clamp({ ...v, x: v.x + step })),
      ArrowRight: () => setView((v) => clamp({ ...v, x: v.x - step })),
      ArrowUp: () => setView((v) => clamp({ ...v, y: v.y + step })),
      ArrowDown: () => setView((v) => clamp({ ...v, y: v.y - step })),
    };
    const f = keys[e.key];
    if (f && (view.k > 1 || !e.key.startsWith("Arrow"))) {
      e.preventDefault();
      f();
    }
  };

  const hovered = hover ? result.seeds.find((s) => s.id === hover.id) : undefined;
  const el = ref.current;
  const tipLeft = hover && el ? Math.min(hover.x + 14, el.clientWidth - 260) : 0;
  const tipTop = hover && el ? (hover.y > el.clientHeight - 150 ? hover.y - 140 : hover.y + 14) : 0;

  return (
    <div className={`pane${inDialog ? " pane-dialog" : ""}`}>
      <div
        ref={ref}
        className={`viewport${view.k > 1 ? " is-zoomed" : ""}`}
        style={{ aspectRatio: `${W} / ${H}`, ["--ar" as string]: W / H }}
        tabIndex={0}
        role="group"
        aria-roledescription="zoomable photo"
        aria-label={`Photo with ${result.seeds.length} seed outlines coloured by class. Use plus and minus to zoom, arrows to move.`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerCancel={onPointerUp}
        onPointerLeave={() => setHover(null)}
        onDoubleClick={(e) => {
          const r = ref.current!.getBoundingClientRect();
          if (view.k >= MAX_K / 2) setView({ k: 1, x: 0, y: 0 });
          else zoomAt(2, e.clientX - r.left, e.clientY - r.top);
        }}
        onKeyDown={onKeyDown}
      >
        <div
          className="viewport-content"
          style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.k})` }}
        >
          <img src={imageUrl} alt="" draggable={false} />
          <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" aria-hidden="true">
            {shapes.seeds.map(({ s, points, colour }) => {
              const dim = only !== null && s.class !== only;
              const cls = `seed${dim ? " is-dim" : ""}${s.n_est > 1 ? " is-multi" : ""}${
                selected === s.id ? " is-selected" : ""
              }${hover?.id === s.id ? " is-hover" : ""}`;
              return (
                <g key={s.id} className={cls} style={{ ["--c" as string]: colour }}>
                  <polygon className="seed-halo" points={points} vectorEffect="non-scaling-stroke" />
                  <polygon className="seed-line" points={points} data-id={s.id} vectorEffect="non-scaling-stroke" />
                </g>
              );
            })}
            {shapes.seeds
              .filter(({ s }) => s.n_est > 1 && (only === null || s.class === only))
              .map(({ s, cx, cy }) => (
                <text key={`t${s.id}`} x={cx} y={cy} className="seed-mult" fontSize={shapes.font / Math.sqrt(view.k)}>
                  x{s.n_est}
                </text>
              ))}
          </svg>
        </div>

        {hovered && hover && (
          <div className="tip" style={{ left: tipLeft, top: tipTop }} aria-hidden="true">
            <div className="tip-head">
              <span className="swatch" style={{ ["--c" as string]: classColour(hovered.class) }} />
              <strong>{classLabel(hovered.class)}</strong>
              <span>{prob(hovered.confidence)}</span>
            </div>
            {hovered.n_est > 1 && <p className="tip-note">Counted as {hovered.n_est} touching seeds</p>}
            <ProbBars probs={hovered.probs} top={3} compact />
          </div>
        )}
      </div>

      <div className="pane-tools">
        <button className="icon-btn" onClick={() => zoomAt(1.5)} aria-label="Zoom in" title="Zoom in" disabled={view.k >= MAX_K}>
          +
        </button>
        <button className="icon-btn" onClick={() => zoomAt(1 / 1.5)} aria-label="Zoom out" title="Zoom out" disabled={view.k <= 1}>
          &minus;
        </button>
        <button
          className="icon-btn"
          onClick={() => setView({ k: 1, x: 0, y: 0 })}
          aria-label="Reset zoom"
          title="Reset zoom"
          disabled={view.k === 1}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
            <path d="M3 3v5h5" />
          </svg>
        </button>
        {extra}
      </div>
    </div>
  );
}
