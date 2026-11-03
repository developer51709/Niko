import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError, getAuth } from "../api";
import { CryptoIcon } from "../components/CryptoIcon";
import { Icon } from "../components/Icon";
import { NetworkIcon } from "../components/NetworkIcon";
import { PublicHeader } from "../components/PublicHeader";
import { useStrings } from "../i18n";
import { navigate } from "../router";

type Perk = { key: string; title: string; description: string };

/** One chain a currency can be paid on, as OxaPay names it. */
type CryptoNetwork = { code: string; label: string };

type Plan = {
  plan: string;
  title: string;
  price_cents: number;
  price_label: string;
  currency: string;
  months: number;
  perks: Perk[];
  renewal_notice_days: number;
  currencies: string[];
  networks?: Record<string, CryptoNetwork[]>;
  methods: {
    crypto: { enabled: boolean };
    card: { enabled: boolean; message?: string };
  };
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

type OrderStatus = {
  status: string;
  paid: boolean;
  amount_label?: string;
  subscription?: { expires_at?: string | null } | null;
};

type PlanGuild = {
  id: string;
  name: string;
  icon_url: string | null;
  member_count: number;
  premium: { active: boolean; expires_at?: string | null } | null;
};

type DonationMeta = {
  presets: number[];
  min_amount: number;
  max_amount: number;
  totals: { total_cents: number; donation_count: number; donor_count: number };
  goal_cents: number;
  progress: number | null;
  your_total_cents: number;
  networks?: Record<string, CryptoNetwork[]>;
  configured: boolean;
};

function formatUsd(cents: number) {
  return `$${(cents / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

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

export function BillingPage() {
  const { t } = useStrings("billing");
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token") || "";
  const guildParam = (params.get("guild") || "").trim();
  const amountParam = params.get("amount") || "";
  const isDonation = Boolean(token);
  // Links from before the split used /billing?...&gift=1.
  const legacyGift = params.get("gift") === "1";

  useEffect(() => {
    if (legacyGift) {
      window.location.replace(`/billing/gift${guildParam ? `?guild=${guildParam}` : ""}`);
    }
  }, [guildParam, legacyGift]);

  const [plan, setPlan] = useState<Plan | null>(null);
  const [amount, setAmount] = useState(() => {
    const parsed = Number.parseFloat(amountParam);
    return Number.isFinite(parsed) && parsed >= 1 ? parsed.toFixed(2) : "5.00";
  });
  const [currency, setCurrency] = useState("USDT");
  // Empty means "whatever the chosen coin lists first", so switching coin can
  // never leave a network selected that the new coin cannot use.
  const [network, setNetwork] = useState("");
  const [guildId, setGuildId] = useState(guildParam);
  const [targets, setTargets] = useState<PlanGuild[] | null>(null);
  const [targetsError, setTargetsError] = useState("");
  const [meta, setMeta] = useState<DonationMeta | null>(null);
  const [step, setStep] = useState<"method" | "asset" | "pay" | "done">("method");
  const [checkout, setCheckout] = useState<Checkout | null>(null);
  const [paid, setPaid] = useState(false);
  const [paidUntil, setPaidUntil] = useState<string | null>(null);
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

  const networkOptions = useMemo<CryptoNetwork[]>(() => {
    const map = isDonation ? meta?.networks : plan?.networks;
    return map?.[currency] || [];
  }, [currency, isDonation, meta, plan]);
  const activeNetwork = networkOptions.some((option) => option.code === network)
    ? network
    : networkOptions[0]?.code || "";
  const activeNetworkLabel =
    networkOptions.find((option) => option.code === activeNetwork)?.label || activeNetwork;

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
      // Only servers the member manages can be upgraded; gifting has its own
      // page and its own (membership-based) list.
      const result = await api<{ guilds: PlanGuild[] }>("/api/premium/guilds");
      setTargets(result.guilds);
      if (!guildId && result.guilds.length === 1) setGuildId(result.guilds[0].id);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) setTargets([]);
      else setTargetsError(reason instanceof Error ? reason.message : t("error.servers"));
    }
  }, [guildId, t]);

  const loadMeta = useCallback(async () => {
    if (!isDonation) return;
    try {
      const query = new URLSearchParams({ token });
      setMeta(await api<DonationMeta>(`/api/donations/meta?${query.toString()}`));
    } catch {
      // Totals are garnish; the checkout still works without them.
    }
  }, [isDonation, token]);

  useEffect(() => {
    void loadPlan();
    void loadMeta();
    if (!isDonation) void loadTargets();
  }, [isDonation, loadMeta, loadPlan, loadTargets]);

  // Countdown for the quoted address; the provider stops accepting it after this.
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
      if (isDonation) {
        const result = await api<OrderStatus>(current.status_url || `/api/donations/${current.order_id}`);
        if (result.paid) {
          setPaid(true);
          setStep("done");
        }
        return;
      }
      const result = await api<OrderStatus>(`/api/premium/orders/${current.order_id}`);
      if (result.paid) {
        setPaid(true);
        setPaidUntil(result.subscription?.expires_at || null);
        setStep("done");
      }
    } catch {
      // A poll failure is not worth a visible error: the next tick retries.
    }
  }, [isDonation]);

  useEffect(() => {
    if (step !== "pay" || !checkout || paid) return;
    const timer = window.setInterval(() => void refreshStatus(checkout), 6000);
    return () => window.clearInterval(timer);
  }, [checkout, paid, refreshStatus, step]);

  const startCheckout = async () => {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const result = isDonation
        ? await api<Checkout>("/api/donations/invoice", {
            method: "POST",
            body: JSON.stringify({
              token,
              amount: Number.parseFloat(amount),
              currency,
              network: activeNetwork,
            }),
          })
        : await api<Checkout>("/api/premium/checkout", {
            method: "POST",
            headers: csrf ? { "X-CSRF-Token": csrf } : undefined,
            body: JSON.stringify({ guild_id: guildId, pay_currency: currency, network: activeNetwork }),
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

  const canPay = isDonation
    ? Number.parseFloat(amount) >= (meta?.min_amount ?? 1)
    : Boolean(guildId);

  const heading = isDonation ? t("head.titleDonation") : t("head.titlePremium");

  if (legacyGift) return null;

  return (
    <>
      <PublicHeader page="billing" />
      <main className="billing-page">
        <div className="billing-glow" aria-hidden="true" />
        <section className="billing-card" aria-labelledby="billing-title">
          <header className="billing-head">
            <span className="billing-eyebrow">
              <span className="billing-dot" aria-hidden="true" />
              {isDonation ? t("head.eyebrowDonation") : t("head.eyebrowSubscription")}
            </span>
            <h1 id="billing-title">{heading}</h1>
            <p>
              {isDonation ? t("head.donationBody") : t("head.subscriptionBody")}
            </p>
          </header>

          {!isDonation && plan && (
            <div className="billing-price">
              <strong>{plan.price_label}</strong>
              <span>{t("price.perMonth")}</span>
            </div>
          )}

          {loading && <div className="billing-loading"><span className="loading-ring" /><p>{t("loading")}</p></div>}

          {!loading && step === "method" && (
            <div className="billing-body">
              {!isDonation && (
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
                    <p className="billing-hint">{t("server.unmanageable")}</p>
                  )}
                  {targets && targets.length > 0 && (
                    <p className="billing-hint">
                      {t("server.giftHint")}{" "}
                      <a href={`/billing/gift${guildId ? `?guild=${guildId}` : ""}`}>{t("server.giftLink")}</a>.
                    </p>
                  )}
                </div>
              )}

              {isDonation && (
                <div className="billing-field">
                  <span className="billing-label">{t("donate.amountLabel")}</span>
                  <div className="billing-presets" role="group" aria-label={t("donate.presetsAria")}>
                    {(meta?.presets || [3, 5, 10, 25, 50]).map((preset) => (
                      <button
                        key={preset}
                        type="button"
                        className={`billing-preset${Number.parseFloat(amount) === preset ? " is-selected" : ""}`}
                        aria-pressed={Number.parseFloat(amount) === preset}
                        onClick={() => setAmount(preset.toFixed(2))}
                      >
                        ${preset}
                      </button>
                    ))}
                  </div>
                  <div className="billing-amount">
                    <span aria-hidden="true">$</span>
                    <input
                      type="number"
                      min={meta?.min_amount ?? 1}
                      max={meta?.max_amount ?? 10000}
                      step="1"
                      value={amount}
                      onChange={(event) => setAmount(event.target.value)}
                      aria-label={t("donate.amountAria")}
                    />
                  </div>
                  <p className="billing-hint">{t("donate.minimum", { amount: meta?.min_amount ?? 1 })}</p>
                  {meta && meta.totals.donation_count > 0 && (
                    <div className="billing-supporter-totals">
                      <p>
                        {t("donate.raised", {
                          total: formatUsd(meta.totals.total_cents),
                          donors: `${meta.totals.donor_count.toLocaleString()} ${t(meta.totals.donor_count === 1 ? "donate.supporterOne" : "donate.supporterMany")}`,
                          count: `${meta.totals.donation_count.toLocaleString()} ${t(meta.totals.donation_count === 1 ? "donate.donationOne" : "donate.donationMany")}`,
                        })}
                      </p>
                      {meta.goal_cents > 0 && (
                        <div
                          className="billing-goal"
                          role="progressbar"
                          aria-valuemin={0}
                          aria-valuemax={meta.goal_cents}
                          aria-valuenow={Math.min(meta.totals.total_cents, meta.goal_cents)}
                          aria-label={t("donate.goalAria")}
                        >
                          <i style={{ width: `${Math.min(100, Math.round((meta.progress || 0) * 100))}%` }} />
                        </div>
                      )}
                      {meta.your_total_cents > 0 && (
                        <p className="billing-hint">{t("donate.thanks", { amount: formatUsd(meta.your_total_cents) })}</p>
                      )}
                    </div>
                  )}
                </div>
              )}

              {!isDonation && plan && (
                <ul className="billing-perks">
                  {plan.perks.map((perk) => (
                    <li key={perk.key}>
                      <Icon name="check" />
                      <span><strong>{perk.title}</strong><small>{perk.description}</small></span>
                    </li>
                  ))}
                  <li>
                    <Icon name="check" />
                    <span><strong>{t("perks.renewalTitle")}</strong><small>{t("perks.renewalText", { days: plan.renewal_notice_days })}</small></span>
                  </li>
                </ul>
              )}

              <div className="billing-methods" role="radiogroup" aria-label={t("methods.aria")}>
                <button type="button" className="billing-method" disabled aria-disabled="true">
                  <span className="billing-method-icon"><Icon name="lock" /></span>
                  <span><strong>{t("methods.card")}</strong><small>{t("methods.cardNetworks")}</small></span>
                  <span className="billing-chip">{t("methods.soon")}</span>
                </button>
                <button
                  type="button"
                  role="radio"
                  aria-checked="true"
                  className="billing-method is-selected"
                  onClick={() => setStep("asset")}
                  disabled={!canPay}
                >
                  <span className="billing-method-icon is-coins" aria-hidden="true">
                    <CryptoIcon code="USDT" />
                    <CryptoIcon code="BTC" />
                    <CryptoIcon code="ETH" />
                  </span>
                  <span><strong>{t("methods.crypto")}</strong><small>{t("methods.cryptoNetworks")}</small></span>
                  <Icon name="arrow" />
                </button>
              </div>
              {!plan?.methods.crypto.enabled && !isDonation && (
                <p className="billing-error" role="alert">{t("methods.unconfigured")}</p>
              )}
              {error && <p className="billing-error" role="alert">{error}</p>}
            </div>
          )}

          {!loading && step === "asset" && (
            <div className="billing-body">
              <div className="billing-step-head">
                <button type="button" className="billing-back" onClick={() => { setStep("method"); setError(""); }}>
                  ← {t("step.back")}
                </button>
                <span className="billing-step-count">{t("step.count")}</span>
              </div>
              <div className="billing-summary">
                <div>
                  <span className="billing-label">{t("step.paying")}</span>
                  <strong>{isDonation ? `$${Number.parseFloat(amount).toFixed(2)} USD` : plan?.price_label}</strong>
                </div>
                <div>
                  <span className="billing-label">{isDonation ? t("step.to") : t("server.label")}</span>
                  <strong>{isDonation ? t("step.niko") : selectedTarget?.name || t("step.serverFallback", { id: guildId })}</strong>
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
              <h2>{isDonation ? t("done.donationTitle") : t("done.premiumTitle")}</h2>
              <p>
                {isDonation
                  ? t("done.donationBody")
                  : paidUntil && formatDate(paidUntil)
                    ? t("done.premiumBodyUntil", { date: formatDate(paidUntil)! })
                    : t("done.premiumBody")}
              </p>
              {isDonation && checkout && (
                <div className="billing-receipt">
                  <div>
                    <span className="billing-label">{t("done.amount")}</span>
                    <strong>{checkout.amount_label}</strong>
                  </div>
                  <div>
                    <span className="billing-label">{t("done.trackId")}</span>
                    <code>{checkout.track_id || checkout.order_id}</code>
                  </div>
                  <p className="billing-hint">
                    {t("done.keepTrackBefore")} <code>/donationstatus</code>{t("done.keepTrackAfter")}
                  </p>
                </div>
              )}
              <div className="billing-done-actions">
                <button type="button" className="billing-primary" onClick={() => navigate(isDonation ? "/" : `/dashboard/${guildId}/moderation`)}>
                  {isDonation ? t("done.back") : t("done.openModeration")}
                  <Icon name="arrow" />
                </button>
                {!isDonation && (
                  <button type="button" className="billing-ghost" onClick={() => navigate("/dashboard")}>
                    {t("done.dashboard")}
                  </button>
                )}
              </div>
              {paid && <span className="billing-sr" role="status">{t("done.confirmed")}</span>}
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

