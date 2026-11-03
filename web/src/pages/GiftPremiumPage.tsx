import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError, getAuth } from "../api";
import { CryptoIcon } from "../components/CryptoIcon";
import { Icon } from "../components/Icon";
import { NetworkIcon } from "../components/NetworkIcon";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";
import { navigate } from "../router";

/**
 * Gift checkout.
 *
 * Buying premium for your own server and gifting it to a community you merely
 * belong to are different purchases: the gift page lists servers by membership,
 * offers multi-month terms, and polls its own order endpoint. Keeping it off
 * /billing means neither flow has to guess the other's rules.
 */

/** One chain a currency can be paid on, as OxaPay names it. */
type CryptoNetwork = { code: string; label: string };

type Plan = {
  price_cents: number;
  price_label: string;
  currencies: string[];
  networks?: Record<string, CryptoNetwork[]>;
  gift: { enabled: boolean; months: number[]; price_cents_per_month: number };
  methods: { crypto: { enabled: boolean } };
};

type GiftTarget = {
  id: string;
  name: string;
  icon_url: string | null;
  member_count: number;
  premium: { active: boolean; expires_at?: string | null } | null;
};

type Checkout = {
  order_id: string;
  track_id?: string;
  amount_label: string;
  amount_cents: number;
  pay_currency?: string | null;
  pay_amount?: number | null;
  network?: string | null;
  address?: string | null;
  memo?: string | null;
  qr_code?: string | null;
  expires_at?: number | null;
  status_url?: string;
  months?: number;
};

type GiftStatus = {
  status: string;
  paid: boolean;
  months?: number;
  subscription?: { active?: boolean; expires_at?: string | null } | null;
};

const CURRENCY_LABELS: Record<string, { name: string; mark: string }> = {
  USDT: { name: "Tether", mark: "₮" },
  ETH: { name: "Ethereum", mark: "Ξ" },
  BTC: { name: "Bitcoin", mark: "₿" },
  BNB: { name: "BNB", mark: "◈" },
  LTC: { name: "Litecoin", mark: "Ł" },
  DOGE: { name: "Dogecoin", mark: "Ð" },
  TRX: { name: "TRON", mark: "◉" },
  XMR: { name: "Monero", mark: "ɱ" },
};

function currencyLabel(code: string) {
  return CURRENCY_LABELS[code] || { name: code, mark: "◈" };
}

