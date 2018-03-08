pipeline {
    agent any
    environment {
        kube_namespace = "${env.JOB_NAME}-${env.BUILD_ID}"
    }
    stages {
        stage('checkout') {
            steps {
                checkout scm
            }
        }
        stage('build images') {
            steps {
                withDockerRegistry([credentialsId: 'ecr:eu-central-1:jenkins-aws-credentials', url: 'https://514443763038.dkr.ecr.eu-central-1.amazonaws.com']) {
                    dir(path: 'kubernetes') {
                        sh './setup-kube.sh build'
                    }
                }
            }
        }
        stage('deploy app') {
            steps {
                dir(path: 'kubernetes') {
                    sh "./setup-kube.sh create -p \$(echo ${env.kube_namespace}|tr '/' '-')"
                }
            }
        }
        stage('tests') {
            steps {
                sleep 5
            }
        }
        stage('destroy deployment') {
            steps {
                dir(path: 'kubernetes') {
                    sh "./setup-kube.sh delete -p \$(echo ${env.kube_namespace}|tr '/' '-')"
                }
            }
        }
    }
}
