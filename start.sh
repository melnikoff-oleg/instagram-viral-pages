#!/bin/sh
# Start Viral Page Studio on any OS with Python 3:  ./start.sh   (PORT=8790 ./start.sh for another port)
cd "$(dirname "$0")" || exit 1
PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"; export PATH
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is not installed."; exit 1; }
command -v claude >/dev/null 2>&1 || echo "Warning: Claude Code (claude) is not on the PATH; the chat will not work until it is."
exec python3 studio/serve.py --port "${PORT:-8788}"
