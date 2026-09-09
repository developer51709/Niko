import { navigate } from "../router";
import { Brand } from "./Brand";

export function Footer() {
  return (
    <footer className="site-footer">
      <Brand />
      <span>Built for communities that care.</span>
      <div>
        <a href="/changelog" onClick={(e) => { e.preventDefault(); navigate("/changelog"); }}>Changelog</a>
        <a href="/privacy" onClick={(e) => { e.preventDefault(); navigate("/privacy"); }}>Privacy</a>
        <a href="/terms" onClick={(e) => { e.preventDefault(); navigate("/terms"); }}>Terms</a>
        <a href="/community" onClick={(e) => { e.preventDefault(); navigate("/community"); }}>Community Policy</a>
        <a href="https://github.com/developer51709/Niko" target="_blank" rel="noreferrer">GitHub</a>
      </div>
    </footer>
  );
}