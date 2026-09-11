#!/usr/bin/env bash
# Launch the team's supplied simulator command without embedding a guessed binary/image.
set -eo pipefail
if [[ $# -eq 0 || "$1" == '--help' ]]; then
    printf 'Usage: examples/scripts/start_sim.sh COMMAND [ARG ...]\n'
    printf 'Use the MuJoCo/Docker launch command supplied with your simulator release.\n'
    printf 'Set ROS_DOMAIN_ID and ROS_LOCALHOST_ONLY in the invoking shell.\n'
    if [[ $# -eq 0 ]]; then exit 2; fi
    exit 0
fi
casbot_sdk_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$casbot_sdk_root/examples/scripts/setup_env.sh"
exec "$@"
