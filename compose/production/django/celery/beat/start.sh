#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


celery -A stratum.taskapp beat -l INFO
