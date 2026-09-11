#!/usr/bin/env bash
# Runs offline regression tests only. Robot workflows are explicit ros2 run commands.
set -eo pipefail
casbot_sdk_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$casbot_sdk_root/examples/scripts/setup_env.sh"
if [[ ! -f "${CASBOT_SDK_SETUP:-$casbot_sdk_root/install/setup.bash}" ]]; then
    printf 'Build the SDK first: bash examples/scripts/build.sh\n' >&2
    exit 1
fi
cd "$casbot_sdk_root"
colcon test --packages-select casbot2_py_tests --event-handlers console_direct+ "$@"
colcon test-result --verbose
