#!/usr/bin/env bash
# SPDX-License-Identifier: 0BSD
# Run the bots
set -e

main() {
  uv run ./master.py &
  local master_id_file='./master_id'
  until [[ -r "${master_id_file}" ]]; do
    sleep 1
  done
  local MASTER_ID
  MASTER_ID="$(cat ${master_id_file})"
  MASTER_ID="${MASTER_ID}" uv run ./slave.py
  # TODO: More workers, export
}

main
