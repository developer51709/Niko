"""
Gateway IDENTIFY patcher.
Spoofs the Discord client device on the very first WebSocket handshake.
"""
from utils import logging


def patch_identify(device: str):
    """
    Patches discord.py's IDENTIFY payload to spoof the client device.
    device: 'normal', 'mobile_ios', 'mobile_android', 'vr', 'embedded'
    """
    import discord.gateway as gateway

    _DEVICES: dict[str, tuple[dict, dict]] = {
        "mobile_ios": (
            {"os": "iOS", "browser": "Discord iOS", "device": "Discord iOS",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 30717},
        ),
        "mobile_android": (
            {"os": "Android", "browser": "Discord Android", "device": "Discord Android",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 30717},
        ),
        "vr": (
            {"os": "Android", "browser": "Quest", "device": "Quest",
             "system_locale": "en-US", "browser_version": "", "os_version": "12",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 125},
        ),
        "embedded": (
            {"os": "Linux", "browser": "Discord Embedded", "device": "",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 8189},
        ),
        "normal": (
            {"os": "Windows", "browser": "Discord", "device": "",
             "system_locale": "en-US", "browser_version": "", "os_version": "",
             "referrer": "", "referring_domain": "",
             "referrer_current": "", "referring_domain_current": "",
             "release_channel": "stable", "client_build_number": 0,
             "native_build_number": None, "client_event_source": None},
            {"capabilities": 16381},
        ),
    }

    if device not in _DEVICES:
        logging.warning("DeviceSpoof", f"Unknown STATUS_DEVICE '{device}', falling back to 'normal'.")

    target_props, target_extra = _DEVICES.get(device, _DEVICES["normal"])
    logging.info("DeviceSpoof", f"Patching gateway IDENTIFY — device={device!r}, capabilities={target_extra.get('capabilities')}")

    _original_identify = gateway.DiscordWebSocket.identify

    async def identify_spoof(self):
        _orig_send = self.send_as_json

        async def _intercept(data):
            if isinstance(data, dict) and data.get("op") == self.IDENTIFY:
                data["d"]["properties"] = target_props
                data["d"].update(target_extra)
            await _orig_send(data)

        self.send_as_json = _intercept
        try:
            await _original_identify(self)
        finally:
            self.send_as_json = _orig_send

    gateway.DiscordWebSocket.identify = identify_spoof
