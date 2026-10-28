// The bot's custom emojis, read from the bot itself at runtime.
//
// This module used to be generated from src/config/emojis.py by
// scripts/build-bot-emojis.mjs, so the list only changed when somebody ran that
// script: an emoji that was added, renamed or re-uploaded stayed dead here
// until then, and a re-upload always changes the id — Discord cannot replace an
// emoji's art, so new art means a new emoji.
//
// `/api/emojis` parses the bot's config on every request together with the ids
// its emoji sync has re-uploaded, so the rendering lab, the emoji popups and
// the bot always draw the same names and ids with no build step to forget.

import { useEffect, useState } from "react";
import { getBotEmojis } from "../api";
import type { BotEmoji } from "../types";

let catalog: BotEmoji[] = [];
let applicationIds: ReadonlySet<string> = new Set();
let failed = false;
let pending: Promise<BotEmoji[]> | null = null;
const listeners = new Set<() => void>();

/** The `<:name:id>` token Discord and the bot use for this emoji. */
export function botEmojiToken(emoji: BotEmoji): string {
  return `<${emoji.animated ? "a" : ""}:${emoji.name}:${emoji.id}>`;
}

/** The catalog as it stands right now; empty until the one fetch resolves. */
export function botEmojis(): BotEmoji[] {
  return catalog;
}

/** Whether an id belongs to the Niko application rather than to a server. */
export function isApplicationEmoji(id: string): boolean {
  return applicationIds.has(id);
}

/**
 * Whether the catalog could not be read, so a surface can say so instead of
 * drawing an empty list as if the bot had no emojis.
 */
export function botEmojisFailed(): boolean {
  return failed;
}

/** Fetch the catalog once per page and share it with every subscriber. */
function ensureBotEmojis(): Promise<BotEmoji[]> {
  if (!pending) {
    pending = getBotEmojis()
      .then((response) => {
        catalog = response.emojis;
        applicationIds = new Set(catalog.map((emoji) => emoji.id));
        failed = false;
        listeners.forEach((listener) => listener());
        return catalog;
      })
      .catch(() => {
        // The lab and the popups keep their fallback behaviour, and a later
        // subscriber may retry the failed load.
        failed = true;
        pending = null;
        listeners.forEach((listener) => listener());
        return catalog;
      });
  }
  return pending;
}

/** The bot's emojis for a component, re-rendering once they arrive. */
export function useBotEmojis(): BotEmoji[] {
  const [emojis, setEmojis] = useState<BotEmoji[]>(() => botEmojis());

  useEffect(() => {
    const listener = () => setEmojis(botEmojis());
    listeners.add(listener);
    void ensureBotEmojis();
    setEmojis(botEmojis());
    return () => { listeners.delete(listener); };
  }, []);

  return emojis;
}
