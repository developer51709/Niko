import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import api_server


def test_api_server_binds_an_explicit_loopback_ephemeral_port():
    api_server.stop_api_server()
    try:
        api_server.start_api_server(None, host="127.0.0.1", port=0)
        port = api_server.listening_port()

        assert port > 0
        assert api_server._server.server_address[0] == "127.0.0.1"
        response = requests.get(f"http://127.0.0.1:{port}/health", timeout=5)
        assert response.status_code == 200
        assert response.json()["ok"] is True
    finally:
        api_server.stop_api_server()
