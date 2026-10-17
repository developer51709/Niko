import { useEffect, useState } from "react";
import { getPublicConfig } from "../api";
import type { PublicConfig } from "../types";

let cachedConfig: PublicConfig | null = null;
let pendingConfig: Promise<PublicConfig> | null = null;

export function useBotConfig() {
  const [config, setConfig] = useState<PublicConfig | null>(cachedConfig);

  useEffect(() => {
    if (!pendingConfig) pendingConfig = getPublicConfig().then((value) => (cachedConfig = value));
    pendingConfig.then(setConfig).catch(() => undefined);
  }, []);

  return config;
}