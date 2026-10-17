# Bundled Unicode fonts

Place the regular and bold font files used by the image renderer in this directory.
The resolver prefers this directory, then falls back to Termux, Android, Linux, and
macOS font locations. It loads every `.ttf`/`.otf` file here and selects a face per
glyph, so adding a broad Unicode family (for example Noto Sans plus its regional
and symbol faces) extends coverage without changing the renderer.
