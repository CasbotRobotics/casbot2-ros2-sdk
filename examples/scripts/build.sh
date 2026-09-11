#!/usr/bin/env bash
set -eo pipefail
casbot_sdk_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$casbot_sdk_root/examples/scripts/setup_env.sh"
cd "$casbot_sdk_root"
colcon build "$@"
