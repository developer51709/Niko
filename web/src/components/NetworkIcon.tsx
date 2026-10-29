import type { CSSProperties } from "react";

/**
 * Blockchain network marks for the checkout network picker.
 *
 * Where a chain's logo is the currency logo (Bitcoin, Ethereum, BNB Chain,
 * TRON, Litecoin, Dogecoin, Monero) the existing Cryptofonts silhouette in
 * `web/public/crypto/` is reused. Solana and Polygon come from the same
 * Cryptofonts pack, TON from Simple Icons (CC0), and Base is drawn here: a
 * filled circle with a bar cut out. Like `CryptoIcon`, the files are painted
 * through a CSS mask so a mark takes whatever `color` it is given.
 */
type Network = { brand: string; file: string };

const NETWORKS: Record<string, Network> = {
  Bitcoin: { brand: "#f7931a", file: "btc" },
  Ethereum: { brand: "#8f9cd8", file: "eth" },
  BSC: { brand: "#f3ba2f", file: "bnb" },
  Tron: { brand: "#ef3b3b", file: "trx" },
  Solana: { brand: "#9a6bff", file: "sol" },
  Polygon: { brand: "#8247e5", file: "matic" },
  "The Open Network": { brand: "#0098ea", file: "ton" },
  Base: { brand: "#3d7dff", file: "base" },
  Litecoin: { brand: "#a9aeb1", file: "ltc" },
  Dogecoin: { brand: "#c9a94a", file: "doge" },
  Monero: { brand: "#ff7a33", file: "xmr" },
};

/**
 * One network logo. A network the API adds later falls back to `fallback`
 * instead of leaving an empty slot in the picker.
 */
export function NetworkIcon({ network, fallback }: { network: string; fallback?: string }) {
  const mark = NETWORKS[network] || NETWORKS[network.trim()];
  if (!mark) return <>{fallback ?? null}</>;

  return (
    <span
      className="crypto-icon network-icon"
      style={
        {
          "--crypto-glyph": `url(/crypto/${mark.file}.svg)`,
          "--crypto-brand": mark.brand,
        } as CSSProperties
      }
      aria-hidden="true"
    />
  );
}
