import { type FormEvent, useEffect, useState } from "react";
import { api } from "../api";
import { PublicHeader } from "../components/PublicHeader";
import { Icon } from "../components/Icon";
import { navigate } from "../router";

type InvoiceResult = {
  ok: boolean;
  order_id?: string;
  track_id?: string;
  pay_link?: string;
  status_url?: string;
  error?: string;
};

type InvoiceStatus = {
  status: string;
  paid: boolean;
};

const CURRENCIES = [
  { code: "USDT", label: "Tether" },
  { code: "ETH", label: "Ethereum" },
  { code: "BTC", label: "Bitcoin" },
  { code: "BNB", label: "BNB" },
  { code: "LTC", label: "Litecoin" },
  { code: "DOGE", label: "Dogecoin" },
  { code: "TRX", label: "TRON" },
  { code: "XMR", label: "Monero" },
];

export function DonatePage() {
  const params = new URLSearchParams(window.location.search);
  const token = params.get("token") || "";

  const [amount, setAmount] = useState("5");
  const [currency, setCurrency] = useState("USDT");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [invoice, setInvoice] = useState<InvoiceResult | null>(null);
  const [status, setStatus] = useState<InvoiceStatus | null>(null);
  const [invalidToken, setInvalidToken] = useState(false);

  useEffect(() => {
    if (!token) setInvalidToken(true);
  }, [token]);

  // Poll for payment status after invoice creation
  useEffect(() => {
    if (!invoice?.status_url || invoice.paid) return;
    const interval = setInterval(async () => {
      try {
        const result = await api<InvoiceStatus>(invoice.status_url!);
        setStatus(result);
        if (result.paid) clearInterval(interval);
      } catch {
        // Ignore polling errors
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [invoice]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const result = await api<InvoiceResult>("/api/donations/invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, amount: parseFloat(amount), currency }),
      });
      setInvoice(result);
      if (result.error) {
        setError(result.error);
        setInvoice(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create invoice.");
    } finally {
      setLoading(false);
    }
  };

  if (invalidToken) {
    return (
      <>
        <PublicHeader page="home" />
        <main className="auth-page">
          <div className="auth-card" style={{ textAlign: "center" }}>
            <span className="auth-mark">!</span>
            <div className="eyebrow">Invalid donation link</div>
            <h1>
              This link is <em>invalid.</em>
            </h1>
            <p>
              The donation link is missing or has expired. Use the{" "}
              <code>/donate</code> command in Discord to generate a new one.
            </p>
            <button
              className="button button-primary full-width"
              onClick={() => navigate("/")}
            >
              Return home
            </button>
          </div>
        </main>
      </>
    );
  }

  if (status?.paid) {
    return (
      <>
        <PublicHeader page="home" />
        <main className="auth-page">
          <div className="auth-card" style={{ textAlign: "center" }}>
            <span className="auth-mark">✓</span>
            <div className="eyebrow">Payment confirmed</div>
            <h1>
              Thank you <em>for supporting!</em>
            </h1>
            <p>
              Your donation has been confirmed. You will receive the Supporter
              badge shortly.
            </p>
            <button
              className="button button-primary full-width"
              onClick={() => navigate("/")}
            >
              Return home
            </button>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <PublicHeader page="home" />
      <main className="page-main">
        <div className="shell">
          <div className="page-heading" style={{ maxWidth: 500, margin: "0 auto" }}>
            <div className="eyebrow" style={{ marginBottom: 15 }}>
              Support Niko
            </div>
            <h1>
              Keep Niko <em>running.</em>
            </h1>
            <p style={{ color: "var(--muted)", marginBottom: 30 }}>
              Your donation helps cover hosting costs and keeps Niko running for
              all servers. Choose an amount and cryptocurrency below.
            </p>

            {invoice?.pay_link ? (
              <div className="dash-panel" style={{ marginBottom: 24 }}>
                <div className="panel-heading">
                  <div>
                    <span className="panel-kicker">Invoice created</span>
                    <h3>Complete your payment</h3>
                  </div>
                </div>
                <p style={{ color: "var(--muted)", fontSize: 12, marginBottom: 16 }}>
                  Amount: <strong>${parseFloat(amount).toFixed(2)} USD</strong> in{" "}
                  <strong>{currency}</strong>
                </p>
                <p style={{ color: "var(--dim)", fontSize: 10, marginBottom: 16 }}>
                  Track ID: <code>{invoice.track_id}</code> · Expires in 60 minutes
                </p>
                <a
                  className="button button-primary"
                  href={invoice.pay_link}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Pay now <Icon name="arrow" />
                </a>
                <p style={{ color: "var(--dim)", fontSize: 10, marginTop: 12 }}>
                  Payment will be confirmed automatically once the transaction is
                  processed on-chain.
                </p>
              </div>
            ) : (
              <form onSubmit={submit} className="dash-panel" style={{ marginBottom: 24 }}>
                <div className="form-grid">
                  <label className="form-field">
                    <span className="form-label">Amount (USD)</span>
                    <input
                      type="number"
                      min="1"
                      max="10000"
                      step="0.01"
                      value={amount}
                      onChange={(e) => setAmount(e.target.value)}
                    />
                    <small>Minimum $1.00, maximum $10,000.00</small>
                  </label>
                  <label className="form-field">
                    <span className="form-label">Cryptocurrency</span>
                    <select
                      value={currency}
                      onChange={(e) => setCurrency(e.target.value)}
                    >
                      {CURRENCIES.map((c) => (
                        <option key={c.code} value={c.code}>
                          {c.label} ({c.code})
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
                {error && (
                  <p className="form-error" style={{ marginTop: 12 }} role="alert">
                    {error}
                  </p>
                )}
                <div style={{ marginTop: 16 }}>
                  <button
                    className="button button-primary"
                    type="submit"
                    disabled={loading}
                  >
                    {loading ? "Creating invoice…" : "Create invoice"}
                  </button>
                </div>
              </form>
            )}

            <div className="docs-footer-note" style={{ marginTop: 20 }}>
              <strong>How it works</strong>
              <p>
                1. Choose an amount and currency above · 2. Click "Pay now" to
                open the payment page · 3. Send crypto to the displayed address ·
                4. Payment is confirmed automatically once processed on-chain
              </p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
