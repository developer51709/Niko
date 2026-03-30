import json
import requests
import sys
import traceback

def censor(url: str) -> str:
    """Censor the webhook URL so logs are safe."""
    if "discord.com/api/webhooks/" not in url:
        return "***"
    parts = url.split("/")
    # Keep only the last ID partially visible
    return f"https://discord.com/api/webhooks/{parts[-2]}/***"

try:
    webhook = sys.argv[1]
    author = sys.argv[2]
    message = sys.argv[3]
    sha = sys.argv[4]
    repo_url = sys.argv[5]
    commit_url = sys.argv[6]

    # Debug: show sanitized webhook
    print(f"[DEBUG] Using webhook: {censor(webhook)}")

    # Escape newlines for CV2 compatibility
    message = message.replace("\n", "\\n")

    payload = [
        {
            "type": 17,
            "accent_color": 1146986,
            "spoiler": False,
            "components": [
                {
                    "type": 10,
                    "content": "### New Commit"
                },
                {
                    "type": 14,
                    "divider": True,
                    "spacing": 1
                },
                {
                    "type": 10,
                    "content": (
                        f"**Author:**\\n{author}\\n\\n"
                        f"**Message:**\\n{message}\\n\\n"
                        f"**Commit:**\\n{sha}"
                    )
                },
                {
                    "type": 14,
                    "divider": True,
                    "spacing": 1
                },
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "style": 5,
                            "label": "Repository",
                            "emoji": "<:github:1488283491941748736>",
                            "disabled": False,
                            "url": repo_url
                        },
                        {
                            "type": 2,
                            "style": 5,
                            "label": "View Commit",
                            "emoji": "<:github:1488283491941748736>",
                            "disabled": False,
                            "url": commit_url
                        }
                    ]
                }
            ]
        }
    ]

    final_payload = {"components": payload}

    # Debug: print payload (safe)
    print("[DEBUG] Final payload JSON:")
    print(json.dumps(final_payload, indent=2))

    # Send webhook
    print("[DEBUG] Sending webhook...")
    response = requests.post(webhook, json=final_payload)

    # Debug: response status
    print(f"[DEBUG] Webhook response status: {response.status_code}")

    if not response.ok:
        print("[ERROR] Discord rejected the payload.")
        print(f"[ERROR] Response text: {response.text}")
        sys.exit(1)

    print("[SUCCESS] Webhook sent successfully.")

except Exception as e:
    print("[FATAL] An unexpected error occurred.")
    print(str(e))
    traceback.print_exc()
    sys.exit(1)
