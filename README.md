# tg-watch

A Telegram message forwarder. Monitors groups for keywords and sends matching messages to a private chat via a bot.

## How it works

- Your **personal account** (userbot) reads messages from the source groups
- A **bot** sends matching messages to your private chat
- This keeps your personal account safe from spam restrictions

Messages are forwarded if they contain `hos` or `assign` (case-insensitive).

## Setup

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure `.env`

```
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=+998xxxxxxxxx
SOURCE_GROUPS=@group1,@group2
BOT_TOKEN=your_bot_token
MY_CHAT_ID=your_chat_id
```

- `API_ID` / `API_HASH` — from https://my.telegram.org
- `PHONE` — your Telegram phone number (with country code)
- `SOURCE_GROUPS` — comma-separated usernames or chat IDs
- `BOT_TOKEN` — from `@BotFather`
- `MY_CHAT_ID` — your personal chat ID (where the bot sends messages)

### 3. Log in (first time only)

```bash
python3 main.py --login
```

This asks for your phone code and 2FA password and creates an authorized `session.session` file. Run it once on a machine where you can type the code interactively.

### 4. Run

```bash
python3 main.py
```

A normal run never asks for a login code. It loads the saved `session.session` and starts monitoring. If the session is missing or revoked, it prints a message telling you to run `--login` and exits — it will **not** request a new code, which avoids `FloodWaitError` (Telegram bans repeated login-code requests for hours).

> Run the account from **one machine only**. Sharing the same account across two `session.session` files (e.g. your laptop and the server) makes Telegram invalidate the sessions, forcing you to log in again. To deploy on a server, log in once with `--login` there, or copy an authorized `session.session` over.

## Customizing keywords

Edit `KEYWORDS` in `main.py`:

```python
KEYWORDS = re.compile(r"hos|assign", re.IGNORECASE)
```

Add more terms separated by `|`.

## Deploying to a server

### systemd (Ubuntu)

`/etc/systemd/system/telephon.service`:

```ini
[Unit]
Description=Telegram Message Forwarder
After=network.target

[Service]
WorkingDirectory=/root/telephon
ExecStart=/root/telephon/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start (`--now` starts it immediately **and** enables auto-start on reboot):

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now telephon
```

> The service is named `telephon` and the repo lives at `/root/telephon` on the
> server. If you deploy elsewhere, adjust the service name, `WorkingDirectory`,
> and `ExecStart` accordingly.

### First-time login on the server

The session must be created interactively (you have to type the code). Do this
**once** on the server, then start the service:

```bash
source venv/bin/activate
python3 main.py --login     # type the login code + 2FA password
```

Run the account from **one machine only** — logging in from a second machine
invalidates the session and forces a new login.

### Updating from GitHub

Pull the latest code and restart the service:

```bash
cd /root/telephon
git pull
sudo systemctl restart telephon
```

Your `.env` and `*.session` files are gitignored, so `git pull` never touches
them. If `git pull` reports a conflict on a tracked file you edited on the
server, discard the local change with `git reset --hard origin/main` (this only
overwrites tracked files — credentials and sessions stay).

### Useful commands

```bash
systemctl status telephon          # check status
journalctl -u telephon -n 50 -f    # live logs (last 50 lines, then follow)
sudo systemctl restart telephon    # restart
sudo journalctl --vacuum-time=1s   # clear all logs
```

## Files

- `main.py` — bot logic
- `config.py` — loads `.env` config
- `.env` — credentials (do not commit)
- `requirements.txt` — Python dependencies
- `session.session` — userbot login state (auto-generated)
- `bot_session.session` — bot login state (auto-generated)
