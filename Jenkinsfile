#!groovy

import groovy.json.JsonSlurper
import java.net.URL

pipeline {
    agent none
    options {
        timeout(time: 1, unit: 'DAYS')
        disableConcurrentBuilds()
    }
    stages {
        stage("Init") {
            agent any
            steps { initialize() }
        }
        stage("Build App") {
            agent any 
            steps { buildApp() }
        }
        stage("Run App Security Scan") {
            agent any 
            steps {  runSecurityTest() }
        }
        stage("Build and Register Image") {
            agent any
            steps { buildAndRegisterDockerImage() }
        }
        stage("Deploy Image to Dev") {
            agent any
            steps { deployImage(env.ENVIRONMENT) }
        }
        stage("Test App in Dev") {
            agent any
            steps { runBrowserTest(env.ENVIRONMENT) }
        }
        stage("Deploy Image to Test") {
            agent any
            when { branch 'master' } 
            steps { deployImage('test') }
        }
        stage("Test App in Test") {
            agent any
            when { branch 'master' } 
            steps { runBrowserTest('test') }
        }
        stage("Proceed to prod?") {
            agent none
            when { branch 'master' } 
            steps { proceedTo('prod') }
        }
        stage("Deploy Image to Prod") {
            agent any
            when { branch 'master' }
            steps { deployImage('prod') }
        }
    }
}


// ================================================================================================
// Initialization steps
// ================================================================================================

def initialize() {
    env.SYSTEM_NAME = "DSO"
    env.AWS_REGION = "us-east-1"
    env.REGISTRY_URL = "https://912661153448.dkr.ecr.us-east-1.amazonaws.com"
    env.MAX_ENVIRONMENTNAME_LENGTH = 32
    setEnvironment()
    env.IMAGE_NAME = "hello-world:" + 
        ((env.BRANCH_NAME == "master") ? "" : "${env.ENVIRONMENT}-") + 
        env.BUILD_ID
    showEnvironmentVariables()
}

def setEnvironment() {
    def branchName = env.BRANCH_NAME.toLowerCase()
    def environment = 'dev'
    echo "branchName = ${branchName}"
    if (branchName == "") {
        showEnvironmentVariables()
        throw "BRANCH_NAME is not an environment variable or is empty"
    } else if (branchName != "master") {
        //echo "split"
        if (branchName.contains("/")) {
            // ignore branch type
            branchName = branchName.split("/")[1]
        }
        //echo "remove '-' characters'"
        branchName = branchName.replace("-", "")
        //echo "remove JIRA project name"
        if (env.JIRA_PROJECT_NAME) {
            branchName = branchName.replace(env.JIRA_PROJECT_NAME, "")
        }
        // echo "limit length"
        branchName = branchName.take(env.MAX_ENVIRONMENTNAME_LENGTH as Integer)
        environment += "-" + branchName
    }
    echo "Using environment: ${environment}"
    env.ENVIRONMENT = environment
}

def showEnvironmentVariables() {
    sh 'env | sort > env.txt'
    sh 'cat env.txt'
}

// ================================================================================================
// Build steps
// ================================================================================================

def buildApp() {
     dir("webapp") {
        withDockerContainer("maven:3.5.0-jdk-8-alpine") { sh "mvn clean install"}
        archiveArtifacts '**/target/spring-boot-web-jsp-1.0.war'
        step([$class: 'JUnitResultArchiver', testResults: '**/target/surefire-reports/TEST-*.xml'] )
     }
}

def buildAndRegisterDockerImage() {
    def buildResult
    docker.withRegistry(env.REGISTRY_URL) {
        echo "Connect to registry at ${env.REGISTRY_URL}"
        dockerRegistryLogin()
        echo "Build ${env.IMAGE_NAME}"
        buildResult = docker.build(env.IMAGE_NAME)
        echo "Register ${env.IMAGE_NAME} at ${env.REGISTRY_URL}"
        buildResult.push()
        echo "Disconnect from registry at ${env.REGISTRY_URL}"
        sh "docker logout ${env.REGISTRY_URL}"
    }
}

def dockerRegistryLogin() {
    def login_command = ""
    withDockerContainer("garland/aws-cli-docker") {
        login_command = sh(returnStdout: true,
            script: "aws ecr get-login --region ${AWS_REGION} | sed -e 's|-e none||g'"
        )
    }
    sh "${login_command}"
}

// ================================================================================================
// Deploy steps
// ================================================================================================

def deployImage(environment) {
    def context = getContext(environment)
    def ip = findIp(environment)
    echo "Deploy ${env.IMAGE_NAME} to '${environment}' environment (in context: ${context})"
    sshagent (credentials: ["${env.SYSTEM_NAME}-${context}-helloworld"]) {
        sh """ssh -o StrictHostKeyChecking=no -tt \"ec2-user@${ip}\" \
            sudo /opt/dso/deploy-app  \"${env.IMAGE_NAME}\" \"${env.REGISTRY_URL}\"
"""
    }
    echo "Ensure site is up"
     // TODO: Replace with wait loop that tests if the siste is responsive
    sleep time: 10, unit: 'SECONDS'
}

