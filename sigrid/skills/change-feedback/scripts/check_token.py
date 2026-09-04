import os
import sys

token = os.environ.get("SIGRID_CI_TOKEN") or os.environ.get("SIGRID_TOKEN")

if token:
    print(f"Token set, length {len(token)}. This is the only diagnostic available or needed "
          "— do not inspect the variable further (no env/printenv/echo of the value).")
    sys.exit(0)

print(
    "Neither SIGRID_CI_TOKEN nor SIGRID_TOKEN is set. This is a shell env var the "
    "user exports themselves, separate from the MCP token in the keychain. Ask the "
    "user to 'export SIGRID_CI_TOKEN=<token>'. Do not read or provide the value "
    "in-context.",
    file=sys.stderr,
)
sys.exit(1)
