#!/usr/bin/env bash

#
# bootstrap in 'developer' mode and run tests.
#
# This is for manual start under linux
#

TEMP_PATH=/tmp/Bootstrap-Env-Test

set -ex

cd ../bootstrap_env

rm -Rf ${TEMP_PATH}
python3 boot_bootstrap_env.py boot_developer ${TEMP_PATH}

cd ${TEMP_PATH}/bin

set +x
source activate
set -ex

echo ${VIRTUAL_ENV}

./python3 bootstrap_env_admin.py install_test_requirements
./python3 bootstrap_env_admin.py pytest
