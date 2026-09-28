#!/bin/bash
# MyFlat Viewer launcher (macOS). Double-click in Finder, or run:  bash start.command
cd "$(dirname "$0")" || exit 1
PORT=${PORT:-8080}

# Use Blender's bundled Python first (always present if Blender is installed),
# then the system python3.
PY=$(ls /Applications/Blender.app/Contents/Resources/*/python/bin/python3* 2>/dev/null | head -1)
if [ -z "$PY" ] && command -v python3 >/dev/null 2>&1; then PY=python3; fi
if [ -z "$PY" ]; then
  echo "Python 3 not found. Install Blender or Python 3, then run this again."; read -r; exit 1
fi

while lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; do PORT=$((PORT+1)); done
URL="http://localhost:$PORT/"
echo "MyFlat Viewer running at $URL"
echo "Keep this window open while you use the viewer. Press Ctrl+C to stop."
echo "Phones / tablets on the same Wi-Fi can use the address printed below."
(sleep 1; open "$URL") &
exec "$PY" scripts/serve.py "$PORT" --lan
