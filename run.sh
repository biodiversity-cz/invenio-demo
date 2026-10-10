#!/usr/bin/env bash
#
# This script sets up a Python virtual environment, installs necessary packages,
# runs tests and other tasks for libraries which are part of the OARepo Invenio RDM
# flavour.
# 
# Usage: ./run.sh --help
#
#
# (C) 2025 CESNET, z.s.p.o.
# OARepo is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
#
set -euo pipefail

base_dir="$(cd "$(dirname "$0")" && pwd)"

if [ ! -f "${base_dir}/.runner.sh" ]; then
  echo "Downloading .runner.sh from oarepo repository..." >&2
  curl -o "${base_dir}/.runner.sh" https://raw.githubusercontent.com/oarepo/oarepo/main/tools/repository_runner.sh
  chmod +x "${base_dir}/.runner.sh"
fi

sync_static_images() {
  if [ -x "${base_dir}/scripts/sync_static_images.sh" ]; then
    "${base_dir}/scripts/sync_static_images.sh"
  fi
}

cmd="${1:-}"

case "${cmd}" in
  python)
    if [[ ! -x "${base_dir}/.venv/bin/python" ]]; then
      echo "Virtual environment not found at ${base_dir}/.venv. Run ./run.sh install first." >&2
      exit 1
    fi
    cd "${base_dir}"
    exec "${base_dir}/.venv/bin/python" "${@:2}"
    ;;
  install|upgrade)
    "${base_dir}/.runner.sh" "$@"
    sync_static_images
    ;;
  run)
    sync_static_images
    "${base_dir}/.runner.sh" "$@"
    ;;
  *)
    "${base_dir}/.runner.sh" "$@"
    ;;
esac
