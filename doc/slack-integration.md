# Jenkins-Slack Integration

Jenkins can easily be integrated with Slack using the built-in `slackSend` command.

E.g. to add a notification to the end of the pipeline:
```
    post { 
        failure { 
            slackSend color: "warning", message: "${env.SLACK_JOB_REFERENCE} failed"
        }
        success { 
            slackSend color: "good", message: "${env.SLACK_JOB_REFERENCE} succeeded"
        }
   }
```


This could be combined with some additional code to build slack messages, e.g. adding @mentions
of the github change author:

```
def prepareSlack() {
    def jobName = env.JOB_NAME.replace('%2F', '/')
    def mention = getSlackMention(getGitAuthor())
    env.SLACK_JOB_REFERENCE = ((mention) ? "${mention} " : "") + 
        "${jobName}: Build ${env.BUILD_NUMBER}"
}

def getGitAuthor() {
    return sh(script: "git show --name-only | awk '/^Author:/ {print \$2;}' | tr '\n' ' '",
        returnStdout: true).trim()
}

def getSlackMention(author) {
    if (env.SLACK_USER_MAPPING == "") {
        echo "Environment variable 'SLACK_USER_MAPPING' not defined"
        return ""
    }
    echo "Getting ${author} from ${env.SLACK_USER_MAPPING}"
    def slurper = new JsonSlurper()
    def mapping = slurper.parseText(env.SLACK_USER_MAPPING)
    def slackUser = mapping[author]
    echo "slackUser=${slackUser}"
    return (slackUser) ? "@${slackUser}" : ""
}
```

This assume a global environment variable (`SLACK_USER_MAPPING`) to be defined in Jenkins
to define a github to slack user mapping, assuming usernames do not match.
```
    SLACK_USER_MAPPING="{\"my-github-user-name\": \"my-slack-user-name\"}"
```