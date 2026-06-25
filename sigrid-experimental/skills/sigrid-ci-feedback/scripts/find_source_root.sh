#!/bin/bash
# Searches upward from a given directory (or pwd) for sigrid.yaml or sigrid.yml.
# Usage: find_source_root.sh [starting-directory]
# Prints the directory containing the scope file, or exits 1 if not found.
dir="${1:-$(pwd)}"
while [ "$dir" != "/" ]; do
  if [ -f "$dir/sigrid.yaml" ] || [ -f "$dir/sigrid.yml" ]; then
    echo "$dir"
    exit 0
  fi
  dir="$(dirname "$dir")"
done
echo "No sigrid.yaml or sigrid.yml found in any parent directory." >&2
exit 1
