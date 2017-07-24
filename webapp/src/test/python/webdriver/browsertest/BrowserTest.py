#!/usr/local/bin/python2.6
# encoding: utf-8
'''
BrowserTest -- shortdesc

BrowserTest is a description

It defines classes_and_methods

@author:     user_name
'''


import sys
import os
import re
import time
import traceback
import unittest

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.webdriver.common.alert import Alert

from selenium.common.exceptions import WebDriverException


from webdriver.browsertest.TestSuite import Container
from webdriver.browsertest.TestSuite import TestSuite

from webdriver.browsertest.expected_conditions import ElementHasText
from webdriver.browsertest.expected_conditions import HasLocation

KEY_MAP = {
    "ADD": u'\ue025',
    "ALT": u'\ue00a',
    "ARROW_DOWN": u'\ue015',
    "ARROW_LEFT": u'\ue012',
    "ARROW_RIGHT": u'\ue014',
    "ARROW_UP": u'\ue013',
    "BACKSPACE": u'\ue003',
    "BACK_SPACE": u'\ue003',
    "CANCEL": u'\ue001',
    "CLEAR": u'\ue005',
    "COMMAND": u'\ue03d',
    "CONTROL": u'\ue009',
    "DECIMAL": u'\ue028',
    "DELETE": u'\ue017',
    "DIVIDE": u'\ue029',
    "DOWN": u'\ue015',
    "END": u'\ue010',
    "ENTER": u'\ue007',
    "EQUALS": u'\ue019',
    "ESCAPE": u'\ue00c',
    "F1": u'\ue031',
    "F10": u'\ue03a',
    "F11": u'\ue03b',
    "F12": u'\ue03c',
    "F2": u'\ue032',
    "F3": u'\ue033',
    "F4": u'\ue034',
    "F5": u'\ue035',
    "F6": u'\ue036',
    "F7": u'\ue037',
    "F8": u'\ue038',
    "F9": u'\ue039',
    "HELP": u'\ue002',
    "HOME": u'\ue011',
    "INSERT": u'\ue016',
    "LEFT": u'\ue012',
    "LEFT_ALT": u'\ue00a',
    "LEFT_CONTROL": u'\ue009',
    "LEFT_SHIFT": u'\ue008',
    "META": u'\ue03d',
    "MULTIPLY": u'\ue024',
    "NULL": u'\ue000',
    "NUMPAD0": u'\ue01a',
    "NUMPAD1": u'\ue01b',
    "NUMPAD2": u'\ue01c',
    "NUMPAD3": u'\ue01d',
    "NUMPAD4": u'\ue01e',
    "NUMPAD5": u'\ue01f',
    "NUMPAD6": u'\ue020',
    "NUMPAD7": u'\ue021',
    "NUMPAD8": u'\ue022',
    "NUMPAD9": u'\ue023',
    "PAGE_DOWN": u'\ue00f',
    "PAGE_UP": u'\ue00e',
    "PAUSE": u'\ue00b',
    "RETURN": u'\ue006',
    "RIGHT": u'\ue014',
    "SEMICOLON": u'\ue018',
    "SEPARATOR": u'\ue026',
    "SHIFT": u'\ue008',
    "SPACE": u'\ue00d',
    "SUBTRACT": u'\ue027',
    "TAB": u'\ue004',
    "UP": u'\ue013',
}

INVERSE_KEY_MAP = dict((v, k) for k, v in KEY_MAP.items())

