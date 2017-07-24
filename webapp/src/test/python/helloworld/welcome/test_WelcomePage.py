# -*- coding: utf-8 -*-

from helloworld.HelloWorldTestBase import HelloWorldTestBase 
from selenium.webdriver.common.by import By

class test_WelcomePage(HelloWorldTestBase):

    def testWelcomeMessage(self):
        self.assertTextPresent(By.CSS_SELECTOR, "h1", "Hello World");

if __name__ == "__main__":
    HelloWorldTestBase.runTestCase(test_WelcomePage)