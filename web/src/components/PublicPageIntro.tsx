import type { ReactNode, MouseEvent } from "react";
import { useBotConfig } from "../hooks/useBotConfig";
import { navigate } from "../router";
import { Icon } from "./Icon";

interface PublicPageIntroProps {
  eyebrow: string;
  title: ReactNode;
  description: string;
}

export function PublicPageIntro({ eyebrow, title, description }: PublicPageIntroProps) {
  const config = useBotConfig();
  const openDashboard = (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    navigate("/dashboard");
  };

  return (
    <section className="public-page-intro">
      <div className="public-page-intro-copy">
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <div className="public-page-intro-actions">
        <a className="button button-primary" href={config?.invite_url || "#"} target="_blank" rel="noreferrer">
          Add Niko to Discord <Icon name="arrow" />
        </a>
        <a className="button button-muted" href="/dashboard" onClick={openDashboard}>
          Open dashboard
        </a>
      </div>
    </section>
  );
}