class BrowserTest(unittest.TestCase):

    RESULT_PASS = 'pass'
    RESULT_ERROR = 'error'
    RESULT_FAILURE = 'failure'

    def setUp(self):
        self._log_enabled = self._logEnabled()
        self._test_name = self._testName()
        self.log("")
        self.log("")
        self.log("==============================================")
        self.log("Start test {0}".format(self._test_name))
        self.log("----------------------------------------------")
        self._step_delay = self._stepDelay()
        self._numberOfErrors = len(self._result.errors)
        self._numberOfFailures = len(self._result.failures)
        self._resultReference = None
        self._environment = self._environment()
        self._default_wait = self._defaultWait()
        self._verificationErrors = []
        self.accept_next_alert = True
        self.setupDriver()

    def tearDown(self):
        self.setResultStatus()
        self.recordResult()
        self.teardownDriver()
        self.assertEqual([], self._verificationErrors)
        self.log("")
        self.log("Finished test {0}".format(self._test_name))
        self.log("----------------------------------------------")
        self.log("")
        self._result = None

    def setupDriver(self):
        if TestSuite.webDriver is None:
            self._driverContainer = Container()
            self._sharedContainer = True
        else:
            self._driverContainer = TestSuite.webDriver
            self._sharedContainer = False
        self._resultReference = self._driverContainer.getResultReference()
        self.driver = self._driverContainer.driver
        self.openBaseUrl()

    def openBaseUrl(self):
        self.base_url = self._base_url()
        cookie = self._cookie()
        self.log("")
        if cookie is None or cookie.strip() == "":
            self.log("No cookie specified")
            self.open("/", handleAlert = True)
        else:
            #self.driver.delete_all_cookies()
            self.open("/?"  + self._cookie(), message = " using specified cookie", \
                handleAlert = True)

    def teardownDriver(self):
        self._driverContainer.logBrowserConsole()
        if self._sharedContainer:
            self.log("TearDown shared driver")
            self._driverContainer.teardownDriver(self.wasSuccessful())

    def isIOs(self):
        return self._driverContainer.isIOs()

    def usesSharedContainer(self):
        return bool(self._sharedContainer)

    def wasSuccessful(self):
        return self._resultStatus == BrowserTest.RESULT_PASS

    def setResultStatus(self):
        if len(self._result.errors) > self._numberOfErrors:
            self._resultStatus = BrowserTest.RESULT_ERROR
        elif len(self._result.failures) > self._numberOfFailures:
            self._resultStatus = BrowserTest.RESULT_FAILURE
        else:
            self._resultStatus = BrowserTest.RESULT_PASS

    def recordResult(self):
        if self._resultStatus is None:
            self.log("WARNING: No result found. This can happen when you override 'self.run()'" +\
                " or programmatically change 'self._result'")
        elif not TestSuite.reporter is None:
            reporter = TestSuite.reporter 
            self.log("Logging results to {0}".format(reporter.getResultsFile()))
            reporter.recordResult(self._resultStatus, self._test_name, \
                self._resultReference if self._resultReference else "")
        else:
            self.log("No results file given")

    def _testName(self):
        name = self.id()
        prefix = "__main__."
        if name.startswith(prefix):
            return name[len(prefix):]
        return name

    def _environment(self):
        environment = os.getenv("ENVIRONMENT")
        self.log("environment={0}".format(environment))
        return environment

    def _defaultWait(self):
        default_wait = os.getenv("DEFAULT_WAIT")
        try:
            default_wait = int(default_wait)
        except:
            default_wait = 15
        
        self.log("default_wait={0}".format(default_wait))
        return default_wait

    def _base_url(self):
        baseURL = os.getenv("BASE_URL")
        if baseURL is None:
            self.fail("Set environment variable 'BASE_URL' (or alternatively override " + 
                "'_base_url' to return base URL of test subject")
        return baseURL

    def _cookie(self):
        return os.getenv('COOKIE')

    def _executionID(self):
        return os.getenv('EXECUTION_ID')

    def _logEnabled(self):
        verbose = os.getenv('VERBOSE')
        return bool(not verbose is None and verbose != "")

    def _stepDelay(self): 
        delay = float(os.getenv('STEP_DELAY', 0))
        self.log("step delay = {0}".format(delay))
        return delay

    def getDefaultWaitFor(self):
        return self._default_wait

    def isLogEnabled(self):
        return bool(self._log_enabled);

    def cookie(self):
        return self._cookie;

    def getEnvironment(self):
        return self._environment

    def getBrowser(self):
        capabilities = self._capabilities()
        browser = capabilities['browser']
        if not browser:
            browser = self._driverClassName()
        return browser

    def run(self, result = None):
        self._result = result
        unittest.TestCase.run(self, result)

    def log(self, message):
        if self._log_enabled:
            sys.stdout.write(message)
            sys.stdout.write("\n")
            sys.stdout.flush()

    def matches(self, actual, expected):
        if not type(expected) is list:
            expected = [ expected ]
        for e in expected:
            if type(e) is str:
                e = re.compile(e)
            message = "Comparing {0} to {1}".format(actual, e.pattern)
            self.log(message)
            if e.match(actual):
                self.log(message + ": Match")
                return True
            self.log(message + ": No match")
        else:
            return False

    def describeValues(self, values):
        if not type(values) is list:
            return self.describeValue(values)
        return "[" + map(self.describeValue, values).join(",") + "]"

    def describeValue(self, value):
        if not value:
            return "-"
        if type(value) is str: 
            return value
        return value.pattern

    def describeElement(self, by, value):
        return "element[{0}={1}]".format(by, value)

    def describeKey(self, key):
        return "Keys." + INVERSE_KEY_MAP[key] if key in INVERSE_KEY_MAP \
            else key.encode('unicode-escape')

    def onFail(self, by, value, message, text):
        if message: 
            message = message + ". "
        else:
            message = ""
        if text:
            text = ":" + text
        else:
            text = ""
        self.fail("Failed: {0}{1} {2}".format(message, self.describeElement(by, value), text))


    #def clearKeys(self):
    #    return [ Keys.CONTROL+"a", Keys.DELETE ]

    def focus(self, by, selector, message = None):
        return self._change_focus(by, selector, True, message)

    def blur(self, by, selector, message = None):
        return self._change_focus(by, selector, False, message)

    def _change_focus(self, by, selector, focus = True, message = None):
        description = self.describeElement(by, selector)
        wait_for = self.getDefaultWaitFor()
        change = 'focus' if focus else 'blur'
        element = self.assertElementPresent(by, selector, message, wait_for = wait_for)
        self.log("{0} on {1}{2}".format(change, description, \
            ", because " + message if message else ""))
        script = ""
        if by == By.ID:
            script = "jQuery(\"#{0}\")".format(selector)
        elif by == By.CSS_SELECTOR:
            script = "jQuery(\"{0}\")".format(selector)
        else:
            self.onFail(by, selector, message, "Cannot {0} for this selector type (yet).".\
                format(change))
        script = "{0}.{1}();".format(script, change)
        self.log("{0} on {1} using {2}".format(change, description, script))
        self.driver.execute_script(script)
        return element

    def tab(self, by, selector, message = None):
        self.log("Tab to next active element. WARNING: Does not work for Safari driver")
        element = self.driver.switch_to.active_element
        element.send_keys(Keys.TAB)
        # script = """
        #     var f = jQuery('#{0}'), e = f, 
        #         hasTag = function(e, tag) {{ return (e.prop("tagName") === tag); }},
        #         getAttr = function(e, attr) {{ return e.attr(attr); }},
        #         i = 0;
        #     while (e && (i < 1000)) {{
        #         e = e.next()
        #         if (
        #             (getAttr(e, 'tabindex') && (getAttr(e, 'tabindex') != -1)) || 
        #             (hasTag(e, 'a') && getAttr(e, 'h')) ||
        #             (hasTag(e, 'input') && (getAttr(e, 'type') !== 'hidden')) ||
        #             (hasTag(e, 'textarea'))
        #            )
        #         {{
        #             f.blur(); 
        #             e.focus();
        #             e = undefined;
        #         }}
        #         i = i + 1;
        #    }}
        #     """.format(selector)
        # self.log("About to execute '{0}'".format(script))
        # self.driver.execute_script(script)
        # self.log("Executed".format(script))

    def enter(self, message = None):
        self.log("Select active element")
        element = self.driver.switch_to.active_element
        element.send_keys(Keys.ENTER)

    def sendKeys(self, by, value, key, message = None):
        element = self.findElement(by, value)
        if not element: self.onFail(by, value, message, "Not found")
        if not element.is_displayed(): self.onFail(by, value, message, "Not visible")
        if not key: self.onFail(by, value, message, "Not key (or keys) given")
        if type(key) is list:
            keys = key
        else:
            keys = [ key ]
        if message:
            self.log(message)
        for k in keys:
            if k == Keys.CLEAR:
                # Converting to clear element, because Safarri/WebKit does not support the key
                self.clearElement(by, value)
            else:
                self.log("Send '{0}' to {1}".format(self.describeKey(k), \
                    self.describeElement(by, value)))
                element.send_keys(k)
            self.throttle()
        return element

    def throttle(self):
        if self._step_delay > 0:
            time.sleep(self._step_delay)

    def findElement(self, by, value):
        return self.driver.find_element(by, value)

    def assertElementIsDisplayed(self, by, value, message = None):
        if self.element.isElementHidden(by, value):
            self.onFail(by, value, "Is hidden, but expect visible", message)

    def assertElementIsHidden(self, by, value, message = None):
        if self.isElementVisible(by, value):
            self.onFail(by, value, "Is displayed, but expected hidden", message)

    def isElementHidden(self, by, value):
        return not self.isElementVisible(by, value)

    def isElementVisible(self, by, value):
        element = self.findElement(by, value)
        self.log(self.describeElement(by, value) + ("exists" if element else "does not exist"))
        visible = element and element.is_displayed()
        self.log(self.describeElement(by, value) + ("visible" if visible else "hidden"))
        return visible


    def getValue(self, name, element = None, by = None, selector = None):
        if not element:
            element = self.findElement(by, selector)
        return element.get_attribute(name) if element else None


    def open(self, url = None, message = None, handleAlert = True, makeAbsolute = True):
        if url is None:
            url = "/"
        if url.startswith("http"):
            prefix = "absolute"
        else: 
            prefix = "relative"
            if not url.startswith("/"):
                url = "/" + url
            if makeAbsolute:
                url = self.base_url + url
        if  message: 
            message = " " + message
        else:
            message = ""
        self.log("Opening {0} URL '{1}'{2}{3}".format(prefix, url, message, \
            " (Automatically handle unexpected alerts)" if handleAlert else ""))
        try:
            self.driver.get(url)
        except UnexpectedAlertPresentException:
            if handleAlert:
                alert = Alert(self.driver)
                text = alert.text
                if not type(text) is str:
                    # Likely unicode
                    text = text.encode('ascii', 'ignore')
                self.log("Accepting unexpected alert ({0})".format(text))
                alert.accept()
                self.log("Retrying opening {0}".format(url))
                self.open(url, message, False, makeAbsolute)
            else:
                raise
        self.throttle()

    def assertTextPresentNow(self, by, value, expectedText, message = None):
        return self.assertTextPresent(by, value, expectedText, message, 0)

    def assertTextPresent(self, by, value, expectedText, message = None, wait_for = None, \
        ignoreCase = True):
        if not wait_for: wait_for = self.getDefaultWaitFor()
        self.assertElementPresent(by, value, message, wait_for)
        # lookup again to avoid stale element exception
        #self.assertElementPresent(by, value, message, wait_for)
        if not type(expectedText) is str:
            expectedText = expectedText.encode('unicode-escape')
        try:
            self.log("{3}Waiting a maximum of {0}s for text {1} in {2}{3}".format(\
                wait_for, expectedText, self.describeElement(by, value),\
                ". " + message if message else ""))
            return WebDriverWait(self.driver, wait_for).until(ElementHasText(\
                (by, value), expectedText, ignoreCase))
        except Exception:
            self.onFail(by, value, message, "Expected text {0}, but timed-out after {1} seconds.".\
                format(expectedText, wait_for, traceback.format_exc()))

    def assertElementPresentNow(self, by, value, message=None):
        return self.assertElementPresent(by, value, message, 0)

    def assertElementPresent(self, by, value, message = None, wait_for = None):
        if not wait_for: wait_for = self.getDefaultWaitFor()
        try:
            self.log("Waiting a maximum of {1}s for {0}{2}".format(self.describeElement(by, value), \
                wait_for, ". " + message if message else ""))
            element = WebDriverWait(self.driver, wait_for).until(EC.visibility_of_element_located(\
                (by, value)))
            self.throttle()
            return element
        except Exception as e:
            self.onFail(by, value, message, \
                "Expected to be present, but timed-out after {0} seconds.".format(wait_for, \
                    traceback.format_exc(e)))

    def clearElement(self, by, value, message = None):
        element = self.assertElementPresent(by, value, message = message)
        self.log("Clear {0}".format(self.describeElement(by, value)))
        element.clear()
        self.throttle()
        return element

    def enterText(self, by, value, text, message = None, key = None, clear = True):
        element = self.assertElementPresent(by, value, message = message)
        if clear:
            self.log("Clear {0}".format(self.describeElement(by, value)))
            element.clear()
        element = self.sendKeys(by, value, text)
        if key:
            element = self.sendKeys(by, value, key)
        return element

    def enterAndSelectFromDropdown(self, by, value, text, message = None, nth = 1, \
        dropdownBy = None, dropdownValue = None):
        element = self.assertElementPresent(by, value, message = message)
        if not element: self.onFail(by, value, message, "Not found")
        element = self.sendKeys(by, value, text)

        if dropdownBy:
            self.assertElementPresent(dropdownBy, dropdownValue, message)
        description = "{0}-th from {1} dropdown".format(nth, self.describeElement(by, value))
        self.log("Find " + description)
        for i in range(1, nth+1):
            element = self.sendKeys(by, value, Keys.ARROW_DOWN)

        element = self.sendKeys(by, value, Keys.ENTER, message = "Select " + description)
        return element

    def hover(self, by, value, message = None):
        element = self.assertElementPresent(by, value, message = message)
        self.log("Hover mouse over {0}".format(self.describeElement(by, value)))
        hoverAction = ActionChains(self.driver).move_to_element(element)
        if not hoverAction: self.onFail(by, value, message, "Unable to move to")
        hoverAction.perform()
        return element


    def click(self, by, value, message, expectedURL = None, key = None, wait_for = None):
        description = self.describeElement(by, value)
        if not wait_for: wait_for = self.getDefaultWaitFor()
        self.assertElementPresent(by, value, message, wait_for = wait_for)
        element = self.findElement(by, value)
        if key:
            element = self.sendKeys(by, value, key)
        else:
            self.log("Click {0}{1}".format(description, ". "+ message if message else ""))
            element.click()
            self.throttle()
        if expectedURL:
            self.assertLocation(by, value, expectedURL, message = message, wait_for = wait_for)
        else:
            self.log("No specific URL expected")

    def assertLocation(self, by, value, expectedURL, message = None, wait_for = None):
        if not wait_for: wait_for = self.getDefaultWaitFor()
        try:
            self.log("Waiting a maximum of {0}s for location {1} on {2}".format(\
                wait_for, expectedURL, self.describeElement(by, value)))
            element = WebDriverWait(self.driver, wait_for).until(HasLocation(expectedURL))
            self.throttle()
            return element
        except Exception as e:
            self.onFail(by, value, message, \
                "Expected location {0}, but timed-out after {1} seconds:\n{2}".format(expectedURL, \
                    wait_for, traceback.format_exc(e)))

    def populateAndSubmitForm(self, formData, buttonBy = None, buttonValue = None):
        self.populateFormByID(formData)
        self.submitForm(buttonBy, buttonValue)

    def populateFormByID(self, formData):
        for form_id, value in formData.iteritems():
            self.sendKeys(By.ID, form_id, value, message = "Setting form field")

    def submitForm(self, buttonBy = None, buttonValue = None):
        self.click(buttonBy if buttonBy else By.CSS_SELECTOR, buttonValue if buttonValue else \
            "button.submitBtn", "Submit form")

    def selectOptionByText(self, by, value, text):
        self.log("selection '{0}' option from {1}".format(text, self.describeElement(by, value)))
        return Select(self.assertElementPresent(by, value)).select_by_visible_text(text)

    def windowMaximize(self):
        self.log("Maximize window")
        self.driver.maximize_window()

    def windowScrollPageHeight(self):
        self.windowScroll(x = 0, y = "document.body.scrollHeight")

    def windowScroll(self, x = 0, y = 0):
        self.driver.execute_script("window.scrollTo({0}, {1});".format(x, y))

    def windowWidth(self):
        window_size = self.driver.get_window_size()
        return window_size[u'width']

    def windowHeight(self):
        window_size = self.driver.get_window_size()
        return window_size[u'height']

    def windowSetWidth(self, width):
        self.windowSetSize(width, self.windowHeight())
        return self.windowWidth()

    def windowSetHeight(self, height):
        self.windowSetSize(self.windowWidth(), height)
        return self.windowHeight()

    def windowSetSize(self, width, height):
        try:
            self.driver.set_window_size(max(0, width), max(0, height))
        except WebDriverException as e:
            message = str(e)
            if 'Not yet implemented' in message:
                self.log("The current WebDriver does not support window resizing. Ignoring.")
            else:
                self.log("Message=[{0}".format(message))
                raise

    def narrowWindow(self, width):
        """Narrows the width of the window to given width.
           If the window is already narrower, no change is made.
           E.g. if the window has a current width of 1280, and a width of 800 is given,
           the resulting width is 800. However, if the current width is 480, the resulting
           width is 480.
           Key arguments:
           width    - The width to set to window to
        """
        width = min(width, self.windowWidth())
        height = self.windowHeight()
        self.driver.set_window_size(width, height)

    def delay(self, seconds = 1):
        seconds = max(0, seconds)
        if seconds > 0:
            self.log("Delay {0} second{1}".format(seconds, "" if seconds == 1 else "s"))
            time.sleep(seconds)

    # The following methods provide backwards compatibility to unottest.TestCase in Python 2.6,
    # which is the default Python version on RHEL 6.x 
    def assertLess(self, a, b):
        try:
            super(BrowserTest, self).assertLess(a, b)
        except AttributeError:
            if not(a < b):
                self.fail("Expected {0} < {1}".format(a, b))

    def assertLessEqual(self, a, b):
        try:
            super(BrowserTest, self).assertLessEqual(a, b)
        except AttributeError:
            if not(a <= b):
                self.fail("Expected {0} <= {1}".format(a, b))

    def assertGreater(self, a, b):
        try:
            super(BrowserTest, self).assertGreater(a, b)
        except AttributeError:
            if not(a > b):
                self.fail("Expected {0} > {1}".format(a, b))

    def assertGreaterEqual(self, a, b):
        try:
            super(BrowserTest, self).assertGreaterEqual(a, b)
        except AttributeError:
            if not(a > b):
                self.fail("Expected {0} >= {1}".format(a, b))

    def assertRegexpMatches(self, s, r):
        try:
            super(BrowserTest, self).assertRegexpMatches(s, r)
        except AttributeError:
            if not(s.search(r)):
                self.fail("Expected regular expression {0} in {1}".format(s, r))

    def assertIsInstance(self, a, b):
        try:
            super(BrowserTest, self).assertIsInstance(a, b)
        except AttributeError:
            if not isinstance(a, b):
                self.fail("Expected {0} is an instance of {1}".format(a, b))

    def assertNotIsInstance(self, a, b):
        try:
            super(BrowserTest, self).assertNotIsInstance(a, b)
        except AttributeError:
            if not(not isinstance(a, b)):
                self.fail("Expected {0} is not an instance of {1}".format(a, b))

    def assertIn(self, a, b):
        try:
            super(BrowserTest, self).assertIsIn(a, b)
        except AttributeError:
            if not(a in b):
                self.fail("Expected {0} in {1}".format(a, b))

    def assertNotIn(self, a, b):
        try:
            super(BrowserTest, self).assertNotIn(a, b)
        except AttributeError:
            if not(a not in b):
                self.fail("Expected {0} not in {1}".format(a, b))

    def assertIs(self, a, b):
        try:
            super(BrowserTest, self).assertIsIn(a, b)
        except AttributeError:
            if not(a is b):
                self.fail("Expected {0} is {1}".format(a, b))

    def assertIsNot(self, a, b):
        try:
            super(BrowserTest, self).assertIsNot(a, b)
        except AttributeError:
            if not(a is not b):
                self.fail("Expected {0} is not {1}".format(a, b))

    def assertIsNone(self, a):
        try:
            super(BrowserTest, self).assertIsNone(a)
        except AttributeError:
            if not(a is None):
                self.fail("Expected None, but got {0}".format(a))

    def assertIsNotNone(self, a):
        try:
            super(BrowserTest, self).assertIsNotNone(a)
        except AttributeError:
            if not(a is not None):
                self.fail("Expected something other than None, but got None")

