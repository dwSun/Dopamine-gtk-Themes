#!/bin/bash

# Build all generated artifacts from source.
# Run this after cloning before running install.sh.

set -ueo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "== Building CSS..."
cd "$REPO_DIR"
./parse-sass.sh

echo "== Building GTK assets..."
cd "$REPO_DIR/src/gtk"
./make-assets.sh
./render-assets.sh

echo "== done!"
echo "You can now run ./install.sh"
