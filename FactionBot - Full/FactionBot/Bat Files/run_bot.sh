#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# FactionBot - Linux/macOS launcher
#
# Activates the local .venv (creating it if missing) and starts the bot.
# Reads the token from .env or tokens.txt automatically (handled in Bot.py).
# ---------------------------------------------------------------------------
set -euo pipefail

# Resolve the project root (one level up from this script's directory).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_DIR"

PYTHON_EXE="$PROJECT_DIR/.venv/bin/python"
RUNBOTS_FILE="$PROJECT_DIR/PythonFiles/RunBots.py"
BOT_FILE="$PROJECT_DIR/PythonFiles/Bot.py"

# Auto-create + populate the venv if it is missing so first-time runs work
# without manual setup.
if [ ! -x "$PYTHON_EXE" ]; then
    echo "Virtual environment not found. Creating it now..."
    python3 -m venv "$PROJECT_DIR/.venv"
    "$PYTHON_EXE" -m pip install --upgrade pip
    "$PYTHON_EXE" -m pip install -r "$PROJECT_DIR/requirements.txt"
fi

if [ ! -f "$BOT_FILE" ]; then
    echo "Bot file not found: $BOT_FILE"
    exit 1
fi

# Multi-bot mode: when ANY bot tokens (ModBot_Token / TicketBot_Token /
# UtilityBot_Token / FunBot_Token / ...) are configured in tokens.txt / .env,
# start every bot through the RunBots supervisor. Otherwise the classic
# single bot runs.
any_bot_tokens() {
    grep -hE '^[A-Za-z0-9]+Bot_Token=' \
        "$PROJECT_DIR/tokens.txt" "$PROJECT_DIR/.env" 2>/dev/null \
        | grep -v 'BOT_TOKEN_HERE' | grep -qE '=[^[:space:]]'
}
if [ -f "$RUNBOTS_FILE" ] && any_bot_tokens; then
    echo "Bot tokens found - starting all bots via RunBots..."
    exec "$PYTHON_EXE" "$RUNBOTS_FILE"
fi

echo "Starting FactionBot locally..."
exec "$PYTHON_EXE" "$BOT_FILE"
