import { useId, useRef, useState, type DragEvent } from "react";

interface Props {
  onFile: (f: File) => void;
  big?: boolean;
  compact?: boolean;
}

/** Drag and drop, file picker, and camera (on phones) for one photo. */
export default function Dropzone({ onFile, big, compact }: Props) {
  const [over, setOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const camRef = useRef<HTMLInputElement>(null);
  const hintId = useId();

  const take = (files: FileList | null) => {
    const f = files?.[0];
    if (f) onFile(f);
  };
  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setOver(false);
    take(e.dataTransfer.files);
  };

  const inputs = (
    <>
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        className="visually-hidden"
        tabIndex={-1}
        aria-hidden="true"
        onChange={(e) => {
          take(e.target.files);
          e.target.value = "";
        }}
      />
      <input
        ref={camRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="visually-hidden"
        tabIndex={-1}
        aria-hidden="true"
        onChange={(e) => {
          take(e.target.files);
          e.target.value = "";
        }}
      />
    </>
  );

  if (compact) {
    return (
      <div className="drop-compact">
        {inputs}
        <button className="btn" onClick={() => fileRef.current?.click()}>
          <UploadIcon /> New photo
        </button>
        <button className="btn only-touch" onClick={() => camRef.current?.click()}>
          <CameraIcon /> Take a photo
        </button>
      </div>
    );
  }

  return (
    <div
      className={`dropzone${big ? " dropzone-big" : ""}${over ? " is-over" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setOver(true);
      }}
      onDragLeave={() => setOver(false)}
      onDrop={onDrop}
    >
      {inputs}
      <div className="dropzone-icon" aria-hidden="true">
        <UploadIcon size={big ? 40 : 28} />
      </div>
      <p className="dropzone-title">{big ? "Drop a photo of your seeds here" : "Drop another photo here"}</p>
      <p className="dropzone-hint" id={hintId}>
        JPEG or PNG, up to 15 MB. Seeds spread out on a plain background work best.
      </p>
      <div className="row gap center wrap">
        <button className="btn btn-primary" aria-describedby={hintId} onClick={() => fileRef.current?.click()}>
          <UploadIcon /> Choose a photo
        </button>
        <button className="btn only-touch" onClick={() => camRef.current?.click()}>
          <CameraIcon /> Take a photo
        </button>
      </div>
    </div>
  );
}

function UploadIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 16V4M7 9l5-5 5 5" />
      <path d="M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3" />
    </svg>
  );
}

function CameraIcon({ size = 18 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z" />
      <circle cx="12" cy="13.5" r="3.5" />
    </svg>
  );
}
