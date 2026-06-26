#!/bin/bash
if [ -n "${SIGRID_CI_TOKEN:-}" ] || [ -n "${SIGRID_TOKEN:-}" ]; then
  exit 0
else
  echo "Neither SIGRID_CI_TOKEN nor SIGRID_TOKEN is set. Ask the user to ensure it is set. Do not read or provide in-context." >&2
  exit 1
fi