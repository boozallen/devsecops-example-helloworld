#!/usr/bin/env bash

### BEGIN INIT INFO
# Provides:          <NAME>
# Required-Start:    $local_fs $network $named $time $syslog
# Required-Stop:     $local_fs $network $named $time $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Description:       <DESCRIPTION>
### END INIT INFO

JENKINS_DATA_HOME="/var/jenkins_home"
JENKINS_USER="ec2-user"
JENKINS_IMAGE="jenkins"
JENKINS_USER_ID=$(id -u ${JENKINS_USER})
JENKINS_PORT="8080"

DOCKER_COMMAND=$(which docker)
DOCKER_GROUP=$(stat -c %g /var/run/docker.sock)
LIBLTDL_PATH=$(whereis libltdl.so.7 | sed -e 's|.*: ||g')
DOCKER_JENKINS_IMAGE="jenkins"

PID_FILE="/var/run/jenkins.docker-id"

function get_id {
    if [ -f "${PID_FILE}" ]; then
        echo $(cat "${PID_FILE}")
    else
        echo "0"
    fi
}
function is_running {
    local id=$(get_id)
    local image=$(docker ps --filter id=${id} | tail -n +2 | grep "${DOCKER_JENKINS_IMAGE}")
    [ "${image}" != "" ];
}

function start {
    if is_running ; then
        echo 'Jenkins is already running'
    else
        docker run \
            --detach \
            --publish 80:"${JENKINS_PORT}" \
            --publish 50000:50000 \
            --volume "${JENKINS_DATA_HOME}:/var/jenkins_home" \
            --volume /var/run/docker.sock:/var/run/docker.sock \
            --volume "${DOCKER_COMMAND}:/usr/bin/docker" \
            --volume "${LIBLTDL_PATH}:/usr/lib/libltdl.so.7" \
            --user "${JENKINS_USER_ID}" \
            "--group-add=${DOCKER_GROUP}" \
            "${JENKINS_IMAGE}" \
            > "${PID_FILE}"
        echo 'Jenkins has been started' >&2
        docker run --detach --name sonarqube --publish 9000:9000 --publish 9092:9092 sonarqube
        echo 'SonarQube has been started' >&2
    fi
}

function status {
    if is_running ; then
        echo 'Jenkins is running' >&2
    else
        echo 'Jenkins is stopped' >&2
        return 1
    fi
}

function stop {
    local id
    if is_running; then
        id=$(get_id)
        echo 'Stopping service…' >&2
        if docker stop "${id}" ; then
            echo 'Jenkins has been stopped' >&2
            echo "0" > "${PID_FILE}"
        else
            echo 'Failed to stop jenkins' >&2
        fi
    else
        echo 'Jenkins is not running' >&2
        return 1
    fi
}

case "$1" in
    status)      status ;;
    start)       start ;;
    stop)        stop ;;
    restart)     stop; start ;;
    *)           echo "Usage: $0 {start|status|stop|restart}" >&2
esac

