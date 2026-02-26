import os
from flask import Flask, send_from_directory

app = Flask(
    __name__,
    static_folder="website",
    static_url_path=""
)

app.secret_key = os.urandom(24)

@app.route("/")
def root():
    return send_from_directory("website", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("website", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)