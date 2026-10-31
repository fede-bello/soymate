import logo from "../assets/logo-360.webp";

const STEPS = [
  { t: "Photo", d: "A phone photo of a seed sample on a plain background." },
  { t: "Find", d: "Every seed is found and outlined, including touching ones." },
  { t: "Check", d: "Each seed is classified: sound, broken, stained, immature, insect hole or impurity." },
  { t: "Share", d: "The share of each class, with a 95 % interval that says how sure it is." },
  { t: "Answer", d: "Pass, add more seeds, or fail, against the limit you choose." },
];

const DATA = [
  {
    name: "A dataset for soybean seed infestation and quality damage",
    who: "Shinde, Nagale, Abin, Joshi, Parashar, Mendeley Data",
    id: "d97rjyk2tz",
    url: "https://data.mendeley.com/datasets/d97rjyk2tz",
  },
  {
    name: "Soybean Seeds (5 classes)",
    who: "Lin et al., Mendeley Data",
    id: "v6vzvfszj6",
    url: "https://data.mendeley.com/datasets/v6vzvfszj6",
  },
  {
    name: "Mechanical-harvest soybean damage segmentation",
    who: "Mendeley Data",
    id: "hwdtghttp7",
    url: "https://data.mendeley.com/datasets/hwdtghttp7",
  },
  {
    name: "Ghana seed varieties (soybean photos)",
    who: "Mendeley Data",
    id: "t94nzy4ptz",
    url: "https://data.mendeley.com/datasets/t94nzy4ptz",
  },
];

export default function About() {
  return (
    <div className="page about">
      <section className="about-hero">
        <div>
          <p className="eyebrow">About</p>
          <h1>A seed grade from a phone photo, that the farmer can check too</h1>
          <p>
            At intake, damaged seeds are still counted by eye on a small sample. SoyMate makes that count fast, the same
            every time, and visible to both sides of the sale. It never hides how sure it is: when the photo has too few
            seeds to decide, it says so and asks for more.
          </p>
        </div>
        <img src={logo} alt="SoyMate logo: a smiling soybean in a mate gourd" width={240} height={240} />
      </section>

      <section aria-labelledby="how-title">
        <h2 id="how-title" className="section-title">
          What it does
        </h2>
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li key={s.t} className="card step">
              <span className="step-n" aria-hidden="true">
                {i + 1}
              </span>
              <h3>{s.t}</h3>
              <p>{s.d}</p>
            </li>
          ))}
        </ol>
      </section>

      <div className="about-two">
        <section className="card" aria-labelledby="cant-title">
          <h2 id="cant-title" className="card-title">
            What it cannot see
          </h2>
          <ul className="list">
            <li>
              <strong>Larvae hidden inside a seed.</strong> A beetle grows inside the seed before it leaves an exit hole.
              A photo of the outside cannot see it, and neither can the visual count used today: cutting seeds open
              finds more damage than looking.
            </li>
            <li>
              <strong>New cameras and lighting.</strong> The model learned from public photos taken with a few setups.
              On a new setup the class shares are not calibrated until it is checked against graders.
            </li>
            <li>
              <strong>Other crops.</strong> It knows soybean only. Lentil needs its own labelled photos.
            </li>
          </ul>
        </section>

        <section className="card about-case" aria-labelledby="case-title">
          <h2 id="case-title" className="card-title">
            Proof of concept on soybean, business case on lentil
          </h2>
          <p>
            Soybean is the only bean with public photos of damaged seeds labelled by type, so that is where we could
            build and test the method. Lentil is where the money is: the gap between food and feed prices, and the
            damage in recent French harvests, make the grade matter.
          </p>
          <p>
            Next step: French lentil photos labelled by graders, checked against the visual reference count, and a trial
            with one cooperative over one harvest.
          </p>
        </section>
      </div>

      <section aria-labelledby="credits-title">
        <h2 id="credits-title" className="section-title">
          Data credits
        </h2>
        <p className="muted">
          All datasets are published under the{" "}
          <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer">
            Creative Commons Attribution 4.0 (CC BY 4.0)
          </a>{" "}
          licence. Changes: we removed duplicates, re-split them by photo session, cropped each seed and masked the
          background.
        </p>
        <ul className="credits">
          {DATA.map((d) => (
            <li key={d.id} className="card credit">
              <a href={d.url} target="_blank" rel="noreferrer" className="credit-name">
                {d.name}
              </a>
              <span className="muted small">
                {d.who}, <code>{d.id}</code>, CC BY 4.0
              </span>
            </li>
          ))}
        </ul>
        <p className="muted small">
          Image features: DINOv2 (Meta AI, Apache 2.0), frozen, with a simple classifier on top. Built at Hack the Fork
          Paris 2026, Track 3.
        </p>
      </section>
    </div>
  );
}
