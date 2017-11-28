import os
import sys
import time
from dbPopulate import DBPopulate

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver

class CongressScraper:
    def __init__(self):
        self.populator = DBPopulate()
        self.important_index = 0
        self.names = []
        self.congr = {}
        self.stateDict = {'ALABAMA':'AL','ALASKA':'AK','ARIZONA':'AZ','ARKANSAS':'AR','CALIFORNIA':'CA','COLORADO':'CO',
                          'CONNECTICUT':'CT','DELAWARE':'DE','FLORIDA':'FL','GEORGIA':'GA','HAWAII':'HI','IDAHO':'ID',
                          'ILLINOIS':'IL','INDIANA':'IN','IOWA':'IA','KANSAS':'KS','KENTUCKY':'KY','LOUISIANA':'LA','MAINE':'ME',
                          'MARYLAND':'MD','MASSACHUSETTS':'MA','MICHIGAN':'MI','MINNESOTA':'MN','MISSISSIPPI':'MS','MISSOURI':'MO',
                          'MONTANA':'MT','NEBRASKA':'NE','NEVADA':'NV','NEW HAMPSHIRE':'NH','NEW JERSEY':'NJ','NEW MEXICO':'NM',
                          'NEW YORK':'NY','NORTH CAROLINA':'NC','NORTH DAKOTA':'ND','OHIO':'OH','OKLAHOMA':'OK','OREGON':'OR',
                          'PENNSYLVANIA':'PA','RHODE ISLAND':'RI','SOUTH CAROLINA':'SC','SOUTH DAKOTA':'SD','TENNESSEE':'TN',
                          'TEXAS':'TX','UTAH':'UT','VERMONT':'VT','VIRGINIA':'VA','WASHINGTON':'WA','WEST VIRGINIA':'WV',
                          'WISCONSIN':'WI','WYOMING':'WY','NORTHERN MARIANA ISLANDS':'MP','GUAM':'GU','PUERTO RICO':'PR',
                          'VIRGIN ISLANDS':'VI','AMERICAN SAMOA':'AS','DISTRICT OF COLUMBIA':'DC','PALAU':'PW',
                          'FEDERATED STATES OF MICRONESIA':'FM','MARSHALL ISLANDS':'MH'}
        print "WebDriver Initializing"
        print "os.environ['MOZ_HEADLESS'] = '1'"
        print "binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)\n"
        self.initDriver()
        
    def initDriver(self):
        os.environ['MOZ_HEADLESS'] = '1'
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        self.driver = webdriver.Firefox(firefox_binary=binary)
        self.driver.implicitly_wait(5)
        
    def restartDriver(self):
        self.driver.quit()
        self.initDriver()

    def fetch(self, string):
        #print "Retrieving: "+string
        self.driver.get(string)
        
    def quickFetch(self, string):
        self.restartDriver()
        self.driver.get(string)

    def findElements(self, code, search):
        try:
            element_presence = EC.presence_of_element_located((By.XPATH, search))
            WebDriverWait(self.driver, 5).until(element_presence)
            return self.driver.find_elements(code, search)
        except TimeoutException:
            print 'Loading took too much time!'
    
    def addCID(self):
        self.fetch("https://www.opensecrets.org/members-of-congress/members-list?cong_no=115&cycle=2018")
        for p in range(0,11):
            persons = self.findElements('xpath', '//table[@id="DataTables_Table_0"]/tbody/tr/td/a')
            for person in persons:
                cid = int(person.get_attribute('href').split('=')[1][1:].split('&')[0])
                name = person.text.strip()
                name = name.split(', ')[1]+" "+name.split(', ')[0]
                fname = name.split()[0]
                lname = ' '.join(name.split()[1:])
                if len(lname.split()) > 1 and len(lname.split()[0]) == 1:
                    lname = lname.split()[0]+". "+' '.join(lname.split()[1:])
                self.populator.addCID(fname, lname, cid)
            button = self.findElements('xpath', '//div[@id="DataTables_Table_0_paginate"]/a[2]')[0]
            button.click()
    
    def addCommittee(self):
        self.fetch('http://clerk.house.gov/committee_info/oal.aspx')
        committees = self.findElements('xpath', '//div/table/tbody/tr/td')#[0].text.split('\n')
        for c in range(0, len(committees)/2):
            names = committees[c*2].text.split(', ')
            fname = names[1]
            lname = names[0]
            comms = [com[:-1] for com in committees[c*2+1].text.split('\n')]
            name = fname + ' ' + lname
            if name in self.congr.keys() and '' not in comms:
                self.congr[name]['committees'] = comms


    def addCongress(self, name, link, items):
        vals = {}
        vals['link'] = link
        reference = self.important_index
        for x in range(0,4):
            item = items[min(reference+x,len(items)-1)].text
            if 'State: ' in item:
                if 'state' not in vals.keys():
                    self.important_index += 1
                    vals['state'] = item.split(': ')[1]
            elif 'District' in item:
                self.important_index += 1
                vals['district'] = int(item.split(': ')[1])
            elif 'Party' in item:
                self.important_index += 1
                vals['party'] = item.split(': ')[1][0]
            elif 'Served:' in item:
                self.important_index += 1
                services = item.split('\n')[1:]
                for service in services:
                    ser = service.split(': ')[0]
                    ter = service.split(': ')[1].split('-')
                    if 'Senate' in ser:
                        vals['s'] = int(ter[0])
                    elif 'House' in ser:
                        vals['h'] = int(ter[0])
        self.congr[name] = vals                                              

    def scrapePage(self, target):
        self.fetch(target)
        names = self.findElements("xpath", '//ol[@class="basic-search-results-lists expanded-view"]/li[@class="expanded"]/span/a')
        links = [link.get_attribute('href') for link in names]
        names = [name.text for name in names]
        names = [name.split(', ')[1]+' '+ ' '.join(name.split(', ')[0].split()[1:]) for name in names]
        self.names.extend(names)
        data = self.findElements("xpath", '//ol[@class="basic-search-results-lists expanded-view"]/li[@class="expanded"]/div/div/span')
        for x in range(0, len(names)):
            self.addCongress(names[x], links[x], data)
        self.important_index = 0
        
    def getCongress(self):
        self.scrapePage("https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D&pageSize=250&page=1")
        self.scrapePage("https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D&pageSize=250&page=2")
        self.scrapePage("https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D&pageSize=250&page=3")
        self.addCommittee()
        
    def populateDB(self):
        print "Populating Legislator table"
        self.getCongress()
        for name in self.congr:
            fname = name.split()[0]
            lname = ' '.join(name.split()[1:])
            if '"' in lname:
                lname = ''.join(lname.split('"'))
            datum = self.congr[name]
            #"(FirstName, LastName, Party, State, Job)"
            self.quickFetch(datum['link'])
            #print fname+" "+lname
            link = self.findElements('xpath', '//div[@id="content"]/div/div/div/div/table[2]/tbody/tr[1]/td/a')[0].text
            #print link
            SoH = ''
            year = 0
            if 's' in datum.keys():
                SoH = "S"
                year = datum['s']
            if 'h' in datum.keys():
                if SoH != '' and datum['h'] > datum['s']:#fix this logic
                    SoH = "H"
                    year = datum['h']
                elif SoH == '': 
                    SoH = "H"
                    year = datum['h']
                    
                else: 
                    SoH = "S"
                    year = datum['h']
            party = datum['party']
            state = self.stateDict[datum['state'].upper()]
            link = datum['link']
            self.populator.insertLeg(fname,lname,party,state,SoH,year,link)
            if 'committees' in datum.keys():
                for comm in datum['committees']:
                    if ', Chair' in comm:
                        comm = comm.split(', Chair')[0]
                    if 'House ' in comm:
                        comm = ' '.join(comm.split()[1:])
                    self.populator.insertCombo(fname,lname,comm)
        self.addCID()
        print "Legilator table populated"

    def runTest(self):
        self.addCID()

    def close(self):
        self.populator.close()
        self.driver.quit()

test = CongressScraper()
run = time.time()
test.populateDB()
end = time.time()
print "Test completed in %0.3f seconds." % ((end-run))
test.close()

#print "Exiting"
#print "Closed"
