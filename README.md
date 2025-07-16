# GPT_CMD

A command-line helper that interacts with ChatGPT via `undetected_chromedriver`.

Features:
- Optional headless mode via `--headless`.
- View conversation history with the `historia` command.
- Save the session to a file with `--save-file`.

## Usage

```bash
pip install -r requirements.txt
python GPT_CMD.py [--headless] [--save-file chat.txt]
```

Login to ChatGPT in the browser when prompted. Questions are asked via the terminal.

While running, you can type `historia` to print the current conversation or `salir` to exit.

## Data Protection

- Runs Chrome in incognito mode to avoid persisting browsing data.
- Does not store login credentials or conversation history to disk.
- Only console output is generated for responses.
 - Optionally, you may specify `--save-file` to save your questions and responses to a text file.

## Security Policy

See [SECURITY.md](SECURITY.md) for guidelines on reporting vulnerabilities.
