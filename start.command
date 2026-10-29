#!/bin/bash
# Double-click this file to start Viral Page Studio (macOS).
cd "$(dirname "$0")" || exit 1
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
PORT="${PORT:-8788}"

fail() {
  echo "$1"
  read -r -p "Press return to close."
  exit 1
}

command -v python3 >/dev/null 2>&1 ||
  fail "Python 3 is not installed. Get it from python.org, then double-click this again."

command -v claude >/dev/null 2>&1 ||
  fail "Claude Code is not installed. Run:  curl -fsSL https://claude.ai/install.sh | bash   then sign in with: claude"

python3 -c "import PIL" 2>/dev/null || pip3 install --quiet pillow

exec python3 studio/serve.py --port "$PORT"
