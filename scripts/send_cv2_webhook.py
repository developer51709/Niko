import json
import requests
import sys

webhook = sys.argv[1]
author = sys.argv[2]
message = sys.argv[3]
sha = sys.argv[4]
repo_url = sys.argv[5]
commit_url = sys.argv[6]

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
                "content": f"**Author:**\n{author}\n\n**Message:**\n{message}\n\n**Commit:**\n{sha}"
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
                        "emoji": None,
                        "disabled": False,
                        "url": repo_url
                    },
                    {
                        "type": 2,
                        "style": 5,
                        "label": "View Commit",
                        "emoji": None,
                        "disabled": False,
                        "url": commit_url
                    }
                ]
            }
        ]
    }
]

requests.post(webhook, json={"components": payload})