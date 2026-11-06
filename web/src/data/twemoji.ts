/**
 * Twemoji's own artwork for a Unicode emoji, which is what Discord draws.
 *
 * Variation selectors (`\uFE0E`/`\uFE0F`) are not part of the asset name, so a
 * text-style or emoji-style spelling of the same character resolves to one SVG.
 */
export function twemojiUrl(value: string) {
  const codepoints = Array.from(value)
    .filter((character) => character !== "\uFE0E" && character !== "\uFE0F")
    .map((character) => character.codePointAt(0)!.toString(16))
    .join("-");
  return `https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/${codepoints}.svg`;
}
