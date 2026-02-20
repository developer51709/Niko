# utils/ai_local.py
import datetime
from ctransformers import AutoModelForCausalLM
from utils.memory import (
    get_user_memory,
    get_conversation_history,
    get_favorability,
    update_user_memory,
    adjust_favorability
)

# Load model once
MODEL_PATH = "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
llm = AutoModelForCausalLM.from_pretrained(
    ".",
    model_file=MODEL_PATH,
    model_type="llama",
    context_length=2500,
    threads=4,
    gpu_layers=0
)

def generate_reply_local(bot, user_id: int, message: str, username: str, SYSTEM_PROMPT: str):
    member_count = len(bot.users)
    server_name = bot.guilds[0].name if bot.guilds else "Server name unavailable"

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

    prompt = f"""<|system|>
{SYSTEM_PROMPT}

Server context:
- The current user is: {username}
- Your current impression: {fav_label}
- There are {member_count} members in this server.
- The server name is: {server_name}

Global context:
- It is currently {datetime.datetime.utcnow().strftime("%A, %B %d, %Y, %I:%M %p")} UTC

Recent Conversation:
{conv_history}
</s>
<|user|>
{message}
</s>
<|assistant|>
"""

    reply = llm(
        prompt,
        max_new_tokens=400,
        temperature=0.7,
        top_p=0.9,
        stop=["</s>", "<|user|>", "<|system|>", f"{username}:", "Niko:", "\n"]
    )

    clean = reply.strip()
    update_user_memory(user_id, message, role=username)
    update_user_memory(user_id, clean, role="Niko")
    adjust_favorability(user_id, delta=1)

    return clean