import os

from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert

from webdriver.browsertest.TestSuite import TestSuite
from webdriver.browsertest.BrowserTest import BrowserTest


class HelloWorldTestBase(BrowserTest):

    @staticmethod
    def runTestSuite(verbose = None):
        TestSuite(verbose = verbose).run()

    @staticmethod
    def runTestCase(clazz, verbose = None):
        TestSuite(clazz = clazz, verbose = verbose).run()

    # See http://getbootstrap.com/css/#responsive-utilities
    VIEWPORT_EXTRASMALL_BREAKPOINT = 768
    VIEWPORT_SMALL_BREAKPOINT = 992
    VIEWPORT_MEDIUM_BREAKPOINT = 1200

    def setUp(self):
        super(HelloWorldTestBase, self).setUp()
        defaultWidth = os.getenv("DEFAULT_WINDOW_WIDTH")
        self._followLinkMaxRetries = int(os.getenv('FOLLOW_LINK_MAX_RETRIES', '2'))
        try:
            if defaultWidth:
                # Window must be at least wider than the extra small breakpoint
                # to ensure non-mobile devices do not reverting to (small) mobile 
                # device settings
                minWidth = 600
                defaultWidth = max(int(defaultWidth), minWidth)
                self.log("Set default window with: {0}".format(defaultWidth))
                self.windowSetWidth(defaultWidth)
            else:
                self.log("Maximize window")
                self.windowMaximize()
        except UnexpectedAlertPresentException as e:
            #if self.usesSharedContainer():
            #    # Can happen when sharing the driver across tests, 
            #    # e.g. when test ended on page the causes a refresh alert
            #    # This simplifies handling the alert
            self.log("Automatically accepting alert: {0}".format(str(e)))
            Alert(self.driver).accept()
            #else:
            #    # Should not happen
            #    raise  
        self.openBaseUrl()
          
    def isExtrasmallViewport(self):
        return bool(self.windowWidth() < self.VIEWPORT_EXTRASMALL_BREAKPOINT)

    def isSmallViewport(self):
        width = self.windowWidth()
        return bool((self.VIEWPORT_EXTRASMALL_BREAKPOINT <= width) and \
            (width < self.VIEWPORT_SMALL_BREAKPOINT))

    def isMediumViewport(self):
        width = self.windowWidth()
        return bool((self.VIEWPORT_SMALL_BREAKPOINT <= width) and \
            (width < self.VIEWPORT_MEDIUM_BREAKPOINT))

    def isLargeViewport(self):
        width = self.windowWidth()
        return bool(self.VIEWPORT_MEDIUM_BREAKPOINT <= width)


    def validateLink(self, url, expectedText = None, expectedTitle = None, expectedUrl = None, \
        xpathContext = None):
        xpathContext = xpathContext if xpathContext else ""
        selector = ".//{1}a[@href='{0}']".format(url, xpathContext)
        if expectedText:
            self.assertTextPresent(By.XPATH, selector, expectedText)

        totalTries = self._followLinkMaxRetries + 1
        for i in range(0, totalTries):
            try:
                self.click(By.XPATH, selector, "Click {0}".format(expectedText), \
                    expectedURL = expectedUrl if expectedUrl else url)
                break
            except TimeoutException:
                retry = i + 1 # First 'try' is not a retry
                if retry < totalTries:
                    pass
        if expectedTitle:
            self.assertTitle(expectedTitle);

    def assertTitle(self, expectedTitle):
        self.assertEquals(self.driver.title, expectedTitle);

