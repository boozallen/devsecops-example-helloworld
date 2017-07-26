#!/usr/bin/env bash

set -e
set -x

JENKINS_DATA_HOME="/var/jenkins_home"
JENKINS_USER="ec2-user"
JENKINS_IMAGE="jenkins"

# https://store.docker.com/editions/community/docker-ce-server-centos?tab=description
echo "================ Installing docker ================"
yum install -y yum-utils > /dev/null
yum-config-manager --enable rhui-REGION-rhel-server-extras
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum makecache fast
yum install -y docker-ce

yum update -y

echo "================ Setup docker service ================"
chkconfig docker on
service docker start

echo "================ Run test container ================"
docker run hello-world 


echo "================ Setup jenkins user ================"
mkdir -p "${JENKINS_DATA_HOME}"
chown -R "${JENKINS_USER}:${JENKINS_USER}" "${JENKINS_DATA_HOME}"
usermod -a -G docker "${JENKINS_USER}"

echo "================ Get jenkins container ================"
docker pull "${JENKINS_IMAGE}"

echo "================ Setup jenkins service ================"
chkconfig jenkins on
service jenkins start