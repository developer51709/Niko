import { useStrings } from "../i18n";
import type { StaffEmailMessage } from "../types";

/**
 * A mail body as its author laid it out: the same markup the recipient's own
 * client renders, formatting, tables, images and signature included. The server
 * sanitizes that markup before storing it, so only a letter's own shapes reach
 * the page. A reply's quoted history stays folded behind a control, the way an
 * inbox hides it, because the reply is what is being read.
 */
export function EmailMessageBody({ message }: { message: StaffEmailMessage }) {
  const { t } = useStrings("shared");
  const html = message.html || "";
  const quoted = message.quoted_html || "";
  return <>
    {html ? <div className="staff-email-html" dangerouslySetInnerHTML={{ __html: html }} /> : null}
    {quoted ? <details className="staff-email-quote">
      <summary>{t("email.showQuoted")}</summary>
      <div className="staff-email-html is-quoted" dangerouslySetInnerHTML={{ __html: quoted }} />
    </details> : null}
    {!html && !quoted ? <p className="staff-email-blank">{t("email.blank")}</p> : null}
  </>;
}
