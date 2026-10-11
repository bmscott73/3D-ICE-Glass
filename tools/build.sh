#!/usr/bin/env bash
# Build in a separate tree; vendor/ stays identical to the pinned EPFL snapshot.
set -euo pipefail
release_root=$(cd "$(dirname "$0")/.." && pwd)
release_build="$release_root/build/3d-ice"
if [ "$(uname -s)" != Linux ]; then
  echo 'Use Linux or the supplied Dockerfile for the GCC/OpenMP build.' >&2
  exit 1
fi
if [ -e "$release_build" ]; then
  echo "Build tree already exists: $release_build. Rebuild there, or rename it before a clean build." >&2
  exit 1
fi
mkdir -p "$release_root/build"
cp -R "$release_root/vendor/3d-ice" "$release_build"
cd "$release_build"
bash install-superlumt.sh > ../superlu-build.log 2>&1
make > ../3d-ice-build.log 2>&1
for release_binary in 3D-ICE-Emulator 3D-ICE-Server 3D-ICE-Client; do
  test -x "bin/$release_binary"
done
echo "Built $release_build/bin/3D-ICE-Emulator"
