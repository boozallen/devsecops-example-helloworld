
from webdriver.browsertest.Bootstrap import Bootstrap

Bootstrap.loadModulesFromPath('modules-path')

from webdriver.browsertest.expected_conditions import ElementHasText
from webdriver.browsertest.expected_conditions import HasLocation
from webdriver.browsertest import BrowserTest
from webdriver.browsertest import TestSuite
from webdriver.browsertest import Container

