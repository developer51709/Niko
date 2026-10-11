import asyncio
import base64
import unittest
from unittest.mock import patch

from utils.backup_proxy import (
    _allowed_host,
    _handle_client,
    backup_proxy_url,
    proxy_password,
    secret_key,
    verification_proof,
)
from utils.proxy_manager import WebshareProxyManager
from webapp.backup_routes import _verification_matches


class FakeWriter:
    def __init__(self):
        self.data = bytearray()
        self.closed = False

    def write(self, value):
        self.data.extend(value)

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        return None

    def write_eof(self):
        return None


class BackupProxyTests(unittest.TestCase):
    def test_challenge_matches_only_when_both_secrets_match(self):
        key = secret_key("prod-token", "prod-session")
        nonce = "fresh-random-nonce-value-long-enough"
        expected = verification_proof(key, nonce)
        self.assertEqual(expected, verification_proof(secret_key("prod-token", "prod-session"), nonce))
        self.assertNotEqual(expected, verification_proof(secret_key("other-token", "prod-session"), nonce))
        self.assertNotEqual(expected, verification_proof(secret_key("prod-token", "other-session"), nonce))

    def test_registration_requires_exact_proof_from_both_production_secrets(self):
        nonce = "unique-registration-challenge-nonce"
        production_key = secret_key("production-token", "production-session")
        valid_proof = verification_proof(production_key, nonce)

        self.assertTrue(_verification_matches(production_key, nonce, valid_proof))
        self.assertFalse(
            _verification_matches(
                secret_key("different-token", "production-session"), nonce, valid_proof
            )
        )
        self.assertFalse(
            _verification_matches(
                secret_key("production-token", "different-session"), nonce, valid_proof
            )
        )
        self.assertFalse(_verification_matches(production_key, nonce, None))
        self.assertFalse(_verification_matches(production_key, nonce, ""))

    def test_health_endpoint_is_available_through_http_ingress(self):
        async def scenario():
            key = secret_key("token", "session")
            reader = asyncio.StreamReader()
            reader.feed_data(b"GET /health HTTP/1.1\r\nHost: standby.example\r\n\r\n")
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            self.assertIn(b"200 OK", writer.data)
            self.assertIn(b'"service":"niko-backup-proxy"', writer.data)

        asyncio.run(scenario())

    def test_render_mode_starts_without_certificate_files(self):
        from utils.backup_proxy import serve_backup_proxy

        async def scenario():
            server = await serve_backup_proxy("127.0.0.1", 0, None, None, "token", "session")
            self.assertIsNotNone(server.sockets)
            server.close()
            await server.wait_closed()

        asyncio.run(scenario())

    def test_proxy_url_requires_https_origin(self):
        self.assertTrue(backup_proxy_url("https://backup.example.org", secret_key("a", "b")).startswith("https://niko-backup:"))
        with self.assertRaises(ValueError):
            backup_proxy_url("http://backup.example.org", secret_key("a", "b"))
        with self.assertRaises(ValueError):
            backup_proxy_url("https://backup.example.org/path", secret_key("a", "b"))

    def test_connect_is_allowlisted_to_discord_tls(self):
        self.assertEqual(("discord.com", 443), _allowed_host("discord.com:443"))
        self.assertEqual(("gateway.discord.gg", 443), _allowed_host("gateway.discord.gg:443"))
        self.assertIsNone(_allowed_host("example.org:443"))
        self.assertIsNone(_allowed_host("discord.com:80"))
        self.assertIsNone(_allowed_host("127.0.0.1:443"))

    def test_verify_challenge_returns_proof_but_not_credentials(self):
        async def scenario():
            key = secret_key("token-secret", "session-secret")
            nonce = "N" * 40
            body = (f'{{"nonce":"{nonce}"}}').encode()
            request = (b"POST /internal/backup/verify HTTP/1.1\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
            reader = asyncio.StreamReader()
            reader.feed_data(request)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            response = writer.data.decode()
            self.assertIn(verification_proof(key, nonce), response)
            self.assertNotIn("token-secret", response)
            self.assertNotIn("session-secret", response)
        asyncio.run(scenario())

    def test_authenticated_proxy_disallows_non_discord_connect_targets(self):
        async def scenario():
            key = secret_key("token", "session")
            auth = base64.b64encode(f"niko-backup:{proxy_password(key)}".encode())
            request = b"CONNECT example.org:443 HTTP/1.1\r\nProxy-Authorization: Basic " + auth + b"\r\n\r\n"
            reader = asyncio.StreamReader()
            reader.feed_data(request)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            self.assertIn(b"403", writer.data)
        asyncio.run(scenario())

    def test_manager_falls_back_to_registered_standby(self):
        async def scenario():
            manager = WebshareProxyManager(None)
            manager.http = type("Http", (), {"proxy": None, "proxy_auth": None})()
            manager.set_backup_proxies(["https://niko-backup:pass@backup.example.org"])
            with patch.object(manager, "_ensure_verify_task"):
                await manager.enable()
            self.assertEqual("https://niko-backup:pass@backup.example.org", manager.http.proxy)
            self.assertTrue(manager.enabled)
            manager.disable()
            self.assertIsNone(manager.http.proxy)
        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
