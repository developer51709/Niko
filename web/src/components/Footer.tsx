import { useStrings } from "../i18n";
import { navigate } from "../router";
import { Brand } from "./Brand";

// Labels are catalogue keys, not copy: the shared catalogue owns the wording so
// the footer changes language with the navigation above it.
const policies = [
  { key: "footer.privacy", path: "/privacy" },
  { key: "footer.terms", path: "/terms" },
  { key: "footer.dataRemoval", path: "/data-removal" },
  { key: "footer.community", path: "/community" },
  { key: "footer.support", path: "/support" },
];

export function Footer() {
  const { t } = useStrings("shared");

  return (
    <footer className="site-footer">
      <Brand />
      <span>{t("footer.tagline")}</span>
      <div>
        {policies.map((policy) => (
          <a
            key={policy.path}
            href={policy.path}
            onClick={(e) => { e.preventDefault(); navigate(policy.path); }}
          >
            {t(policy.key)}
          </a>
        ))}
      </div>
    </footer>
  );
}
