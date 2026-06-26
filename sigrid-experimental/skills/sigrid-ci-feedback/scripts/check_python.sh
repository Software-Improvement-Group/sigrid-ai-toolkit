#!/bin/bash
if command -v python3 &>/dev/null; then
  echo "python3"
  exit 0
elif command -v python &>/dev/null; then
  version=$(python -c 'import sys; print(sys.version_info[0])' 2>/dev/null)
  if [ "$version" = "3" ]; then
    echo "python"
    exit 0
  fi
fi
echo "ERROR: Python 3 is required but not found. Instruct the user to install Python 3.7 or higher." >&2
exit 1
