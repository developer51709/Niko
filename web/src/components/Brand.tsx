import { useBotConfig } from "../hooks/useBotConfig";
import { navigate } from "../router";

export function Brand({ onNavigate }: { onNavigate?: () => void }) {
  const config = useBotConfig();

  return (
    <a className="brand" href="/" onClick={(event) => {
      event.preventDefault();
      onNavigate ? onNavigate() : navigate("/");
    }}>
      <span className="brand-mark">
        {config?.bot_avatar_url ? (
          <img src={config.bot_avatar_url} alt="Niko" />
        ) : (
          "n"
        )}
      </span>
      <span>niko</span>
    </a>
  );
}
