import { useCallback, useEffect, useMemo, useState } from "react";
import { api, ApiError, getAuth } from "../api";
import { CryptoIcon } from "../components/CryptoIcon";
import { Icon } from "../components/Icon";
import { PublicHeader } from "../components/PublicHeader";
import { navigate } from "../router";

type Perk = { key: string; title: string; description: string };

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
      // Only servers the member manages can be upgraded; gifting has its own
      // page and its own (membership-based) list.
      const result = await api<{ guilds: PlanGuild[] }>("/api/premium/guilds");
      setTargets(result.guilds);
      if (!guildId && result.guilds.length === 1) setGuildId(result.guilds[0].id);
    } catch (reason) {
      if (reason instanceof ApiError && reason.status === 401) setTargets([]);
      else setTargetsError(reason instanceof Error ? reason.message : "Your servers could not be loaded.");
    }
  }, [guildId]);

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
            body: JSON.stringify({ token, amount: Number.parseFloat(amount), currency }),
          })
        : await api<Checkout>("/api/premium/checkout", {
            method: "POST",
            headers: csrf ? { "X-CSRF-Token": csrf } : undefined,
            body: JSON.stringify({ guild_id: guildId, pay_currency: currency }),
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

  const canPay = isDonation
    ? Number.parseFloat(amount) >= (meta?.min_amount ?? 1)
    : Boolean(guildId);

  const heading = isDonation ? "Support Niko" : "Niko Premium";

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
              {isDonation ? "One-off donation" : "Monthly subscription"}
            </span>
            <h1 id="billing-title">{heading}</h1>
            <p>
              {isDonation
                ? "Every dollar covers hosting, the AI moderation API, and the new niko.sryze.cc domain."
                : "AI image moderation for your community, billed monthly. Cancel by simply not renewing."}
            </p>
          </header>

          {!isDonation && plan && (
            <div className="billing-price">
              <strong>{plan.price_label}</strong>
              <span>per server / month</span>
            </div>
          )}

          {loading && <div className="billing-loading"><span className="loading-ring" /><p>Preparing checkout…</p></div>}

          {!loading && step === "method" && (
            <div className="billing-body">
              {!isDonation && (
                <div className="billing-field">
                  <span className="billing-label">Server</span>
                  {targets === null ? (
                    <div className="billing-skeleton" aria-hidden="true" />
                  ) : targets.length === 0 ? (
                    <p className="billing-hint">
                      <a href={loginHref}>Sign in with Discord</a> to choose a server.
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
                    <p className="billing-hint">That server is not one you can manage. Pick another below.</p>
                  )}
                  {targets && targets.length > 0 && (
                    <p className="billing-hint">
                      Buying for a community you are in but do not manage?{" "}
                      <a href={`/billing/gift${guildId ? `?guild=${guildId}` : ""}`}>Gift premium instead</a>.
                    </p>
                  )}
                </div>
              )}

              {isDonation && (
                <div className="billing-field">
                  <span className="billing-label">Amount (USD)</span>
                  <div className="billing-presets" role="group" aria-label="Suggested amounts">
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
                      aria-label="Donation amount in USD"
                    />
                  </div>
                  <p className="billing-hint">
                    Minimum ${meta?.min_amount ?? 1}. A receipt and Supporter badge arrive after the network confirms.
                  </p>
                  {meta && meta.totals.donation_count > 0 && (
                    <div className="billing-supporter-totals">
                      <p>
                        <strong>{formatUsd(meta.totals.total_cents)}</strong> raised by{" "}
                        {meta.totals.donor_count.toLocaleString()} supporter{meta.totals.donor_count === 1 ? "" : "s"}{" "}
                        across {meta.totals.donation_count.toLocaleString()} donation{meta.totals.donation_count === 1 ? "" : "s"}.
                      </p>
                      {meta.goal_cents > 0 && (
                        <div
                          className="billing-goal"
                          role="progressbar"
                          aria-valuemin={0}
                          aria-valuemax={meta.goal_cents}
                          aria-valuenow={Math.min(meta.totals.total_cents, meta.goal_cents)}
                          aria-label="Donation goal"
                        >
                          <i style={{ width: `${Math.min(100, Math.round((meta.progress || 0) * 100))}%` }} />
                        </div>
                      )}
                      {meta.your_total_cents > 0 && (
                        <p className="billing-hint">You have donated {formatUsd(meta.your_total_cents)} so far. Thank you!</p>
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
                    <span><strong>Renewal reminder</strong><small>We DM the owner {plan.renewal_notice_days} days before the term ends.</small></span>
                  </li>
                </ul>
              )}

              <div className="billing-methods" role="radiogroup" aria-label="Payment method">
                <button type="button" className="billing-method" disabled aria-disabled="true">
                  <span className="billing-method-icon"><Icon name="lock" /></span>
                  <span><strong>Card</strong><small>Visa, Mastercard, Amex</small></span>
                  <span className="billing-chip">Coming soon</span>
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
                  <span><strong>Crypto</strong><small>USDT, Bitcoin, Ethereum and more</small></span>
                  <Icon name="arrow" />
                </button>
              </div>
              {!plan?.methods.crypto.enabled && !isDonation && (
                <p className="billing-error" role="alert">Payments are not configured on this deployment yet.</p>
              )}
              {error && <p className="billing-error" role="alert">{error}</p>}
            </div>
          )}

          {!loading && step === "asset" && (
            <div className="billing-body">
              <div className="billing-step-head">
                <button type="button" className="billing-back" onClick={() => { setStep("method"); setError(""); }}>
                  ← Back
                </button>
                <span className="billing-step-count">Step 2 of 2</span>
              </div>
              <div className="billing-summary">
                <div>
                  <span className="billing-label">Paying</span>
                  <strong>{isDonation ? `$${Number.parseFloat(amount).toFixed(2)} USD` : plan?.price_label}</strong>
                </div>
                <div>
                  <span className="billing-label">{isDonation ? "To" : "Server"}</span>
                  <strong>{isDonation ? "Niko" : selectedTarget?.name || `Server ${guildId}`}</strong>
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
                Stay on this page: status refreshes automatically. Premium activates the moment OxaPay
                confirms the transaction, and a receipt lands in your DMs.
              </p>
            </div>
          )}

          {!loading && step === "done" && (
            <div className="billing-body billing-done">
              <span className="billing-done-mark" aria-hidden="true"><Icon name="check" /></span>
              <h2>{isDonation ? "Thank you for supporting Niko" : "Premium is active"}</h2>
              <p>
                {isDonation
                  ? "Your donation is confirmed. The Supporter badge is applied in the support server."
                  : `AI image moderation is unlocked${paidUntil ? ` until ${formatDate(paidUntil)}` : ""}. Turn it on under Moderation in the dashboard.`}
              </p>
              {isDonation && checkout && (
                <div className="billing-receipt">
                  <div>
                    <span className="billing-label">Amount</span>
                    <strong>{checkout.amount_label}</strong>
                  </div>
                  <div>
                    <span className="billing-label">Track ID</span>
                    <code>{checkout.track_id || checkout.order_id}</code>
                  </div>
                  <p className="billing-hint">
                    Keep the track ID for <code>/donationstatus</code>. A receipt is waiting in your DMs.
                  </p>
                </div>
              )}
              <div className="billing-done-actions">
                <button type="button" className="billing-primary" onClick={() => navigate(isDonation ? "/" : `/dashboard/${guildId}/moderation`)}>
                  {isDonation ? "Back to site" : "Open moderation"}
                  <Icon name="arrow" />
                </button>
                {!isDonation && (
                  <button type="button" className="billing-ghost" onClick={() => navigate("/dashboard")}>
                    Go to dashboard
                  </button>
                )}
              </div>
              {paid && <span className="billing-sr" role="status">Payment confirmed</span>}
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

