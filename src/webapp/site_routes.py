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

@app.route("/llms.txt")
def llms_index():
    return send_from_directory(WEB_DIST_DIR, "llms.txt", mimetype="text/plain")

@app.route("/docs/<slug>.md")
def docs_markdown(slug):
    return send_from_directory(WEB_DIST_DIR, f"docs/{slug}.md", mimetype="text/markdown")

@app.route("/changelog/<slug>.md")
def changelog_markdown(slug):
    return send_from_directory(WEB_DIST_DIR, f"changelog/{slug}.md", mimetype="text/markdown")

@app.route("/commands")
@app.route("/leaderboard")
@app.route("/levels")
@app.route("/docs")
@app.route("/team")
@app.route("/support")
@app.route("/discord")
@app.route("/changelog")
@app.route("/community")
@app.route("/privacy")
@app.route("/terms")
@app.route("/data-removal")
@app.route("/donate")
@app.route("/billing")
@app.route("/transcript/<path:path>")
@app.route("/transcript")
def public_spa_route(path=None):
    return serve_spa_shell()

@app.route("/commands/<path:path>")
@app.route("/levels/<path:path>")
@app.route("/docs/<path:path>")
@app.route("/team/<path:path>")
@app.route("/changelog/<path:path>")
@app.route("/privacy/<path:path>")
@app.route("/terms/<path:path>")
@app.route("/data-removal/<path:path>")
@app.route("/community/<path:path>")
@app.route("/donate/<path:path>")
@app.route("/billing/<path:path>")
@app.route("/dashboard/<path:path>")
def nested_spa_route(path):
    return serve_spa_shell()

@app.route("/dashboard.html")
def legacy_dashboard_redirect():
    return redirect("/dashboard")
