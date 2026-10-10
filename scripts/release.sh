#!/usr/bin/env bash
#
# First deployment on an empty NRP test environment.
# CESNET runs this when the test instance is created from scratch:
# https://nrp-cz.github.io/docs/deploy/deployment
#
# INVENIO_S3_BUCKET comes from the deployment environment. This script does
# not create an admin user and does not contain passwords.

set -exo pipefail

cd "$(dirname "$0")/.."

if [ -d .venv ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

if [ -z "${INVENIO_S3_BUCKET:-}" ]; then
  echo "INVENIO_S3_BUCKET is not set" >&2
  exit 1
fi

if [ -z "${KUBERNETES_SERVICE_HOST:-}" ]; then
  ./run.sh cli services setup
else
  ./run.sh cli services setup --no-services --no-demo-data
fi

invenio files location create --default s3 "s3://${INVENIO_S3_BUCKET}"

invenio roles create administration
invenio access allow administration-access role administration
invenio access allow administration-moderation role administration
