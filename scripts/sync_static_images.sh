#!/usr/bin/env bash
# Copy repo static/images into the Invenio instance static tree (served at /static/images/…).
set -euo pipefail

base_dir="$(cd "$(dirname "$0")/.." && pwd)"
src="${base_dir}/static/images"
venv="${base_dir}/${UV_PROJECT_ENVIRONMENT:-.venv}"
dest="${venv}/var/instance/static/images"

if [ ! -d "${src}" ]; then
  exit 0
fi

if [ ! -d "${venv}" ]; then
  echo "sync_static_images: no ${venv}, skipping" >&2
  exit 0
fi

mkdir -p "${dest}"
shopt -s nullglob
files=("${src}"/*)
shopt -u nullglob

if [ ${#files[@]} -eq 0 ]; then
  exit 0
fi

for f in "${files[@]}"; do
  if [ -f "${f}" ]; then
    cp -f "${f}" "${dest}/"
  fi
done

echo "Synced ${src} -> ${dest}"
