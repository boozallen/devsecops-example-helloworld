'''
Created on Aug 24, 2016

@author: rob.proper
'''

import os
import sys
import json
import requests

from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


class Container:

    SAUCELABS_API_BASE = "https://saucelabs.com/rest/v1"
    SAUCELABS_RESULTS_BASE = "https://saucelabs.com/beta/tests"
    BROWSERSTACK_API_BASE = "https://www.browserstack.com/automate"

    def __init__(self):
        self._log_enabled = self._logEnabled()
        self._location = self._location()
        self._environment = self._environment()
        self._resultReference = None
        self.browserLogIndex = 0
        self.setupDriver()

    def setupDriver(self):
        if self.localLocation():
            self.localSetup()
        self.driver = self._webdriver()
        self.log("driver.CAPABILITIES={0}".format(json.dumps(self.driver.desired_capabilities)))
        self.setupRemote()
        self.driver.implicitly_wait(self._implicitWait())

    def teardownDriver(self, successful = None):
        self.teardownRemote(successful)
        try:
            self.driver.quit()
        except Exception:
            pass
            self.log("Safely ignoring driver error (usually related to the PhantomJS webdriver)")
        if self.localLocation():
            self.localTeardown()

    def startSession(self):
        self.log("starting new session")
        self.driver.start_session(self._capabilities())

    def stopSession(self):
        self.log("stopping session")
        self.driver.stop_session()

    def _logEnabled(self):
        verbose = os.getenv('VERBOSE')
        return bool(not verbose is None and verbose != "")

    def log(self, message):
        if self._log_enabled:
            sys.stdout.write(message)
            sys.stdout.write("\n")
            sys.stdout.flush()

    def _location(self):
        location = os.getenv("LOCATION", "local")
        self.log("location={0}".format(location))
        return location

    def _environment(self):
        environment = os.getenv("ENVIRONMENT")
        self.log("environment={0}".format(environment))
        return environment

    def _webdriver(self):
        className = self._driverClassName()
        self._remoteUsername = self._remoteUsername()
        remoteURL = self._remoteURL()
        capabilities = self._capabilities()
        if remoteURL:
            self.log("RemoteURL")
            # Remote driver requires a executor (typically a Remote URL)
            browserProfile = FirefoxProfile()
            return webdriver.Remote(command_executor = remoteURL, keep_alive = True, \
                browser_profile = browserProfile, desired_capabilities = capabilities)
        clazz = self._driverClass(className)
        try:
            self.log("" + className + "(capabilities)")
            return clazz(desired_capabilities = capabilities)
        except Exception:
            self.log("Setting up " + className)
            if className == 'PhantomJS':
                # PhantomJS cannot handle capabilities
                self.log("Creating " + className)
                return clazz()
            else:
                # Firefox and Ie drivers have different name for desired capabilities parameter
                #return clazz(capabilities = capabilities)
                return clazz()

    def _remoteUsername(self):
        if self.localLocation():
            return None
        remoteUsername = os.getenv("REMOTE_USERNAME")
        if not remoteUsername:
            self.fail("No remote username given for {0}".format(self._location))
        return remoteUsername

    def _remoteURL(self):
        if self.localLocation():
            return None
        if self.saucelabsLocation():
            remoteURL = self.saucelabsRemoteURL()
        elif self.browserstackLocation():
            remoteURL = self.browserstackRemoteURL()
        else:
            remoteURL = os.getenv("REMOTE_URL")
        if not remoteURL:
            self.fail("No remote URL for {0}".format(self._location))
        return remoteURL

    def _driverClassName(self):
        className = os.getenv("WEBDRIVER_CLASS")
        if not className:
            className = "Chrome"
        self.log("WEBDRIVER_CLASS={0}".format(className))
        return className

    def _driverClass(self, className = "Firefox"):
        parts = "selenium.webdriver.{0}".format(className).split('.')
        module = ".".join(parts[:-1])
        clazz = __import__(module)
        for comp in parts[1:]:
            clazz = getattr(clazz, comp)
        return clazz

    def _capabilities(self):
        webdriverCapabilities = os.getenv("WEBDRIVER_CAPABILITIES", "{}")
        self.log("WEBDRIVER_CAPABILITIES={0}".format(webdriverCapabilities))
        capabilities = json.loads(webdriverCapabilities)
        capabilities['unexpectedAlertBehaviour'] = "ignore"
        capabilities['nativeEvents'] = True
        self.log("parameter.CAPABILITIES={0}".format(json.dumps(capabilities)))
        return capabilities

    def _implicitWait(self):
        implicit_wait = int(os.getenv("IMPLICIT_WAIT", 1))
        self.log("implicit_wait={0}".format(implicit_wait))
        return implicit_wait

    def _remoteTestID(self):
        return os.getenv("REMOTE_TEST_ID")

    def _buildID(self):
        return os.getenv("BUILD_ID")

    def getResultReference(self):
        return self._resultReference

    def setupRemote(self):
        self._resultReference = None
        if self.saucelabsLocation():
            self.saucelabsSetup()
        elif self.browserstackLocation(): 
            self.browserstackSetup()

    def teardownRemote(self, successful):
        if self.saucelabsLocation():
            self.saucelabsTeardown(successful)
        elif self.browserstackLocation(): 
            self.browserstackTeardown(successful)

    def localLocation(self):
        return (self._location == 'local')

    def localSetup(self):
        self.log("Try import Display from pyvirtualdisplay")
        self._virtualDisplay = None
        try:
            virtualdisplay = __import__("pyvirtualdisplay", globals(), locals(), ['Display'])
            self.log("Imported [" + str(virtualdisplay) + "]")
            if virtualdisplay:
                self._virtualDisplay = virtualdisplay.Display(visible=0, size=(1024, 768))
                self._virtualDisplay.start()
        except ImportError:
            pass

    def localTeardown(self):
        if self._virtualDisplay:
            self._virtualDisplay.stop()


    def saucelabsLocation(self):
        return (self._location == 'saucelabs')

    def saucelabsRemoteURL(self):
        return "http://{0}:{1}@ondemand.saucelabs.com:80/wd/hub".format(self._remoteUsername, \
            os.getenv("REMOTE_ACCESSKEY"))

    def saucelabsSetup(self):
        self.log("Setup for saucelabs")
        auth = (self._remoteUsername, os.getenv("REMOTE_ACCESSKEY"))
        baseURL = "{0}/{1}".format(self.SAUCELABS_API_BASE, self._remoteUsername)
        jobsURL = "{0}/jobs".format(baseURL)
        response = requests.get(jobsURL, \
            auth = auth, \
            headers = { 'content-type': 'application/json' }, \
            params = { 'full': 'true' })
        self.log("response={0}".format(json.dumps(response.json())))
        remoteJobid = self.saucelabsFindJobId(response.json(), self._remoteTestID())
        self.saucelabsJobURL = '{0}/jobs/{1}'.format(baseURL, remoteJobid)
        self._resultReference = "{0}/{1}".format(self.SAUCELABS_RESULTS_BASE, remoteJobid)
        response = requests.put(self.saucelabsJobURL,
            auth = auth, 
            headers = { 'content-type': 'application/json' }, 
            data = json.dumps({'name': self._buildID() }))

    def saucelabsTeardown(self, successful = None):
        if successful is None:
            self.log("Cannot set Saucelabs job result")
            return
        self.log("Saucelabs job result: {0}".format(successful))
        auth = (self._remoteUsername, os.getenv("REMOTE_ACCESSKEY"))
        response = requests.put(self.saucelabsJobURL, \
            auth = auth, \
            headers = { 'content-type': 'application/json' },\
            params = { 'content-type': 'application/json' }, \
            data = json.dumps({ 'passed': successful }))

    def saucelabsFindJobId(self, jobs, remoteTestId):
        if jobs is None:
            return None
        for job in jobs:
            data = job['custom-data']
            jobId = job['id']
            if (remoteTestId is None):
                return jobId
            if data and data['test-id'] and data['test-id'].encode('ascii','ignore').startswith(
               remoteTestId):
                return jobId
        return None


    def browserstackSetup(self):
        self.log("Setup for browserstack")
        if not 'webdriver.remote.sessionid' in self.driver.desired_capabilities:
            self.log("Unable to reference browserstack test, because property " + 
                "'{0}' is missing in [{1}]".format('webdriver.remote.sessionid', \
                json.dumps(self.driver.desired_capabilities)))
            return
        sessionID = self.driver.desired_capabilities['webdriver.remote.sessionid']
        capabilities = self._capabilities();
        auth = (self._remoteUsername, os.getenv("REMOTE_ACCESSKEY"))
        buildID = self.browserstackFindBuildId(auth, capabilities['build'])
        if buildID:
            self._resultReference = "{0}/builds/{1}/sessions/{2}".format(\
                self.BROWSERSTACK_API_BASE, buildID, sessionID)
            self.log("reference URL={0}".format(self._resultReference))
        else:
            self.log("Unable to find Browserstack session")


    def browserstackTeardown(self, successful = None):
        pass


    def browserstackLocation(self):
        return (self._location == 'browserstack')

    def browserstackRemoteURL(self):
        return "http://{0}:{1}@hub.browserstack.com:80/wd/hub".format(self._remoteUsername, \
            os.getenv("REMOTE_ACCESSKEY"))

    def browserstackFindBuildId(self, credentials, buildID):
        url = "{0}/builds.json?status=running&name={1}".format(self.BROWSERSTACK_API_BASE, buildID)
        response = requests.get(url, auth = credentials, headers = { 'content-type': \
            'application/json' })
        if not hasattr(response, 'json'):
            self.log("Browserstack response has no json object.")
            return None
        builds = response.json()
        if builds is None:
            return None
        for build in builds:
            automation = build['automation_build']
            if automation and automation['name'].encode('ascii','ignore') == buildID:
                return automation['hashed_id']
        return None

    def getDesiredCapability(self, name):
        value = self.driver.desired_capabilities[name] if name in self.driver.desired_capabilities \
            else ""
        if value:
            value = value.replace(" ", "").lower()
        return value

    def isIOs(self):
        return (self.getDesiredCapability('platformName') in ["ios"])

    def isInternetExplorer(self):
        return (self.getDesiredCapability('browserName') in ["ie", "internetexplorer"])

    def supportsBrowserLog(self):
        return not self.isInternetExplorer()

    def logBrowserConsole(self):
        if not self.supportsBrowserLog():
            self.log("Current driver does not support browser log")
        else:
            entries = self.getConsole('browser', self.browserLogIndex)
            if entries:
                self.log("\n------ BROWSER-LOG ------\n")
                for entry in entries:
                    self.log("{0}".format(entry))
                self.log("\n------------------------=\n")
                self.browserLogIndex = self.browserLogIndex + len(entries)
            else:
                self.log("Browser log is empty")

    def getConsole(self, logType = None, startingIndex = 0):
        logType = logType if logType else 'browser'
        entries = None
        try:
            i = startingIndex
            for entry in self.driver.get_log(logType):
                if i > 0:
                    i = i - 1
                else:
                    if entries is None:
                        entries = []
                    entries.append("{0}".format(entry))
        except Exception as e:
            entries = ["Unable to get {1} console, because {0}".format(e, logType)]
        finally:
            pass
        return entries

