#!/usr/local/bin/python2.6
# encoding: utf-8
'''
BrowserTest -- shortdesc

BrowserTest is a description

It defines classes_and_methods

@author:     user_name
'''


import csv
import datetime
import json
import os


class Reporter():

    TEST_NAME_COLUMN = "Test Name"
    STATUS_COLUMN = "Status"
    REFERENCE_COLUMN = "Reference"

    def __init__(self, resultsFile):
        if not resultsFile:
            raise Exception("No results file name provided")
        self._resultsFile =  resultsFile

    def getResultsFile(self):
        return self._resultsFile

    def openResultsFile(self):
        with open(self._resultsFile, "w") as f:
            f.write("Status,Test Name,Reference\n")

    def recordResult(self, status, testName, reference = None):
        with open(self._resultsFile, "a") as f:
            f.write(status)
            f.write(",")
            f.write(testName)
            f.write(",")
            f.write(reference)
            f.write("\n")
            f.flush()

    def closeResultsFile(self):
        with open(self._resultsFile, "a") as f:
            f.close()
        self._writeReferenceFile()

    def _writeReferenceFile(self):
        testResultRows = ""
        with open(self._resultsFile, 'rb') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                label = row[Reporter.TEST_NAME_COLUMN]
                status = row[Reporter.STATUS_COLUMN]
                href = row[Reporter.REFERENCE_COLUMN]
                testResultRows = "{0}\n<tr><th>{1}</th><td class=\"{2}\">{2}</td></tr>".format(\
                    testResultRows,\
                    "<a href=\"{0}\">{1}</a>".format(href, label) if href else label,\
                    status)
        environment = os.getenv("ENVIRONMENT", "-")
        capabilities = json.loads(os.getenv("WEBDRIVER_CAPABILITIES", "{}"))
        project = capabilities['project'] if 'project' in capabilities else '-'
        build = capabilities['build'] if 'build' in capabilities else '-'
        capabilities['completion time'] = datetime.datetime.now().strftime("%Y/%m/%d %H:%S")
        capabilities['environment'] = environment
        testPropertyRows = ""
        keys = []
        for key in capabilities:
            keys.append(key)
        keys = sorted(keys)
        for i in range(0,len(keys)):
            key = keys[i]
            value = capabilities[key]
            key = key.replace("_", " ").capitalize()
            testPropertyRows = testPropertyRows + "<tr><th>{0}</th><td>{1}</td>".format(key, value)
        title = "{0}-{1}-{2}::TestResults".format(project, environment, build)
        contents = self._contents()
        contents = contents.replace("{TITLE}", title)
        contents = contents.replace("{TEST_PROPERTIES}", testPropertyRows)
        contents = contents.replace("{TEST_RESULTS}", testResultRows)
        with open(self._resultsFile.replace(".csv", ".html"), "w") as f:
            f.write(contents)
            f.close()

    def _contents(self):
        return '''
<!doctype html>
<html>
<head>
<title>{TITLE}</title>
<style>
h1 {display:block; margin:auto;width:96%; text-align:center;}
table {padding:0px; margin:auto;width:96%;border: 1px solid #EEE}
caption {display:none;}
thead th {background-color:#210065; color:white;}
tbody th {background-color:#EEE;}
th {border:0px; padding:5px 15px 5px 15px; text-align:left; margin:0; width:40%;}
td {border:0px; padding:5px 15px 5px 15px; text-align:left; margin:0; width:60%;border: 1px solid #EEE}
td.pass {background-color:green; color:white;}
td.failure {background-color:red; color:white;}
td.error {background-color:orange; color:white;}
</style>
</head>
<body>
<h1>Test Information</h1>
<table>
<caption>Test Information</caption>
<tbody>
{TEST_PROPERTIES}
</tbody>
</table>
<h1>Test Results</h1>
<table>
<caption>Test Results</caption>
<thead>
<tr><th>Test</th><th>Status</th></tr>
</thead>
<tbody>
{TEST_RESULTS}
</tbody>
</table>
</body>
</html>
'''

