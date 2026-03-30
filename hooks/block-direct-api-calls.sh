#!/usr/bin/env bash
#
# PreToolUse hook — blocks direct curl/wget calls to the Sigrid REST API.
# Forces all data fetching through the Python scripts instead.
#
# Exit codes:
#   0 = allow the command
#   2 = block the command (stderr message shown to Claude as feedback)
#
# Receives JSON on stdin with shape:
#   { "tool_name": "Bash", "tool_input": { "command": "..." } }

set -euo pipefail

INPUT="$(cat)"
COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"

[ -z "$COMMAND" ] && exit 0

if echo "$COMMAND" | grep -qE '(curl|wget)[[:space:]].*sigrid-says\.com/rest'; then
  {
    echo "BLOCKED: Direct API calls to Sigrid are not allowed."
    echo "Use the Python script instead:"
    echo '  python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fetch-refactoring-candidates.py" <customer> <system> [--count N]'
  } >&2
  exit 2
fi

exit 0
