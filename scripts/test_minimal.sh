#!/usr/bin/env sh
python3 "$(dirname "$0")/../src/main.py" \
  --vfs "$(dirname "$0")/../fixtures/vfs_minimal.json"
