import os
import sys
#import platform
#import urllib

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver

# http://clerk.house.gov/evs/2015/index.asp

class VoteScraper:
    def __init__(self):
        print "VoteScraper Initializing"
        os.environ['MOZ_HEADLESS'] = '1'
        print "os.environ['MOZ_HEADLESS'] = '1'"
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        print "binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)"
        self.driver = webdriver.Firefox(firefox_binary=binary)
        
    def fetch(self, string):
        print "Retrieving: "+string
        self.driver.get(string)
        print "Retrieved"

    def findElements(self, code, search):
        print "Finding element: "+search
        return self.driver.find_elements(code, search)

    def getText(self, elem):
        return ''.join(elem.get_property('textContent').strip())
    
    def getRollHouse(self, year, rollNum):
        self.fetch('http://clerk.house.gov/evs/'+str(year)+'/roll'+str(rollNum)+'.xml')
        issue = '.'.join(self.findElements('xpath', '//body/b[2]')[0].text.title().split())
        votes = self.findElements('xpath', '//table[@cols="3"]/tbody/tr/td')
        yea = []
        nea = []
        abst = []
        for x in range(0,3):
            yea.extend(votes[x].text.split('\n'))
        for x in range(3,6):
            nea.extend(votes[x].text.split('\n'))
        for x in range(6,9):
            abst.extend(votes[x].text.split('\n'))
        print issue
            
    
    def printInfo(self, ans):
        for x in ans:
            print(self.getText(x))
    
    def runTest(self):
        self.getRollHouse(2015, 702)

    def close(self):
        self.driver.quit()
        
test = VoteScraper()
test.runTest()
test.close()

print "Exiting"
print "Closed"

