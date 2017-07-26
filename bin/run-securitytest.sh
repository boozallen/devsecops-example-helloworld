#!/usr/bin/env bash

MAVEN_ARGS="$@"

# https://hub.docker.com/_/maven/
MAVEN_IMAGE="maven:3.5.0-jdk-8-alpine"

function get_parent {
    local script_dir=$(dirname $1)
    if [ "${script_dir}" == "." ]; then echo ".."; else echo "${script_dir}/.."; fi

}

function get_absolute_path {
    pushd "$1" > /dev/null; pwd; popd > /dev/null 
}

function get_sonarqube_image_id {
    docker ps -all | awk -F" " ' /sonarqube/ {print $1;}' | tr -d '\n'
}

REPO_DIR=$(get_parent $0)
REPO_HOME=$(get_absolute_path "${REPO_DIR}")

SONAR_IMAGE_ID=$(get_sonarqube_image_id)
if [ "${SONAR_IMAGE_ID}" == "" ]; then
    echo "Starting sonarqube daemon ..."
    SONAR_IMAGE_ID=$(docker run -d --name sonarqube -p 9000:9000 -p 9092:9092 sonarqube)
fi
echo "======================================================================"
echo "     Sonar daemon is running as Docker image ${SONAR_IMAGE_ID}"
echo "     Once done with testing you can stop and remove daemon using:"
echo "           docker stop ${SONAR_IMAGE_ID}"
echo "           docker rm ${SONAR_IMAGE_ID}"
echo "======================================================================"

winpty docker run --name maven --rm --net=host\
    --volume "/${REPO_HOME}/webapp:/project" \
    "${MAVEN_IMAGE}" \
    sh -c "cd /project;  mvn ${MAVEN_ARGS} sonar:sonar"
