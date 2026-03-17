# Security Model

Hive scripts are designed to be invoked by AI agents. This document explains the guardrails that prevent unintended or destructive actions.

## Confirmation Gates

Write operations that affect external systems require a `--confirm` flag. Without it, the script prints a dry-run preview and exits with code 2.

```bash
# Dry run — shows what WOULD happen
python scripts/slack_handler.py send C123 "Hello"
# → DRY RUN: Send to C123: Hello. Re-run with --confirm to execute.

# Execute
python scripts/slack_handler.py send C123 "Hello" --confirm
```

### Protected Operations

| Handler | Protected Commands | What `--confirm` gates |
|---------|-------------------|----------------------|
| `binance_handler.py` | `spot-order`, `futures-order`, `cancel`, `futures-cancel` | All trades and cancellations |
| `gate_handler.py` | `spot-order`, `futures-order`, `cancel`, `futures-cancel`, `set-leverage`, `earn-lend`, `earn-redeem`, `dual-order` | All trades, leverage changes, earn operations |
| `slack_handler.py` | `send`, `reply`, `upload` | All outbound messages and file uploads |
| `whatsapp_handler.py` | `send`, `template`, `media` | All outbound messages |
| `gmail_handler.py` | `send`, `draft-send` | **Blocked entirely** — exits with error, no `--confirm` override |

### Read-only Operations (no confirmation needed)

- Price queries, balances, positions, order books
- Reading emails, threads, calendar events
- Searching files, listing documents
- Getting templates, checking status

## Domain Allowlist (Google Drive)

File sharing is restricted to allowed domains. Sharing outside the allowlist requires `--allow-external`:

```python
ALLOWED_DOMAINS = ["publica.la"]
```

## Gmail Send Block

Email sending is **permanently disabled** at the handler level. The AI can only create drafts — the user must review and send manually from Gmail.

```python
elif args.command in ("send", "draft-send"):
    sys.stderr.write("Error: 'send' is disabled for security.\n")
    sys.exit(1)
```

## Secret Detection

A pre-commit hook (`scripts/pre-commit-secrets.sh`) scans staged files for:

- API keys (Binance, Gate.io, OpenAI, GitHub, Slack, Supabase)
- OAuth tokens and refresh tokens
- Private keys (RSA, EC, DSA, OpenSSH)
- JWT patterns (`eyJ...`)

The hook blocks commits containing detected patterns. Only `.env.example` and the hook itself are allowlisted.

## Environment Variables

- All credentials live in `.env` (gitignored, never committed)
- Scripts load via `load_dotenv()` — no hardcoded secrets
- See [ENV_VARIABLES.md](ENV_VARIABLES.md) for the full key map

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (API failure, missing config, etc.) |
| 2 | Dry run — confirmation required |

## Recommendations for Operators

1. **API key permissions**: Configure exchange API keys as read-only if you only need portfolio queries
2. **Rotate keys regularly**: Especially after sharing access to the machine
3. **Review dry-runs**: Always read the preview before approving with `--confirm`
4. **Google OAuth scopes**: Use minimal scopes when generating refresh tokens
5. **Slack bot permissions**: Restrict the bot to specific channels if possible
