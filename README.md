# GPT_CMD

A command-line helper that interacts with ChatGPT via `undetected_chromedriver`.

Features:
- Interactive menu to choose options like headless mode and saving history
- View and clear conversation history from the menu
- Copy the last response or entire history to the clipboard
- Search messages in the current session
- Export history to a Markdown file
- Optional batch mode loading questions from a text file
- Send an image from the clipboard directly to ChatGPT
- Optionally forward every response to your phone via Telegram
- Optional headless mode via `--headless`.
- Save the session to a file with `--save-file`.

## Usage

```bash
pip install -r requirements.txt
python GPT_CMD.py
```

`pillow` is required for clipboard image support. `requests` is used to send
notifications via the Telegram bot.

### Telegram setup

To keep your bot token private, store it in an environment variable named
`TELEGRAM_TOKEN` or in a file called `.telegram_token` next to `GPT_CMD.py`.
The file is ignored by Git, so it won't be committed.

Login to ChatGPT in the browser when prompted. Questions are asked via the terminal.

Follow the prompts to configure the session. During execution use the menu to
ask questions, show or clear history, copy answers, search messages, export the
conversation or send an image from your clipboard. You can also provide a file
with predefined questions to run them automatically at startup.
If you enable Telegram notifications at startup, provide your chat ID and all
responses will be sent to your phone.
Use the menu to view history or exit. File paths may be entered with or without
quotes; the script cleans them automatically.

## Data Protection

- Runs Chrome in incognito mode to avoid persisting browsing data.
- Does not store login credentials or conversation history to disk.
- Only console output is generated for responses. You may optionally choose to
  save the conversation in a file.
- Optionally, you may specify `--save-file` to save your questions and responses to a text file.

## Security Policy

See [SECURITY.md](SECURITY.md) for guidelines on reporting vulnerabilities.
