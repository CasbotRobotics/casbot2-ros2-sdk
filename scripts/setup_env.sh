#!/usr/bin/env bash
# Usage: source scripts/setup_env.sh
# The same environment loader is used for simulation and real robots.

casbot_setup_environment() {
    local sdk_root ros_setup sdk_setup
    sdk_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || return 1
    ros_setup="${CASBOT_ROS_SETUP:-/opt/ros/humble/setup.bash}"
    if [[ ! -f "$ros_setup" ]]; then
        printf 'ROS 2 setup not found: %s\n' "$ros_setup" >&2
        return 1
    fi
    source "$ros_setup" || return 1

    # Optional explicit runtime environment; do not silently select another robot workspace.
    if [[ -n "${CASBOT_RUNTIME_SETUP:-}" ]]; then
        if [[ ! -f "$CASBOT_RUNTIME_SETUP" ]]; then
            printf 'Runtime setup not found: %s\n' "$CASBOT_RUNTIME_SETUP" >&2
            return 1
        fi
        source "$CASBOT_RUNTIME_SETUP" || return 1
    fi

    sdk_setup="${CASBOT_SDK_SETUP:-$sdk_root/install/setup.bash}"
    if [[ -f "$sdk_setup" ]]; then
        source "$sdk_setup" || return 1
    fi
    # Leave ROS_DOMAIN_ID and ROS_LOCALHOST_ONLY under the operator's control.
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    printf 'Use: source scripts/setup_env.sh\n' >&2
    exit 1
fi
casbot_setup_environment
