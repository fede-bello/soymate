import { useEffect, useState } from "react";
import { getApi, IS_MOCK, type Health } from "./api";
import mark from "./assets/mark.webp";
import Analyze from "./components/Analyze";
import Trust from "./components/Trust";
import About from "./components/About";

type Route = "analyze" | "trust" | "about";
const ROUTES: { id: Route; label: string }[] = [
  { id: "analyze", label: "Analyze" },
  { id: "trust", label: "How much to trust it" },
  { id: "about", label: "About" },
];

function readRoute(): Route {
  const h = window.location.hash.replace(/^#\/?/, "");
  return (ROUTES.find((r) => r.id === h)?.id ?? "analyze") as Route;
}

export default function App() {
  const [route, setRoute] = useState<Route>(readRoute);
  const [health, setHealth] = useState<Health | null | "down">(null);

  useEffect(() => {
    const onHash = () => {
      setRoute(readRoute());
      window.scrollTo({ top: 0 });
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    getApi()
      .then((api) => api.health())
      .then(setHealth)
      .catch(() => setHealth("down"));
  }, []);

  useEffect(() => {
    const label = ROUTES.find((r) => r.id === route)?.label;
    document.title = route === "analyze" ? "SoyMate: seed grade from a photo" : `${label} | SoyMate`;
  }, [route]);

  return (
    <div className="app">
      <a className="skip" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <div className="topbar-inner">
          <a className="brand" href="#/analyze" aria-label="SoyMate, home">
            <img src={mark} alt="" width={40} height={40} />
            <span>SoyMate</span>
            {IS_MOCK && <span className="mock-badge">Mock data</span>}
          </a>
          <nav aria-label="Main">
            <ul>
              {ROUTES.map((r) => (
                <li key={r.id}>
                  <a href={`#/${r.id}`} aria-current={route === r.id ? "page" : undefined}>
                    {r.label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>

      <main id="main" tabIndex={-1}>
        {/* Analyze stays mounted so a result survives a visit to the other tabs. */}
        <div hidden={route !== "analyze"}>
          <Analyze />
        </div>
        {route === "trust" && <Trust />}
        {route === "about" && <About />}
      </main>

      <footer className="footer">
        <div className="footer-inner">
          <span>SoyMate, Hack the Fork Paris 2026. Proof of concept on soybean, business case on lentil.</span>
          <span className="footer-status" aria-live="polite">
            {health === null && "Checking server..."}
            {health === "down" && <span className="dot dot-down">Server not reachable</span>}
            {health && health !== "down" && (
              <span className="dot dot-ok">
                Model {health.model}
                {health.version ? `, ${health.version}` : ""}
              </span>
            )}
          </span>
        </div>
      </footer>
    </div>
  );
}
