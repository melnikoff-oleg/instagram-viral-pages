#!/bin/sh
# One-command preview: builds the pages, starts a local server on port 8787 and opens the browser.
# Usage: ./instagram-preview/serve.sh          -> opens me.html (our draft account)
#        ./instagram-preview/serve.sh index    -> opens index.html (the iamnotsrc capture)
cd "$(dirname "$0")" || exit 1
PORT=8787
PAGE="${1:-me}"
URL="http://localhost:$PORT/${PAGE%.html}.html"
python3 build.py || exit 1
if lsof -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "A server is already running on port $PORT. Opening $URL"
  open "$URL" 2>/dev/null
  exit 0
fi
( sleep 1; open "$URL" 2>/dev/null ) &
echo "Preview running at $URL  (Ctrl+C to stop)"
exec python3 -m http.server "$PORT" --bind 127.0.0.1
