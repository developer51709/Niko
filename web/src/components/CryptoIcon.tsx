import type { CSSProperties } from "react";

/**
 * Cryptocurrency brand marks taken from CryptoFonts (https://cryptofonts.com),
 * `@cryptofonts/cryptofont` v1.3.5 (ISC). The files in `web/public/crypto/` are
 * single-colour silhouettes, so they are painted through a CSS mask: the icon
 * takes whatever `color` it is given and stays crisp at any size.
 */
type Coin = { brand: string; file: string };

const COINS: Record<string, Coin> = {
  USDT: { brand: "#26a17b", file: "usdt" },
  ETH: { brand: "#8f9cd8", file: "eth" },
  BTC: { brand: "#f7931a", file: "btc" },
  BNB: { brand: "#f3ba2f", file: "bnb" },
  LTC: { brand: "#a9aeb1", file: "ltc" },
  DOGE: { brand: "#c9a94a", file: "doge" },
  TRX: { brand: "#ef3b3b", file: "trx" },
  XMR: { brand: "#ff7a33", file: "xmr" },
};

/**
 * One coin logo. Unknown tickers render `fallback` instead of an empty box, so
 * a currency the API adds later still shows *something* in the picker.
 */
export function CryptoIcon({ code, fallback }: { code: string; fallback?: string }) {
  const coin = COINS[code.toUpperCase()];
  if (!coin) return <>{fallback ?? null}</>;

  return (
    <span
      className="crypto-icon"
      style={
        {
          "--crypto-glyph": `url(/crypto/${coin.file}.svg)`,
          "--crypto-brand": coin.brand,
        } as CSSProperties
      }
      aria-hidden="true"
    />
  );
}
