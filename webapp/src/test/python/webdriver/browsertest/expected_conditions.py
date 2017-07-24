# -*- coding: utf-8 -*-

import re

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException

class ElementHasText(object):
    """An expectation for checking the the text of an element denoted by the locator.
    locator is the locator
    text is the expected text
    returns True if the text matches, false otherwise."""
    def __init__(self, locator, text, ignoreCase = True):
        self.locator = locator
        self.ignoreCase = ignoreCase
        self.expected = self.setCase(text if type(text) is str else text.encode('unicode-escape'))

    def __call__(self, driver):
        try:
            actual = _find_element(driver, self.locator).text
            if not type(actual) is str:
                actual = actual.encode('unicode-escape')
            actual = self.setCase(actual)
            #print "Comparing '{0}' and '{1}'".format(actual, self.expected)
            return actual == self.expected
        except StaleElementReferenceException:
            return False

    def setCase(self, text):
        return text.lower() if text and self.ignoreCase else text



class HasLocation(object):
    """An expectation for checking the current URL.
    url is the expected location. Must be a string or a regular expression
    returns True if the current URL matches 'rul', false otherwise."""
    def __init__(self, url):
        if not type(url) is list:
            url = [ url ]
        self.expected = []
        for u in url:
            self.expected.append(re.compile(u) if type(u) is str else u)

    def __call__(self, driver):
        return (self.matches(driver.current_url))

    def matches(self, actual):
        #print "===== matching {0} to {1}".format(actual, self.expected)
        if not actual:
            actual = ""
        elif not type(actual):
            actual = str(actual)
        for e in self.expected:
            if e.match(actual):
                return True
        else:
            return False



def _find_element(driver, by):
    """Looks up an element. Logs and re-raises ``WebDriverException``
    if thrown."""
    try :
        return driver.find_element(*by)
    except NoSuchElementException as e:
        raise e
    except WebDriverException as e:
        raise e
        