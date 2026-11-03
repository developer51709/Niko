import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { getOwnerLocales, syncOwnerLocales } from "../../api";
import { useStrings } from "../../i18n";
import type { OwnerLocalePage, OwnerLocales } from "../../types";
import { notifyError, notifySuccess } from "../../utils/toast";
import { Icon } from "../Icon";

type Translate = (key: string, values?: Record<string, string | number>) => string;

const TOAST_KEY = "owner-locales";

function percent(done: number, total: number) {
  return total ? Math.round((done / total) * 1000) / 10 : 0;
}

function ago(timestamp: number | null | undefined, t: Translate) {
  if (!timestamp) return t("owner.never");
  const seconds = Math.max(0, Math.round(Date.now() / 1000 - timestamp));
  if (seconds < 60) return t("owner.justNow");
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return t("owner.minutesAgo", { count: minutes });
  return t("owner.hoursAgo", { count: Math.floor(minutes / 60) });
}

/** One collapsible slice of the catalogue card, with its own count in the header. */
function Fold({
  title,
  meta,
  children,
}: {
  title: string;
  meta: string;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  return (
    <details
      className="owner-fold"
      open={open}
      onToggle={(event) => setOpen(event.currentTarget.open)}
    >
      <summary>
        <Icon name="chevron" className="owner-fold-arrow" />
        <span className="owner-fold-title">{title}</span>
        <span className="owner-fold-meta">{meta}</span>
      </summary>
      <div className="owner-fold-body">{children}</div>
    </details>
  );
}

/**
 * One collapsible card per catalogue, with a one-line overview.
 *
 * Bot catalogues and website pages are counted the same way — English keys per
 * file, translated keys per language — so both families share this list. The
 * overview answers "is this one done?" without opening anything; the body then
 * gives each language its own bar, because a half-translated catalogue is the
 * thing a translator actually needs to find.
 */
function CatalogueList({
  rows,
  languages,
  t,
}: {
  rows: OwnerLocalePage[];
  languages: { code: string }[];
  t: Translate;
}) {
  return (
    <div className="owner-catalogue-list">
      {rows.map((row) => {
        const covered = languages.reduce((sum, language) => sum + (row.languages[language.code] ?? 0), 0);
        const finished = languages.filter(
          (language) => row.keys > 0 && (row.languages[language.code] ?? 0) >= row.keys,
        ).length;
        const overall = row.keys && languages.length
          ? Math.round((covered / (row.keys * languages.length)) * 100)
          : 0;
        return (
          <details className="owner-catalogue" key={row.page}>
            <summary>
              <Icon name="chevron" className="owner-catalogue-arrow" />
              <span className="owner-catalogue-name">{row.page}</span>
              <span className="owner-catalogue-overview">
                <span className="owner-language-meter" aria-hidden="true">
                  <span style={{ width: `${overall ? Math.max(1.5, overall) : 0}%` }} />
                </span>
                <small>
                  {t("owner.locales.cardKeys", { count: row.keys })} · {t("owner.locales.cardLanguages", { done: finished, total: languages.length })}
                </small>
              </span>
              <strong className={`owner-catalogue-percent${overall >= 100 ? " is-complete" : ""}`}>{overall}%</strong>
            </summary>
            <ul className="owner-catalogue-langs">
              {languages.map((language) => {
                const done = row.languages[language.code] ?? 0;
                const share = percent(done, row.keys);
                const tone = !done ? "" : done >= row.keys ? "is-complete" : "is-partial";
                return (
                  <li key={language.code} className={tone}>
                    <span className="owner-catalogue-code">{language.code}</span>
                    <span className="owner-language-meter" aria-hidden="true">
                      <span style={{ width: `${done ? Math.max(1.5, share) : 0}%` }} />
                    </span>
                    <strong>{done ? `${share}%` : "—"}</strong>
                    <small>{done} / {row.keys}</small>
                  </li>
                );
              })}
            </ul>
          </details>
        );
      })}
    </div>
  );
}

/**
 * The owner's live view of the site's catalogues.
 *
 * Reads the same merge the public `/status` page uses, so the numbers here and
 * there can never disagree, and says plainly whether they describe beta's
 * working copy or this deployment's build.
 */
export function LocaleSyncView({ csrfToken }: { csrfToken?: string }) {
  const { t } = useStrings("staff");
  const [data, setData] = useState<OwnerLocales | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setData(await getOwnerLocales());
      setError("");
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const sync = async () => {
    setBusy(true);
    try {
      const next = await syncOwnerLocales(csrfToken);
      setData(next);
      notifySuccess(t("owner.locales.synced"), TOAST_KEY);
    } catch (exc) {
      notifyError(exc instanceof Error ? exc.message : String(exc), TOAST_KEY);
    } finally {
      setBusy(false);
    }
  };

  if (error && !data) {
    return (
      <div className="owner-view">
        <div className="owner-empty">
          <p>{error}</p>
          <button type="button" className="button button-muted" onClick={() => void load()}>{t("owner.retry")}</button>
        </div>
      </div>
    );
  }

  if (!data) {
    return <div className="owner-view"><div className="owner-empty"><div className="loading-ring" /><p>{t("owner.loading")}</p></div></div>;
  }

  const live = data.source?.mode === "beta";
  const languages = [...data.coverage].sort((a, b) => b.percent - a.percent);

  return (
    <div className="owner-view">
      <header className="staff-guilds-heading">
        <div>
          <span className="panel-kicker">{t("owner.locales.kicker")}</span>
          <h2>{t("owner.locales.title")}</h2>
          <p>{t("owner.locales.body")}</p>
        </div>
        <div className="staff-guild-count">
          <strong>{data.languages.length}</strong>
          <span>{t("owner.locales.languageCount", { keys: data.total_keys + (data.bot_total_keys ?? 0) })}</span>
        </div>
      </header>

      {!data.configured && (
        <div className="owner-notice">
          <Icon name="doc" />
          <div>
            <strong>{t("owner.locales.notConfigured")}</strong>
            <p>{t("owner.locales.notConfiguredBody")}</p>
            <code>BETA_INSTANCE_URL=https://beta.example.com</code>
          </div>
        </div>
      )}

      <section className="owner-card">
        <div className="owner-card-head">
          <div>
            <span className="panel-kicker">{t("owner.locales.sourceKicker")}</span>
            <h3>{live ? t("owner.locales.liveTitle") : t("owner.locales.localTitle")}</h3>
            <p>
              {live
                ? t("owner.locales.liveBody", { origin: data.origin ?? "beta", age: data.source?.age_seconds ?? 0 })
                : data.configured
                  ? t("owner.locales.fallbackBody", { error: data.source?.error ?? t("owner.locales.noAnswer") })
                  : t("owner.locales.buildBody")}
            </p>
          </div>
          <div className="owner-card-actions">
            <span className={`owner-chip${live ? " is-live" : ""}`}>{live ? t("owner.locales.liveChip") : t("owner.locales.buildChip")}</span>
            {data.configured && (
              <button type="button" className="button button-muted" onClick={() => void sync()} disabled={busy}>
                <Icon name="spark" /> {busy ? t("owner.locales.syncing") : t("owner.locales.sync")}
              </button>
            )}
          </div>
        </div>
        <dl className="owner-facts">
          <div><dt>{t("owner.locales.beta")}</dt><dd>{data.origin ?? t("owner.locales.unset")}</dd></div>
          <div><dt>{t("owner.locales.scanned")}</dt><dd>{ago(data.generated_at, t)}</dd></div>
          <div><dt>{t("owner.locales.pages")}</dt><dd>{data.pages.length}</dd></div>
          <div><dt>{t("owner.locales.botCatalogues")}</dt><dd>{data.bot?.length ?? 0}</dd></div>
          <div><dt>{t("owner.locales.keys")}</dt><dd>{data.total_keys + (data.bot_total_keys ?? 0)}</dd></div>
          <div>
            <dt>{t("owner.locales.botSyncLabel")}</dt>
            <dd>
              {data.bot_sync?.files
                ? t("owner.locales.botSyncLive", { count: data.bot_sync.files })
                : t("owner.locales.botSyncNone")}
            </dd>
          </div>
        </dl>
      </section>

      <section className="owner-card">
        <div className="owner-card-head">
          <div>
            <span className="panel-kicker">{t("owner.locales.languagesKicker")}</span>
            <h3>{t("owner.locales.languagesTitle")}</h3>
            <p>{t("owner.locales.languagesBody")}</p>
          </div>
        </div>
        <ul className="owner-language-list">
          {languages.map((row) => {
            // Pages and cogs are counted together in the percentage, so the
            // finished tally has to add both halves up as well.
            const done = (row.complete_pages ?? 0) + (row.complete_bot ?? 0);
            const entries = (row.pages ?? 0) + (row.bot ?? 0);
            return (
              <li key={row.code} className={row.missing === 0 ? "is-complete" : ""}>
                <span className="owner-language-code">{row.code}</span>
                <span className="owner-language-name">{row.label}</span>
                <span className="owner-language-meter" aria-hidden="true"><span style={{ width: `${Math.max(1.5, row.percent)}%` }} /></span>
                <strong>{row.percent}%</strong>
                <small>
                  {row.translated} / {row.total}
                  {entries ? ` · ${done}/${entries} ${t("owner.locales.pagesDone")}` : ""}
                </small>
              </li>
            );
          })}
        </ul>
      </section>

      <section className="owner-card">
        <div className="owner-card-head">
          <div>
            <span className="panel-kicker">{t("owner.locales.cataloguesKicker")}</span>
            <h3>{t("owner.locales.cataloguesTitle")}</h3>
            <p>{t("owner.locales.cataloguesBody")}</p>
          </div>
        </div>
        {/* The two halves of the feed: the bot keeps its strings in each cog's
            ``locales`` folder, the site in its own page folders. They are read
            from the same manifest, so they belong in one card, folded apart. */}
        <Fold
          title={t("owner.locales.botSection")}
          meta={t("owner.locales.catalogueCount", { count: data.bot?.length ?? 0 })}
        >
          <p className="owner-fold-note">{t("owner.locales.botSectionBody")}</p>
          <CatalogueList rows={data.bot ?? []} languages={data.languages} t={t} />
        </Fold>
        <Fold
          title={t("owner.locales.siteSection")}
          meta={t("owner.locales.pageCount", { count: data.pages.length })}
        >
          <p className="owner-fold-note">{t("owner.locales.siteSectionBody")}</p>
          <CatalogueList rows={data.pages} languages={data.languages} t={t} />
        </Fold>
      </section>
    </div>
  );
}
