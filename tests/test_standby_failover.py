import asyncio
import json
import unittest
from unittest.mock import patch

from utils.standby_failover import _handle_client, control_proof, secret_key, verification_proof
from utils.standby_manager import StandbyFailoverManager
from webapp.standby_routes import _verification_matches


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


class StandbyFailoverTests(unittest.TestCase):
    def test_registration_proof_requires_both_production_secrets(self):
        key = secret_key("production-token", "production-session")
        nonce = "unique-standby-registration-challenge"
        proof = verification_proof(key, nonce)

        self.assertTrue(_verification_matches(key, nonce, proof))
        self.assertFalse(_verification_matches(secret_key("other-token", "production-session"), nonce, proof))
        self.assertFalse(_verification_matches(secret_key("production-token", "other-session"), nonce, proof))
        self.assertFalse(_verification_matches(key, nonce, None))

    def test_health_identifies_standby_backend(self):
        async def scenario():
            reader = asyncio.StreamReader()
            reader.feed_data(b"GET /health HTTP/1.1\r\nHost: standby.example\r\n\r\n")
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, secret_key("token", "session"))
            self.assertIn(b'"service":"niko-standby-backend"', writer.data)
            self.assertNotIn(b"proxy", writer.data.lower())

        asyncio.run(scenario())

    def test_authenticated_gateway_control_rejects_replayed_nonce(self):
        from utils import standby_failover

        class Controller:
            def __init__(self):
                self.actions = []

            async def activate(self):
                self.actions.append("activate")

            async def relinquish(self):
                self.actions.append("relinquish")

        async def send_request(key, nonce, proof):
            body = json.dumps({"action": "activate", "nonce": nonce, "proof": proof}).encode()
            raw = (
                b"POST /internal/standby/control HTTP/1.1\r\nContent-Length: "
                + str(len(body)).encode()
                + b"\r\n\r\n"
                + body
            )
            reader = asyncio.StreamReader()
            reader.feed_data(raw)
            reader.feed_eof()
            writer = FakeWriter()
            await _handle_client(reader, writer, key)
            return writer.data

        async def scenario():
            key = secret_key("token", "session")
            controller = Controller()
            standby_failover._GATEWAY_CONTROLLER = controller
            standby_failover._CONTROL_NONCES.clear()
            nonce = "standby-control-nonce-00000000000001"
            proof = control_proof(key, "activate", nonce)
            self.assertIn(b"200 OK", await send_request(key, nonce, proof))
            self.assertIn(b"403", await send_request(key, nonce, proof))
            self.assertEqual(["activate"], controller.actions)
            standby_failover._GATEWAY_CONTROLLER = None
            standby_failover._CONTROL_NONCES.clear()

        asyncio.run(scenario())

    def test_manager_selects_healthy_full_backend(self):
        async def scenario():
            manager = StandbyFailoverManager()
            manager.set_standbys(["https://east.example"], ["standby-east"])
            with patch.object(manager, "probe_standby", return_value={"service": "niko-standby-backend"}):
                self.assertTrue(await manager.activate_standby("standby-east"))
                self.assertFalse(await manager.activate_standby("unknown"))
            self.assertEqual("standby-east", manager.status()["active_standby_id"])
            self.assertEqual("standby", manager.status()["mode"])

        asyncio.run(scenario())

    def test_webshare_proxy_configuration_is_not_part_of_standby_control(self):
        manager = StandbyFailoverManager()
        manager.set_standbys(["https://east.example"], ["standby-east"])
        manager.active_origin = "https://east.example"

        self.assertTrue(manager.select_failover("auto"))
        self.assertEqual("https://east.example", manager.active_origin)
        with self.assertRaisesRegex(ValueError, "auto or off"):
            manager.select_failover("webshare")
        self.assertTrue(manager.select_failover("off"))
        self.assertIsNone(manager.active_origin)
        self.assertEqual("off", manager.status()["mode"])


if __name__ == "__main__":
    unittest.main()
