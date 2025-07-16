# GPT_CMD

A command-line helper that interacts with ChatGPT via `undetected_chromedriver`.

Features:
- Interactive menu to choose options like headless mode and saving history
- View and clear conversation history from the menu
- Copy the last response to the clipboard

## Usage

```bash
pip install -r requirements.txt
python GPT_CMD.py
```

Login to ChatGPT in the browser when prompted. Questions are asked via the terminal.

Follow the prompts to configure the session. During execution use the menu to
ask questions, show or clear history, copy the last answer, or exit the tool.

## Data Protection

- Runs Chrome in incognito mode to avoid persisting browsing data.
- Does not store login credentials or conversation history to disk.
- Only console output is generated for responses. You may optionally choose to
  save the conversation in a file.

## Security Policy

See [SECURITY.md](SECURITY.md) for guidelines on reporting vulnerabilities.
