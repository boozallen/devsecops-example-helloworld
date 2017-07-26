#!/usr/bin/env bash

WEBSITE_URL="$1"

if [ "${WEBSITE_URL}" == "" ]; then
    WEBSITE_URL="http:\/52.72.139.105"
fi


PYTHON_IMAGE="killercentury/python-phantomjs"

function get_parent {
    local script_dir=$(dirname $1)
    if [ "${script_dir}" == "." ]; then echo "..";  else echo "${script_dir}/.."; fi
}

function get_absolute_path {
    pushd "$1" > /dev/null; pwd; popd > /dev/null 
}

REPO_DIR=$(get_parent $0)
REPO_HOME=$(get_absolute_path "${REPO_DIR}")

WORKSPACE="\/project\/src\/test"
RESULTS_DIR="\/project\/target\/browser-test-results"

ARGS=()
ARGS+=("--base-url=${WEBSITE_URL}")
ARGS+=("--webdriver-class=PhantomJS")
ARGS+=("--reuse-driver")
ARGS+=("--default-wait=10")
ARGS+=("--verbose")
ARGS+=("--default-window-width=800")
ARGS+=("--results-file=${RESULTS_DIR}/results.csv")
ARGS+=("--test-reports-dir=${RESULTS_DIR}")

CMD="export PYTHONPATH=${WORKSPACE}\/resources\/lib\/python2.6\/site-packages:${WORKSPACE}\/python"
CMD="${CMD};mkdir -p ${RESULTS_DIR}"
CMD="${CMD};python -B -u ${WORKSPACE}/python/helloworld/test_suite.py ${ARGS[@]}"

winpty docker run --name browser-test --rm --volume "/${REPO_HOME}/webapp:/project" \
    "${PYTHON_IMAGE}" sh -c "${CMD}"


