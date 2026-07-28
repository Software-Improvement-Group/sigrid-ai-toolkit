#!/bin/bash
SIGRIDCI_DIR="${TMPDIR:-/tmp}/sigridci"

if [ -f "$SIGRIDCI_DIR/sigridci/sigridci.py" ]; then
  echo "$SIGRIDCI_DIR"
  exit 0
fi

rm -rf "$SIGRIDCI_DIR"
if ! git clone --depth 1 https://github.com/Software-Improvement-Group/sigridci.git "$SIGRIDCI_DIR"; then
  echo "ERROR: Failed to clone sigridci repository." >&2
  exit 1
fi

if [ ! -f "$SIGRIDCI_DIR/sigridci/sigridci.py" ]; then
  echo "ERROR: Clone succeeded but sigridci.py not found at expected path." >&2
  exit 1
fi

echo "$SIGRIDCI_DIR"
