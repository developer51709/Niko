import os
from flask import Flask, send_from_directory

app = Flask(
    __name__,
    static_folder="website",      # your static folder
    static_url_path=""            # serve files at root URL
)

app.secret_key = os.urandom(24)

# Serve index.html when visiting the root
@app.route("/")
def home():
    return send_from_directory("website", "index.html")

# Optional: serve any file inside the website folder
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("website", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)