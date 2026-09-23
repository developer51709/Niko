"""Flask routes for site."""

from . import server as _server

globals().update({
    name: value
    for name, value in vars(_server).items()
    if not name.startswith("__")
})

@app.route("/")
def root():
    return send_from_directory(WEB_DIST_DIR, "index.html")

@app.route("/dashboard")
def dashboard_redirect():
    return send_from_directory(WEB_DIST_DIR, "index.html")

@app.route("/support")
def support_metadata_page():
    return send_from_directory(WEB_DIST_DIR, "support/index.html")

@app.route("/discord")
def discord_metadata_page():
    return send_from_directory(WEB_DIST_DIR, "discord/index.html")

@app.route("/commands")
@app.route("/docs")
@app.route("/privacy")
@app.route("/terms")
@app.route("/donate")
@app.route("/transcript/<path:path>")
@app.route("/transcript")
def public_spa_route(path=None):
    return serve_spa_shell()

@app.route("/commands/<path:path>")
@app.route("/docs/<path:path>")
@app.route("/privacy/<path:path>")
@app.route("/terms/<path:path>")
@app.route("/donate/<path:path>")
@app.route("/dashboard/<path:path>")
def nested_spa_route(path):
    return serve_spa_shell()

@app.route("/dashboard.html")
def legacy_dashboard_redirect():
    return redirect("/dashboard")

@app.route("/<path:path>")

# ── SVG Card Endpoints ──────────────────────────────────────────────────────
# These return SVG markup that wsrv.nl converts to PNG for Discord rendering.
# Query parameters supply card data; a timestamp param busts CDN caches.


def _svg_wrap(body, width, height):
    """Wrap SVG body in a proper document and return as image/svg+xml."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="' + str(width) + '" height="' + str(height) + '" '
        'viewBox="0 0 ' + str(width) + ' ' + str(height) + '">'
        '<style>'
        '@import url("https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;family=Space+Mono:wght@400;700&amp;display=swap");'
        '</style>'
        + body +
        '</svg>'
    )
    return Response(svg, mimetype="image/svg+xml")
