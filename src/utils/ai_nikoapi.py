# this is similar to the openai version but uses the nikoapi instead
import requests
import os
import datetime
from utils.memory import (
    get_user_memory,
    get_conversation_history,
    get_favorability,
    update_user_memory,
    adjust_favorability
)

# The API dashboard can be found at:
# https://nikoapi.lovable.app

BASE_URL = "https://ofkulvdrcwpsebewszsz.supabase.co/functions/v1"

_FALLBACK_REPLIES = [
    "sorry, my mind went blank for a sec ☕ try again in a moment~",
    "hmm, i seem to be a little out of it right now... give me a moment ☕",
    "i didn't quite catch that — my thoughts are a bit fuzzy today 🌿 try again shortly!",
]
_fallback_idx = 0

headers = {
    "Content-Type": "application/json",
    "x-api-key": os.environ.get("NIKOAPI_KEY")
}

def generate_reply_nikoapi(bot, user_id: int, server, message: str, username: str, SYSTEM_PROMPT: str):
    member_count = len(bot.users)
    server_name = server.name

    user_mem = get_user_memory(user_id)
    conv_history = get_conversation_history(user_id)
    favor = get_favorability(user_id)

    if favor > 15:
        fav_label = f"{username} is one of your absolute favorites on this server."
    elif favor > 8:
        fav_label = f"You like {username} a lot and consider them top-tier."
    elif favor > 3:
        fav_label = f"You have a good impression of {username}."
    elif favor > 0:
        fav_label = f"You are warming up to {username}."
    else:
        fav_label = f"You don't know {username} very well yet."

    prompt = f"""
{SYSTEM_PROMPT}

User: {username}
Impression: {fav_label}
Server: {server_name}
Members: {member_count}
Time: {datetime.datetime.utcnow().strftime("%A, %B %d, %Y, %I:%M %p")} UTC

Recent conversation:
{conv_history}

User message:
{message}
"""

    global _fallback_idx
    try:
        data = {"messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]}
        response = requests.post(
            f"{BASE_URL}/api-chat",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        response = response.json()

    except Exception:
        reply = _FALLBACK_REPLIES[_fallback_idx % len(_FALLBACK_REPLIES)]
        _fallback_idx += 1
        return reply

    clean = response["choices"][0]["message"]["content"].strip()

    update_user_memory(user_id, message, role=username)
    update_user_memory(user_id, clean, role="Niko")
    adjust_favorability(user_id, delta=1)
    
    return clean