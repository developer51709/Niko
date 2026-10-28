import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError, getAuth } from "../api";
import { CryptoIcon } from "../components/CryptoIcon";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { navigate } from "../router";

/**
 * Gift checkout.
 *
 * Buying premium for your own server and gifting it to a community you merely
 * belong to are different purchases: the gift page lists servers by membership,
 * offers multi-month terms, and polls its own order endpoint. Keeping it off
 * /billing means neither flow has to guess the other's rules.
 */

type Plan = {
  price_cents: number;
  price_label: string;
  currencies: string[];
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

function monthLabel(months: number) {
  return `${months} month${months === 1 ? "" : "s"}`;
}

export function GiftPremiumPage() {
  const params = new URLSearchParams(window.location.search);
  const guildParam = (params.get("guild") || "").trim();

  const [plan, setPlan] = useState<Plan | null>(null);
  const [targets, setTargets] = useState<GiftTarget[] | null>(null);
  const [targetsError, setTargetsError] = useState("");
  const [guildId, setGuildId] = useState(guildParam);
  const [months, setMonths] = useState(1);
  const [currency, setCurrency] = useState("USDT");
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
      setError(reason instanceof Error ? reason.message : "Billing is unavailable right now.");
    } finally {
      setLoading(false);
    }
  }, []);

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
      else setTargetsError(reason instanceof Error ? reason.message : "Your servers could not be loaded.");
    }
  }, [guildId]);

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
        body: JSON.stringify({ guild_id: guildId, months, pay_currency: currency }),
      });
      setCheckout(result);
      setStep("pay");
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) {
        setTargets([]);
        setError("Sign in with Discord to continue.");
      } else {
        setError(reason instanceof Error ? reason.message : "Checkout could not be started.");
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
      setError("Copying failed — select the address manually.");
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
              One-off gift
            </span>
            <h1 id="gift-title">Gift Niko Premium</h1>
            <p>
              Send a community premium moderation. You do not need to manage the server —
              only to be a member of it — and the owner is told who sent it.
            </p>
          </header>

          {plan && (
            <div className="billing-price">
              <strong>{`$${(totalCents / 100).toFixed(2)}`}</strong>
              <span>{monthLabel(months)} for one server</span>
            </div>
          )}

          {loading && <div className="billing-loading"><span className="loading-ring" /><p>Preparing checkout…</p></div>}

          {!loading && step === "setup" && (
            <div className="billing-body">
              <div className="billing-field">
                <span className="billing-label">Server</span>
                {targets === null ? (
                  <div className="billing-skeleton" aria-hidden="true" />
                ) : targets.length === 0 ? (
                  <p className="billing-hint">
                    <a href={loginHref}>Sign in with Discord</a> to pick a server you are in.
                  </p>
                ) : (
                  <div className="billing-targets" role="radiogroup" aria-label="Server">
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
                              ? `Premium until ${formatDate(target.premium.expires_at) || "later"}`
                              : `${target.member_count.toLocaleString()} members`}
                          </small>
                        </span>
                        {target.premium?.active && <span className="billing-chip">Premium</span>}
                      </button>
                    ))}
                  </div>
                )}
                {targetsError && <p className="billing-error" role="alert">{targetsError}</p>}
                {guildParam && !selectedTarget && targets && targets.length > 0 && (
                  <p className="billing-hint">You are not a member of that server. Pick another below.</p>
                )}
                <p className="billing-hint">
                  Buying for a server you manage? <a href={`/billing${guildId ? `?guild=${guildId}` : ""}`}>Subscribe instead</a>.
                </p>
              </div>

              <div className="billing-field">
                <span className="billing-label">Length</span>
                <div className="billing-presets" role="radiogroup" aria-label="Gift length">
                  {terms.map((option) => (
                    <button
                      key={option}
                      type="button"
                      role="radio"
                      aria-checked={months === option}
                      className={`billing-preset${months === option ? " is-selected" : ""}`}
                      onClick={() => setMonths(option)}
                    >
                      {option}mo
                    </button>
                  ))}
                </div>
                {selectedTarget?.premium?.active && (
                  <p className="billing-hint">
                    This adds {monthLabel(months)} on top of the current term, so no paid days are lost.
                  </p>
                )}
              </div>

              {plan && (
                <ul className="billing-perks">
                  <li>
                    <Icon name="check" />
                    <span><strong>Same perks as a subscription</strong><small>AI image moderation for the whole server, for the gifted term.</small></span>
                  </li>
                  <li>
                    <Icon name="check" />
                    <span><strong>The owner is told</strong><small>They get a DM naming you and the date the new term ends.</small></span>
                  </li>
                  <li>
                    <Icon name="check" />
                    <span><strong>No renewal, no surprise charge</strong><small>When the gift ends, premium simply pauses.</small></span>
                  </li>
                </ul>
              )}

              <button
                type="button"
                className="billing-primary"
                onClick={() => setStep("asset")}
                disabled={!canPay}
              >
                Continue to payment
                <Icon name="arrow" />
              </button>
              {!plan?.methods.crypto.enabled && (
                <p className="billing-error" role="alert">Payments are not configured on this deployment yet.</p>
              )}
              {error && <p className="billing-error" role="alert">{error}</p>}
            </div>
          )}

          {!loading && step === "asset" && (
            <div className="billing-body">
              <div className="billing-step-head">
                <button type="button" className="billing-back" onClick={() => { setStep("setup"); setError(""); }}>
                  ← Back
                </button>
                <span className="billing-step-count">Step 2 of 2</span>
              </div>
              <div className="billing-summary">
                <div>
                  <span className="billing-label">Paying</span>
                  <strong>{`$${(totalCents / 100).toFixed(2)} USD`}</strong>
                </div>
                <div>
                  <span className="billing-label">Gift for</span>
                  <strong>{selectedTarget?.name || `Server ${guildId}`}</strong>
                </div>
              </div>
              <span className="billing-label">Choose a currency</span>
              <div className="billing-assets" role="radiogroup" aria-label="Cryptocurrency">
                {(plan?.currencies || Object.keys(CURRENCY_LABELS)).map((code) => {
                  const meta = currencyLabel(code);
                  return (
                    <button
                      key={code}
                      type="button"
                      role="radio"
                      aria-checked={currency === code}
                      className={`billing-asset${currency === code ? " is-selected" : ""}`}
                      onClick={() => setCurrency(code)}
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
              {error && <p className="billing-error" role="alert">{error}</p>}
              <button type="button" className="billing-primary" onClick={() => void startCheckout()} disabled={busy}>
                {busy ? "Quoting…" : `Pay with ${currency}`}
                <Icon name="arrow" />
              </button>
              <p className="billing-fineprint">
                The exact amount and address are quoted in {currency} for 60 minutes. Send the quoted amount only —
                underpayments are not credited.
              </p>
            </div>
          )}

          {!loading && step === "pay" && checkout && (
            <div className="billing-body">
              <div className="billing-step-head">
                <span className="billing-live"><span className="billing-dot" />Waiting for the network</span>
                {secondsLeft !== null && (
                  <span className={`billing-countdown${secondsLeft < 300 ? " is-late" : ""}`}>
                    {formatCountdown(secondsLeft)} left
                  </span>
                )}
              </div>
              <div className="billing-quote">
                <div className="billing-quote-amount">
                  <span className="billing-label">Send exactly</span>
                  <strong>
                    <CryptoIcon code={checkout.pay_currency || currency} />
                    {checkout.pay_amount ?? "—"} {checkout.pay_currency || currency}
                  </strong>
                  <small>{checkout.amount_label}</small>
                </div>
                {checkout.qr_code && (
                  <img className="billing-qr" src={checkout.qr_code} alt={`${checkout.pay_currency || currency} payment QR code`} />
                )}
              </div>
              <div className="billing-address">
                <span className="billing-label">Address</span>
                <code>{checkout.address || "Address unavailable — reopen checkout."}</code>
                {checkout.address && (
                  <button type="button" className="billing-copy" onClick={() => void copy(checkout.address!, "address")}>
                    {copied === "address" ? "Copied" : "Copy"}
                  </button>
                )}
              </div>
              {checkout.memo && (
                <p className="billing-hint"><strong>Memo required:</strong> {checkout.memo}</p>
              )}
              {error && <p className="billing-error" role="alert">{error}</p>}
              <button type="button" className="billing-primary" onClick={() => void refreshStatus(checkout)}>
                I've sent it — check now
                <Icon name="refresh" />
              </button>
              <p className="billing-fineprint">
                Stay on this page: status refreshes automatically. The gift starts the moment OxaPay confirms
                the transaction, and the owner is notified straight away.
              </p>
            </div>
          )}

          {!loading && step === "done" && (
            <div className="billing-body billing-done">
              <span className="billing-done-mark" aria-hidden="true"><Icon name="check" /></span>
              <h2>Gift on its way</h2>
              <p>
                {selectedTarget?.name || "The server"} has {monthLabel(giftedMonths)} of premium
                {giftedUntil ? ` until ${formatDate(giftedUntil)}` : ""}. The owner has been told who sent it,
                and you got a receipt in your DMs.
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
                  Gift another
                  <Icon name="arrow" />
                </button>
                <button type="button" className="billing-ghost" onClick={() => navigate("/")}>
                  Back to site
                </button>
              </div>
            </div>
          )}

          <footer className="billing-foot">
            <span>Payments by OxaPay</span>
            <span aria-hidden="true">·</span>
            <span>AI moderation by fal.ai</span>
          </footer>
        </section>
      </main>
    </>
  );
}
