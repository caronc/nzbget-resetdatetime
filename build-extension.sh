#!/usr/bin/env bash
#
# Builds ResetDateTime the same way a GitHub release does:
# - build/ResetDateTime/ can be copied straight into NZBGet's scripts folder
# - build/resetdatetime-<version>-dist.zip (and .sha256) are for a release
#
set -euo pipefail

# Always work from the folder this script lives in
cd "$(dirname "$0")"

NAME=ResetDateTime
OUT="build/${NAME}"
VERSION=$(python3 -c "import json; print(json.load(open('manifest.json'))['version'])")
ZIP="resetdatetime-${VERSION}-dist.zip"

# Start fresh
rm -rf build
mkdir -p "${OUT}"

# Copy in everything the extension ships with, including its translations
cp -r ResetDateTime.py manifest.json README.md LICENSE CHANGELOG.md _locales "${OUT}/"

# Zip it up the same way the official extensions are
(cd build && zip -qr "${ZIP}" "${NAME}")

# Write a checksum so people can make sure their download isn't damaged
# (sha256sum on Linux, shasum on macOS)
(
    cd build
    if command -v sha256sum >/dev/null; then
        sha256sum "${ZIP}" > "${ZIP}.sha256"
    else
        shasum -a 256 "${ZIP}" > "${ZIP}.sha256"
    fi
)

echo "Folder:   ${OUT}"
echo "Zip:      build/${ZIP}"
echo "Checksum: build/${ZIP}.sha256"
