import os
import shutil
import subprocess
import sys

sigridci_dir = os.path.join(os.environ["CLAUDE_PLUGIN_DATA"], "dependency-cache", "sigridci")
agents_py = os.path.join(sigridci_dir, "sigridci", "agents.py")

if os.path.isfile(agents_py):
    result = subprocess.run(
        ["git", "-C", sigridci_dir, "pull", "--ff-only", "--quiet"]
    )
    if result.returncode == 0:
        print(sigridci_dir)
        sys.exit(0)
    print("WARNING: Failed to update cached sigridci clone; re-cloning.", file=sys.stderr)
    shutil.rmtree(sigridci_dir)

os.makedirs(os.path.dirname(sigridci_dir), exist_ok=True)
result = subprocess.run(
    [
        "git",
        "clone",
        "--depth",
        "1",
        "https://github.com/Software-Improvement-Group/sigridci.git",
        sigridci_dir,
    ]
)
if result.returncode != 0:
    print("ERROR: Failed to clone sigridci repository.", file=sys.stderr)
    sys.exit(1)

if not os.path.isfile(agents_py):
    print("ERROR: Clone succeeded but agents.py not found at expected path.", file=sys.stderr)
    sys.exit(1)

print(sigridci_dir)
