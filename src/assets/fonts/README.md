# Bundled Unicode fonts

Place the regular and bold font files used by the image renderer in this directory.
The resolver prefers this directory, then falls back to Termux, Android, Linux, and
macOS font locations. It loads every `.ttf`/`.otf` file here and selects a face per
glyph, so adding a broad Unicode family (for example Noto Sans plus its regional
and symbol faces) extends coverage without changing the renderer.

Bundled faces (all SIL Open Font License 1.1, from the Noto project):

| File | Covers |
| --- | --- |
| `NotoSans-Regular.ttf` | Latin, Greek, Cyrillic, and most common symbols |
| `NotoSansBamum-Regular.ttf` | Bamum (U+A6A0–U+A6FF) |
| `NotoSansHebrew-Regular.ttf` | Hebrew |
| `NotoSansMath-Regular.ttf` | Mathematical operators and symbols |
| `NotoSansSymbols-Regular.ttf` | Miscellaneous symbols, dingbats |
| `NotoSansSymbols2-Regular.ttf` | Symbols and pictographs fallback |
| `NotoSansTaiLe-Regular.ttf` | Tai Le (U+1950–U+197F) |
| `NotoSansTaiViet-Regular.ttf` | Tai Viet (U+AA80–U+AADF) |
| `NotoSansLimbu-Regular.ttf` | Limbu (U+1900–U+194F) |

A display name such as `ᥒꪗ᥊ꫀᥒ` mixes Tai Le, Tai Viet and Limbu letters, so the
leveling and economy cards need all three of those faces to draw it instead of
rendering tofu boxes. When a new card would need another script, download the
matching `NotoSans<Script>-Regular.ttf` from
`https://github.com/notofonts/notofonts.github.io/tree/main/fonts` into this
directory and list it here.
