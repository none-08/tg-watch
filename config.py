import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MY_CHAT_ID = int(os.getenv("MY_CHAT_ID"))

# Parse source groups: supports integers (chat IDs) and strings (usernames)
SOURCE_GROUPS = []
for g in os.getenv("SOURCE_GROUPS", "").split(","):
    g = g.strip()
    if g.lstrip("-").isdigit():
        SOURCE_GROUPS.append(int(g))
    else:
        SOURCE_GROUPS.append(g)
