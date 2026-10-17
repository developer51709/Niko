import { navigate } from "../router";
import { Brand } from "./Brand";

export function Footer() {
  return (
    <footer className="site-footer">
      <Brand />
      <span>Built for communities that care.</span>
      <div>
        <a href="/privacy" onClick={(e) => { e.preventDefault(); navigate("/privacy"); }}>Privacy</a>
        <a href="/terms" onClick={(e) => { e.preventDefault(); navigate("/terms"); }}>Terms</a>
        <a href="/community" onClick={(e) => { e.preventDefault(); navigate("/community"); }}>Community Policy</a>
        <a href="/support" onClick={(e) => { e.preventDefault(); navigate("/support"); }}>Support</a>
      </div>
    </footer>
  );
}