#!/usr/bin/env bash
# Downloads the Mixkit stock footage used in the film (too large for git).
# All items are under the Mixkit Stock Video Free License (commercial use and ads allowed,
# attribution not required): https://mixkit.co/license/
# Music (music_src/543.mp3) and sound effects (sfx_src/*.wav) are already in the repo.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stock_src
for id in 42910 3806 101169 101172 101672 101179; do
  [ -s "stock_src/$id.mp4" ] && continue
  url=$(curl -s "https://mixkit.co/free-stock-video/download/$id/?context=sidebar&type=2160p" \
        | grep -oE 'data-download--modal-url-value="[^"]+"' | cut -d'"' -f2 || true)
  [ -z "$url" ] && url="https://assets.mixkit.co/videos/$id/$id-2160.mp4"
  echo "downloading $id"
  curl -sL "$url" -o "stock_src/$id.mp4"
  sleep 2
done
