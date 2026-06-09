#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Run the bots
set -e

get_master_id() {
    local master_id_file='./master_id'
    until [[ -r "${master_id_file}" ]]; do
        sleep 1
    done
    cat "${master_id_file}"
}

main() {
    uv run ./master.py &
    local MASTER_ID
    MASTER_ID="$(get_master_id)"
    MASTER_ID="${MASTER_ID}" uv run ./slave.py
    # TODO: More workers, export
}

main
