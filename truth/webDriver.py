import requests
import time
import os

from lxml import html
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class Driver:
    def __init__(self):
        self.initDriver()

    def initDriver(self):
        #os.environ['MOZ_HEADLESS'] = '1'
        #binary = FirefoxBinary('C:\\Program Files\\Python27\\')
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(firefox_options=options)

    def restartDriver(self):
        self.driver.quit()
        self.initDriver()

    def fetch(self, string):
        """Use Selenium driver to get JavaScript pages"""
        time.sleep(1.4)
        self.driver.get(string)
        self.tree = html.fromstring(self.driver.page_source)

    def get(self, url_string):
        """Use python.requests to get pure HTML Pages"""
        page = requests.get(url_string)#, header)
        self.tree = html.fromstring(page.content)
        time.sleep(1.2)

    def find(self, string):
        """Parse XML Tree for *string* by XPath"""
        return self.tree.xpath(string)

    def printTree(self):
        """Prints current tree"""
        return html.tostring(self.tree)

    def quit(self):
        self.driver.quit()
