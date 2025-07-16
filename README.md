# GPT_CMD

A command-line helper that interacts with ChatGPT via `undetected_chromedriver`.

## Usage

```bash
pip install -r requirements.txt
python GPT_CMD.py
```

Login to ChatGPT in the browser when prompted. Questions are asked via the terminal.

## Data Protection

- Runs Chrome in incognito mode to avoid persisting browsing data.
- Does not store login credentials or conversation history to disk.
- Only console output is generated for responses.

## Security Policy

See [SECURITY.md](SECURITY.md) for guidelines on reporting vulnerabilities.
