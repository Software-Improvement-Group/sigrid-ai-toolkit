#!/bin/bash
if [ -n "${SIGRID_CI_TOKEN:-}" ] || [ -n "${SIGRID_TOKEN:-}" ]; then
  exit 0
else
  echo "Neither SIGRID_CI_TOKEN nor SIGRID_TOKEN is set. This is a shell env var the user exports themselves, separate from the MCP token in the keychain. Ask the user to 'export SIGRID_CI_TOKEN=<token>'. Do not read or provide the value in-context." >&2
  exit 1
fi