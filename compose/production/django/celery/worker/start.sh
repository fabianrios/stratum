#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


celery -A stratum.taskapp worker -l INFO
