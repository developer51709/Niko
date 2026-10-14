import type { ReactNode } from "react";
import { navigate } from "../router";

/**
 * Inline link to the website's `/discord` page.
 *
 * That page resolves the current support-server invite from the live bot config,
 * so it keeps working after an invite is rotated or expires. Never hardcode a
 * discord.gg invite URL in user-facing copy.
 */
export function SupportLink({ children = "support server" }: { children?: ReactNode }) {
  return (
    <a
      href="/discord"
      onClick={(event) => {
        event.preventDefault();
        navigate("/discord");
      }}
    >
      {children}
    </a>
  );
}
