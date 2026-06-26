import re
import sys
import asyncio
from telethon import TelegramClient, events, Button
from config import API_ID, API_HASH, PHONE, BOT_TOKEN, MY_CHAT_ID, SOURCE_GROUPS

WHOLE_WORD_KEYWORDS = ["hos", "mg need", "mg needed", "need mg", "mg avail", "mg kere", "mg bormi", "mg service"]
SUBSTRING_KEYWORDS = ["assign"]

_patterns = []
for k in WHOLE_WORD_KEYWORDS:
    _patterns.append(rf"\b{re.escape(k)}\b")
for k in SUBSTRING_KEYWORDS:
    _patterns.append(re.escape(k))

KEYWORDS = re.compile("|".join(_patterns), re.IGNORECASE)

# Userbot — monitors groups
user_client = TelegramClient("session", API_ID, API_HASH)

# Bot — sends messages (no spam risk to personal account)
bot_client = TelegramClient("bot_session", API_ID, API_HASH)


async def build_message_link(event):
    chat = await event.get_chat()
    msg_id = event.id

    if hasattr(chat, "username") and chat.username:
        return f"https://t.me/{chat.username}/{msg_id}"

    chat_id = str(chat.id)
    if chat_id.startswith("-100"):
        chat_id = chat_id[4:]
    return f"https://t.me/c/{chat_id}/{msg_id}"


async def build_sender_info(event):
    """Return a markdown line identifying the sender, with a link that
    opens a private chat even after the original message is deleted."""
    sender = await event.get_sender()
    if sender is None:
        return "**From user:** unknown"

    name = " ".join(
        part for part in (getattr(sender, "first_name", None),
                          getattr(sender, "last_name", None)) if part
    ) or getattr(sender, "title", None) or "Unknown"

    username = getattr(sender, "username", None)
    if username:
        # @username links resolve in any client and survive message deletion.
        link = f"https://t.me/{username}"
    else:
        # No username: tg://user?id= opens the private chat by numeric ID.
        link = f"tg://user?id={sender.id}"

    return f"**From user:** [{name}]({link})"


@user_client.on(events.NewMessage(chats=SOURCE_GROUPS))
async def handler(event):
    if not event.text:
        return

    if not KEYWORDS.search(event.text):
        return

    chat = await event.get_chat()
    chat_name = getattr(chat, "title", "Unknown")
    link = await build_message_link(event)
    sender_info = await build_sender_info(event)

    message = (
        f"**From: {chat_name}**\n"
        f"{sender_info}\n\n"
        f"{event.text}"
    )

    await asyncio.sleep(2)
    await bot_client.send_message(
        MY_CHAT_ID,
        message,
        link_preview=False,
        buttons=Button.url("➡️ Go to message", link),
    )

    print(f"Sent message {event.id} from {chat_name}")


async def main():
    await bot_client.start(bot_token=BOT_TOKEN)

    # Connect without triggering a login. If the saved session is dead, exit
    # with a clear message instead of firing SendCodeRequest — repeated code
    # requests get the phone number flood-banned for hours.
    await user_client.connect()
    if not await user_client.is_user_authorized():
        print(
            "Userbot session is not authorized.\n"
            "Run this manually and log in interactively to create a valid session:\n"
            "    python3 main.py --login\n"
            "Do NOT keep relaunching — repeated login attempts cause a FloodWaitError."
        )
        await user_client.disconnect()
        await bot_client.disconnect()
        return

    all_keywords = WHOLE_WORD_KEYWORDS + SUBSTRING_KEYWORDS
    print(f"Monitoring {len(SOURCE_GROUPS)} groups for keywords: {', '.join(all_keywords)}")
    print("Press Ctrl+C to stop.")
    await user_client.run_until_disconnected()


async def login():
    """Interactive login — run on a machine where you can type the code."""
    await user_client.start(phone=PHONE)
    print("Login successful. session.session is now authorized.")
    await user_client.disconnect()


if "--login" in sys.argv:
    asyncio.run(login())
else:
    asyncio.run(main())