function formatCountdown(seconds: number) {
  if (seconds <= 0) return "expired";
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

function formatDate(value?: string | null) {
  if (!value) return null;
  const parsed = new Date(value.includes("T") ? value : value.replace(" ", "T") + "Z");
  if (Number.isNaN(parsed.getTime())) return null;
  return parsed.toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" });
}

function monthLabel(months: number, t: (key: string, values?: Record<string, string | number>) => string) {
  return t(months === 1 ? "months.one" : "months.many", { count: months });
}

export function GiftPremiumPage() {
  const { t } = useStrings("gift");
  const params = new URLSearchParams(window.location.search);
  const guildParam = (params.get("guild") || "").trim();

  const [plan, setPlan] = useState<Plan | null>(null);
  const [targets, setTargets] = useState<GiftTarget[] | null>(null);
  const [targetsError, setTargetsError] = useState("");
  const [guildId, setGuildId] = useState(guildParam);
  const [months, setMonths] = useState(1);
  const [currency, setCurrency] = useState("USDT");
  // Empty means "the chosen coin's first network", so switching coin never
  // keeps a chain the new coin cannot be paid on.
  const [network, setNetwork] = useState("");
  const [step, setStep] = useState<"setup" | "asset" | "pay" | "done">("setup");
  const [checkout, setCheckout] = useState<Checkout | null>(null);
  const [giftedUntil, setGiftedUntil] = useState<string | null>(null);
  const [giftedMonths, setGiftedMonths] = useState(1);
  const [error, setError] = useState("");
  const [csrf, setCsrf] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const [copied, setCopied] = useState("");

  const selectedTarget = useMemo(
    () => targets?.find((target) => target.id === guildId) || null,
    [targets, guildId],
  );

  const networkOptions = useMemo<CryptoNetwork[]>(
    () => plan?.networks?.[currency] || [],
    [currency, plan],
  );
  const activeNetwork = networkOptions.some((option) => option.code === network)
    ? network
    : networkOptions[0]?.code || "";
  const activeNetworkLabel =
    networkOptions.find((option) => option.code === activeNetwork)?.label || activeNetwork;

  const terms = plan?.gift.months?.length ? plan.gift.months : [1, 3, 6, 12];
  const perMonthCents = plan?.gift.price_cents_per_month || plan?.price_cents || 1500;
  const totalCents = perMonthCents * months;

  const loginHref = useMemo(
    () => `/auth/login?next=${encodeURIComponent(window.location.pathname + window.location.search)}`,
    [],
  );

  const loadPlan = useCallback(async () => {
    try {
      setPlan(await api<Plan>("/api/premium/plans"));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : t("error.unavailable"));
    } finally {
      setLoading(false);
    }
  }, [t]);

  const loadTargets = useCallback(async () => {
    setTargetsError("");
    try {
      const auth = await getAuth();
      if (!auth.authenticated) {
        setTargets([]);
        return;
      }
      setCsrf(auth.csrf_token || "");
      const result = await api<{ guilds: GiftTarget[] }>("/api/premium/gift-targets");
      setTargets(result.guilds);
      if (!guildId && result.guilds.length === 1) setGuildId(result.guilds[0].id);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) setTargets([]);
      else setTargetsError(reason instanceof Error ? reason.message : t("error.servers"));
    }
  }, [guildId, t]);

  useEffect(() => {
    void loadPlan();
    void loadTargets();
  }, [loadPlan, loadTargets]);

  useEffect(() => {
    if (!checkout?.expires_at) {
      setSecondsLeft(null);
      return;
    }
    const tick = () => setSecondsLeft(Math.max(0, Math.floor(checkout.expires_at! - Date.now() / 1000)));
    tick();
    const timer = window.setInterval(tick, 1000);
    return () => window.clearInterval(timer);
  }, [checkout?.expires_at]);

  const refreshStatus = useCallback(async (current: Checkout) => {
    try {
      const result = await api<GiftStatus>(
        current.status_url || `/api/premium/gift/orders/${current.order_id}`,
      );
      if (result.paid) {
        setGiftedUntil(result.subscription?.expires_at || null);
        setGiftedMonths(result.months || current.months || months);
        setStep("done");
      }
    } catch {
      // A poll failure is not worth a visible error: the next tick retries.
    }
  }, [months]);

  useEffect(() => {
    if (step !== "pay" || !checkout) return;
    const timer = window.setInterval(() => void refreshStatus(checkout), 6000);
    return () => window.clearInterval(timer);
  }, [checkout, refreshStatus, step]);

  const startCheckout = async () => {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const result = await api<Checkout>("/api/premium/gift/checkout", {
        method: "POST",
        headers: csrf ? { "X-CSRF-Token": csrf } : undefined,
        body: JSON.stringify({ guild_id: guildId, months, pay_currency: currency, network: activeNetwork }),
      });
      setCheckout(result);
      setStep("pay");
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        setTargets([]);
        setError(t("error.signIn"));
      } else {
        setError(reason instanceof Error ? reason.message : t("error.checkout"));
      }
    } finally {
      setBusy(false);
    }
  };

  const copy = async (value: string, label: string) => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(label);
      window.setTimeout(() => setCopied(""), 1800);
    } catch {
      setError(t("error.copy"));
    }
  };

  const canPay = Boolean(guildId && selectedTarget);

  return (
    <>
      <PublicHeader page="billing" />
      <main className="billing-page">
        <div className="billing-glow" aria-hidden="true" />
        <section className="billing-card" aria-labelledby="gift-title">
          <header className="billing-head">
            <span className="billing-eyebrow">
              <span className="billing-dot" aria-hidden="true" />
              {t("head.eyebrow")}
            </span>
            <h1 id="gift-title">{t("head.title")}</h1>
            <p>{t("head.body")}</p>
          </header>

          {plan && (
            <div className="billing-price">
              <strong>{`$${(totalCents / 100).toFixed(2)}`}</strong>
              <span>{t("price.forOneServer", { term: monthLabel(months, t) })}</span>
            </div>
          )}

          {loading && <div className="billing-loading"><span className="loading-ring" /><p>{t("loading")}</p></div>}

          {!loading && step === "setup" && (
            <div className="billing-body">
              <div className="billing-field">
                <span className="billing-label">{t("server.label")}</span>
                {targets === null ? (
                  <div className="billing-skeleton" aria-hidden="true" />
                ) : targets.length === 0 ? (
                  <p className="billing-hint">
                    <a href={loginHref}>{t("server.signIn")}</a> {t("server.signInAfter")}
                  </p>
                ) : (
                  <div className="billing-targets" role="radiogroup" aria-label={t("server.label")}>
                    {targets.map((target) => (
                      <button
                        key={target.id}
                        type="button"
                        role="radio"
                        aria-checked={guildId === target.id}
                        className={`billing-target${guildId === target.id ? " is-selected" : ""}`}
                        onClick={() => setGuildId(target.id)}
                      >
                        <span className="billing-target-icon">
                          {target.icon_url ? <img src={target.icon_url} alt="" /> : <b>{target.name.slice(0, 1)}</b>}
                        </span>
                        <span className="billing-target-text">
                          <strong>{target.name}</strong>
                          <small>
                            {target.premium?.active
                              ? t("server.premiumUntil", { date: formatDate(target.premium.expires_at) || t("server.later") })
                              : t("server.members", { count: target.member_count.toLocaleString() })}
                          </small>
                        </span>
                        {target.premium?.active && <span className="billing-chip">{t("server.chip")}</span>}
                      </button>
                    ))}
                  </div>
                )}
                {targetsError && <p className="billing-error" role="alert">{targetsError}</p>}
                {guildParam && !selectedTarget && targets && targets.length > 0 && (
                  <p className="billing-hint">{t("server.notMember")}</p>
                )}
                <p className="billing-hint">
                  {t("server.subscribeHint")} <a href={`/billing${guildId ? `?guild=${guildId}` : ""}`}>{t("server.subscribeLink")}</a>.
                </p>
              </div>

              <div className="billing-field">
                <span className="billing-label">{t("length.label")}</span>
                <div className="billing-presets" role="radiogroup" aria-label={t("length.aria")}>
                  {terms.map((option) => (
                    <button
                      key={option}
                      type="button"
                      role="radio"
                      aria-checked={months === option}
                      className={`billing-preset${months === option ? " is-selected" : ""}`}
                      onClick={() => setMonths(option)}
                    >
                      {t("length.months", { count: option })}
                    </button>
                  ))}
                </div>
                {selectedTarget?.premium?.active && (
                  <p className="billing-hint">{t("length.adds", { term: monthLabel(months, t) })}</p>
                )}
              </div>

              {plan && (
                <ul className="billing-perks">
                  <li>
                    <Icon name="check" />
                    <span><strong>{t("perks.sameTitle")}</strong><small>{t("perks.sameBody")}</small></span>
                  </li>
                  <li>
                    <Icon name="check" />
                    <span><strong>{t("perks.ownerTitle")}</strong><small>{t("perks.ownerBody")}</small></span>
                  </li>
                  <li>
                    <Icon name="check" />
                    <span><strong>{t("perks.noRenewalTitle")}</strong><small>{t("perks.noRenewalBody")}</small></span>
                  </li>
                </ul>
              )}

              <button
                type="button"
                className="billing-primary"
                onClick={() => setStep("asset")}
                disabled={!canPay}
              >
                {t("action.continue")}
                <Icon name="arrow" />
              </button>
              {!plan?.methods.crypto.enabled && (
                <p className="billing-error" role="alert">{t("methods.unconfigured")}</p>
              )}
              {error && <p className="billing-error" role="alert">{error}</p>}
            </div>
          )}

          {!loading && step === "asset" && (
            <div className="billing-body">
              <div className="billing-step-head">
                <button type="button" className="billing-back" onClick={() => { setStep("setup"); setError(""); }}>
                  ← {t("step.back")}
                </button>
                <span className="billing-step-count">{t("step.count")}</span>
              </div>
              <div className="billing-summary">
                <div>
                  <span className="billing-label">{t("step.paying")}</span>
                  <strong>{`$${(totalCents / 100).toFixed(2)} USD`}</strong>
                </div>
                <div>
                  <span className="billing-label">{t("step.giftFor")}</span>
                  <strong>{selectedTarget?.name || t("step.serverFallback", { id: guildId })}</strong>
                </div>
              </div>
              <span className="billing-label">{t("asset.currency")}</span>
              <div className="billing-assets" role="radiogroup" aria-label={t("asset.currencyAria")}>
                {(plan?.currencies || Object.keys(CURRENCY_LABELS)).map((code) => {
                  const meta = currencyLabel(code);
                  return (
                    <button
                      key={code}
                      type="button"
                      role="radio"
                      aria-checked={currency === code}
                      className={`billing-asset${currency === code ? " is-selected" : ""}`}
                      onClick={() => {
                        setCurrency(code);
                        setNetwork("");
                      }}
                    >
                      <span className="billing-asset-mark" aria-hidden="true">
                        <CryptoIcon code={code} fallback={meta.mark} />
                      </span>
                      <strong>{code}</strong>
                      <small>{meta.name}</small>
                    </button>
                  );
                })}
              </div>
              {networkOptions.length > 0 && (
                <div className="billing-networks-block">
                  <span className="billing-label">{t("asset.network")}</span>
                  <div className="billing-networks" role="radiogroup" aria-label={t("asset.networkAria")}>
                    {networkOptions.map((option) => (
                      <button
                        key={option.code}
                        type="button"
                        role="radio"
                        aria-checked={activeNetwork === option.code}
                        className={`billing-network${activeNetwork === option.code ? " is-selected" : ""}`}
                        onClick={() => setNetwork(option.code)}
                      >
                        <NetworkIcon network={option.code} fallback="◈" />
                        <span>{option.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <p className="billing-network-warning">
                <Icon name="alert" />
                <span>
                  {t("warn.send")} <strong>{currency}</strong> {t("warn.onlyOn")}{" "}
                  <strong>{activeNetworkLabel || t("warn.quotedAfter")}</strong>{t("warn.otherNetwork")}
                </span>
              </p>
              {error && <p className="billing-error" role="alert">{error}</p>}
              <button type="button" className="billing-primary" onClick={() => void startCheckout()} disabled={busy}>
                {busy ? t("action.quoting") : t("action.payWith", { currency })}
                <Icon name="arrow" />
              </button>
              <p className="billing-fineprint">{t("fineprint.quote", { currency })}</p>
            </div>
          )}

          {!loading && step === "pay" && checkout && (
            <div className="billing-body">
              <div className="billing-step-head">
                <span className="billing-live"><span className="billing-dot" />{t("pay.waiting")}</span>
                {secondsLeft !== null && (
                  <span className={`billing-countdown${secondsLeft < 300 ? " is-late" : ""}`}>
                    {t("pay.countdown", { time: formatCountdown(secondsLeft) })}
                  </span>
                )}
              </div>
              <div className="billing-quote">
                <div className="billing-quote-amount">
                  <span className="billing-label">{t("pay.sendExactly")}</span>
                  <strong>
                    <CryptoIcon code={checkout.pay_currency || currency} />
                    {checkout.pay_amount ?? "—"} {checkout.pay_currency || currency}
                  </strong>
                  <small>
                    {checkout.amount_label}
                    {checkout.network ? ` · ${checkout.network}` : ""}
                  </small>
                </div>
                {checkout.qr_code && (
                  <img className="billing-qr" src={checkout.qr_code} alt={t("pay.qrAlt", { currency: checkout.pay_currency || currency })} />
                )}
              </div>
              <div className="billing-address">
                <span className="billing-label">{t("pay.address")}</span>
                <code>{checkout.address || t("pay.addressMissing")}</code>
                {checkout.address && (
                  <button type="button" className="billing-copy" onClick={() => void copy(checkout.address!, "address")}>
                    {copied === "address" ? t("pay.copied") : t("pay.copy")}
                  </button>
                )}
              </div>
              {checkout.memo && (
                <p className="billing-hint"><strong>{t("pay.memo")}</strong> {checkout.memo}</p>
              )}
              <p className="billing-network-warning">
                <Icon name="alert" />
                <span>
                  {t("warn.send")} <strong>{checkout.pay_currency || currency}</strong> {t("warn.onlyOn")}{" "}
                  <strong>{checkout.network || activeNetworkLabel}</strong>{t("warn.transferOther")}
                </span>
              </p>
              {error && <p className="billing-error" role="alert">{error}</p>}
              <button type="button" className="billing-primary" onClick={() => void refreshStatus(checkout)}>
                {t("pay.checkNow")}
                <Icon name="refresh" />
              </button>
              <p className="billing-fineprint">{t("fineprint.status")}</p>
            </div>
          )}

          {!loading && step === "done" && (
            <div className="billing-body billing-done">
              <span className="billing-done-mark" aria-hidden="true"><Icon name="check" /></span>
              <h2>{t("done.title")}</h2>
              <p>
                {giftedUntil && formatDate(giftedUntil)
                  ? t("done.bodyUntil", { server: selectedTarget?.name || t("done.thisServer"), term: monthLabel(giftedMonths, t), date: formatDate(giftedUntil)! })
                  : t("done.body", { server: selectedTarget?.name || t("done.thisServer"), term: monthLabel(giftedMonths, t) })}
              </p>
              <div className="billing-done-actions">
                <button
                  type="button"
                  className="billing-primary"
                  onClick={() => {
                    setCheckout(null);
                    setStep("setup");
                  }}
                >
                  {t("done.giftAnother")}
                  <Icon name="arrow" />
                </button>
                <button type="button" className="billing-ghost" onClick={() => navigate("/")}>
                  {t("done.back")}
                </button>
              </div>
            </div>
          )}

          <footer className="billing-foot">
            <span>{t("foot.oxapay")}</span>
            <span aria-hidden="true">·</span>
            <span>{t("foot.fal")}</span>
          </footer>
        </section>
      </main>
    </>
  );
}
