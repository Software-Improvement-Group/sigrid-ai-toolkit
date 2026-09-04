import os
import sys

start = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
directory = os.path.abspath(start)

while True:
    if os.path.isfile(os.path.join(directory, "sigrid.yaml")) or os.path.isfile(
        os.path.join(directory, "sigrid.yml")
    ):
        print(directory)
        sys.exit(0)
    parent = os.path.dirname(directory)
    if parent == directory:
        break
    directory = parent

print("No sigrid.yaml or sigrid.yml found in any parent directory.", file=sys.stderr)
sys.exit(1)
