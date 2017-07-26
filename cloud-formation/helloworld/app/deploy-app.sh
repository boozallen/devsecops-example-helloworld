#!/usr/bin/env bash

IMAGE="$1"
REGISTRY_URL="$2"
AWS_REGION="$3"

if [ "${AWS_REGION}" == "" ]; then
        AWS_REGION="us-east-1"
fi

REGISTRY_URI=$(echo "${REGISTRY_URL}" | sed -e 's|^https://||g')
IMAGE_NAME="${REGISTRY_URI}/${IMAGE}"

SUCCESS=
echo "Login to ${REGISTRY_URL}"
LOGIN_COMMAND=$(/usr/local/bin/aws ecr get-login --region "${AWS_REGION}" | sed -e 's|-e none||g')
$LOGIN_COMMAND

echo "Pull ${IMAGE_NAME}"
if docker pull "${IMAGE_NAME}" ; then
    CONTAINER=$(docker ps -all | tail -n +2 | grep 'webserver$')
    if [ "${CONTAINER}" != "" ] ; then
        docker stop webserver
        docker rm webserver
    fi
    if docker run -d -p 80:8080 --name webserver "${IMAGE_NAME}" ; then
        SUCCESS="yes"
    else
        echo "Failed to run ${IMAGE_NAME} image" >&2
    fi
else
    echo "Failed to pull ${IMAGE_NAME} image" >&2
fi

echo "Logout from  ${REGISTRY_URL}"
docker logout "${REGISTRY_URL}"

if [ "${SUCCESS}" == "" ]; then
    exit 1
else
     echo "Successfully installed ${IMAGE_NAME}" >&2
fi