def getContext(environment) {
    return (env.BRANCH_NAME == 'master') ? environment : 'dev'
}


// ================================================================================================
// Test steps
// ================================================================================================

def runSecurityTest() {
    def sonarReportDir = "target/sonar"
    def jenkinsIP = findJenkinsIp()
    dir("webapp") {
        withDockerContainer("maven:3.5.0-jdk-8-alpine")  {
            sh "mvn sonar:sonar -Dsonar.host.url=http://${jenkinsIP}:9000"
        }
        sh "ls -al ${sonarReportDir}"
        //archiveArtifacts "**/${sonarReportDir}/*.txt"
     }
}

def runBrowserTest(environment) {
    def ip = findIp(environment)
    def workDir = "src/test"
    def testsDir="${workDir}/python"
    def resultsDir = "target/browser-test-results/${environment}"
    def resultsPrefix = "${resultsDir}/results-${env.BUILD_ID}"
    def sitePackagesDir="${workDir}/resources/lib/python2.6/site-packages"
    def script = """
        export PYTHONPATH="${sitePackagesDir}:${testsDir}"
        mkdir -p ${resultsDir}
        /usr/bin/python -B -u ./${testsDir}/helloworld/test_suite.py \
            "--base-url=http://${ip}" \
            --webdriver-class=PhantomJS\
            --reuse-driver \
            --environment ${environment} \
            --default-wait=15 \
            --verbose \
            --default-window-width=800 \
            --test-reports-dir=${resultsDir} \
            --results-file=${resultsPrefix}.csv
"""
    dir("webapp") {
        withDockerContainer("killercentury/python-phantomjs") { sh "${script}" }
        step([$class: 'JUnitResultArchiver', testResults: "**/${resultsDir}/TEST-*.xml"])
        sh "ls -lhr ${resultsDir}"
        archiveArtifacts "**/${resultsPrefix}.*"
    }
}

// ================================================================================================
// Utility steps
// ================================================================================================

def proceedTo(environment) {
    def description = "Choose 'yes' if you want to deploy to this build to " + 
        "the ${environment} environment"
    def proceed = 'no'
    timeout(time: 4, unit: 'HOURS') {
        proceed = input message: "Do you want to deploy the changes to ${environment}?",
            parameters: [choice(name: "Deploy to ${environment}", choices: "no\nyes",
                description: description)]
        if (proceed == 'no') {
            error("User stopped pipeline execution")
        }
    }
}

def findIp(environment) {
    def ip = ""
    withDockerContainer("garland/aws-cli-docker") {
       ip = sh(returnStdout: true,
            script: """aws ec2 describe-instances \
                --filters "Name=instance-state-name,Values=running" \
                "Name=tag:Name,Values=${env.SYSTEM_NAME}-${environment}-helloworld" \
                --query "Reservations[].Instances[].{Ip:PrivateIpAddress}" \
                --output text --region ${env.AWS_REGION} | tr -d '\n'
"""
        )
    }
    echo "ip=[${ip}]"
    return ip
}

def findJenkinsIp() {
    def ip = ""
    withDockerContainer("garland/aws-cli-docker") {
       ip = sh(returnStdout: true,
            script: """aws ec2 describe-instances \
                --filters "Name=instance-state-name,Values=running" \
                "Name=tag:Name,Values=${env.SYSTEM_NAME}-shared-jenkins" \
                --query "Reservations[].Instances[].{Ip:PrivateIpAddress}" \
                --output text --region ${env.AWS_REGION} | tr -d '\n'
"""
        )
    }
    echo "ip=[${ip}]"
    return ip
}

// def startSonarQube() {
//     if (!isSonarQubeRunning()) {
//         echo "Restarting SonarQube"
//         stopSonarQube()
//         sh "docker run -d --name ${env.SONARQUBE_IMAGE_NAME} -p 9000:9000 -p 9092:9092 sonarqube"
//     } else {
//         echo "SonarQube already running"
//     }
// }

// def stopSonarQube() {
//     if (isSonarQubeRunning()) {
//         sh "docker stop ${env.SONARQUBE_IMAGE_NAME}"
//         sh "docker rm ${env.SONARQUBE_IMAGE_NAME}"
//     }
// }

// def isSonarQubeRunning() {
//     def imageID = sh(returnStdout: true, script: """
//         docker ps | grep '${env.SONARQUBE_IMAGE_NAME}' | awk -F" " '{print \$1;}' | tr -d '\n'
// """
//     )
//     echo "SonarQube ImageID=${imageID}"
//     return (imageID?.trim())
// }
