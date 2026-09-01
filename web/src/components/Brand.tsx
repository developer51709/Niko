import { navigate } from "../router";

export function Brand({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <a className="brand" href="/" onClick={(event) => {
      event.preventDefault();
      onNavigate ? onNavigate() : navigate("/");
    }}>
      <span className="brand-mark">n</span>
      <span>niko</span>
    </a>
  );
}