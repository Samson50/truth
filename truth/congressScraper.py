import time
from dbPopulate import DBPopulate
import requests

from lxml import html
from lxml.etree import tostring
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
#107.134.155.108
class CongressScraper:
    def __init__(self):
        self.populator = DBPopulate()
        self.ua = UserAgent()
        self.important_index = 0
        self.congr = {}
        self.testing = True
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
        self.initDriver()

    def initDriver(self):
        self.driver = webdriver.PhantomJS()

    def restartDriver(self):
        self.driver.quit()
        self.initDriver()

    def get(self, string):
        if self.testing: print "Getting: "+string
        page = requests.get(string)
        self.tree = html.fromstring(page.content)
        time.sleep(2)
        #requests.exceptions.Timeout
        #request.get("str", timeout=10)

    def find(self, string):
        return self.tree.xpath(string)

    def fetch(self, string):
        print "Fetching: " +string
        self.driver.get(string)
        time.sleep(1.4)
        self.tree = html.fromstring(self.driver.page_source)
        '''
        if self.testing: print "Retrieving: "+string
        self.driver.get(string)
        '''

    def findElements(self, code, search):
        if self.testing: print "Finding "+search
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
            states = self.findElements('xpath', '//table[@id="DataTables_Table_0"]/tbody/tr/td[2]')
            parties = self.findElements('xpath', '//table[@id="DataTables_Table_0"]/tbody/tr/td[3]')
            for p in range(len(persons)):
                cid = int(persons[p].get_attribute('href').split('=')[1][1:].split('&')[0])
                name = persons[p].text.strip()
                name = name.split(', ')[1]+" "+name.split(', ')[0]
                fname = name.split()[0]
                lname = ' '.join(name.split()[1:])
                if len(lname.split()) > 1 and len(lname.split()[0]) == 1:
                    lname = lname.split()[0]+". "+' '.join(lname.split()[1:])
                state = self.stateDict[states[p].text.strip().upper()]
                party = parties[p].text.strip()
                self.populator.addCID(fname, lname, cid, state, party)
            button = self.findElements('xpath', '//div[@id="DataTables_Table_0_paginate"]/a[2]')[0]
            button.click()

    def addCommittee(self):
        self.fetch('http://clerk.house.gov/committee_info/oal.aspx')
        committees = self.findElements('xpath','//div/table/tbody/tr/td')#[0].text.split('\n')
        for c in range(0, len(committees)/2):
            names = committees[c*2].text.split(', ')
            fname = names[1]
            lname = names[0]
            comms = [com[:-1] for com in committees[c*2+1].text.split('\n')]
            name = fname + ' ' + lname
            if name in self.congr.keys() and '' not in comms:
                self.congr[name]['committees'] = comms


    def addCongress(self, person):
        vals = {}
        #vals['link'] = link
        #data = box.xpath('div/span')
        data = person.xpath('div[2]/div/span')
        name = person.xpath('span/a')[0].text
        name = name.split(', ')[1]+' '+ ' '.join(name.split(', ')[0].split()[1:])
        link = person.xpath('span/a')[0].attrib['href']
        vals['link'] = link
        try:
            pic = "https://www.congress.gov/" + str(person.xpath('div/div/img')[0].attrib['src'])
        except:
            pic = "none"
            #print "pic: "+name
        vals['pic'] = pic
        #dat = person.xpath('/div[2]/div/span')
        for dat in data:
            da = dat.getchildren()
            if 'Served:' in da[0].text:
                for d in da[1].getchildren()[0].getchildren():
                    ser = d.text.strip().split(': ')[0]
                    ter = int(d.text.strip().split(': ')[1].split('-')[0])
                    if 'Senate' in ser:
                        vals['s'] = ter
                    elif 'House' in ser:
                        vals['h'] = ter
            elif 'District:' in da[0].text:
                vals[da[0].text.strip().lower()] = int(da[1].text.strip())
            else:
                #print da[0].text.strip().lower()
                #print da[1].text.strip()
                vals[da[0].text.strip().lower()[:-1]] = da[1].text.strip()
        self.congr[name] = vals

    def scrapePage(self, target):
        #TODO: Finish this implementation
        self.fetch(target)
        #names = self.find('//ol[@class="basic-search-results-lists expanded-view"]/li[@class="expanded"]/span/a')
        people = self.find('//li[@class="expanded"]')#//div[@class="quick-search-member"]')
        #links = [link.attrib['href'] for link in names]
        #names = [name.text for name in names]
        #names = [name.split(', ')[1]+' '+ ' '.join(name.split(', ')[0].split()[1:]) for name in names]
        #pics = self.find('//ol[@class="basic-search-results-lists expanded-view"]/li[@class="expanded"]/span/')
        #boxes = self.find('//li[@class="expanded"]//div[@class="quick-search-member"]')
        #for x in range(0, len(names)):
        for x in range(0, len(people)):
            self.addCongress(people[x])
            #self.addCongress(names[x], links[x], boxes[x])

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
            link = datum['link']
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
            party = datum['party'][0]
            state = self.stateDict[datum['state'].upper()]
            link = datum['link']
            pic = datum['pic']
            #print fname,lname,party,state,SoH,year
            self.populator.insertLeg(fname,lname,party,state,SoH,year,link, pic)
            if 'committees' in datum.keys():
                for comm in datum['committees']:
                    if ', Chair' in comm:
                        comm = comm.split(', Chair')[0]
                    if 'House ' in comm:
                        comm = ' '.join(comm.split()[1:])
                    self.populator.insertCombo(fname,lname,comm)
        print "Getting Legislator CID"
        self.addCID()
        self.getMoney()
        print "Legilator table populated"

    def getContributors(self, legID, cid, cycle): #padd cid string as necessary
        self.fetch("https://www.opensecrets.org/members-of-congress/summary?cid=N"+str(cid).zfill(8)+"&cycle="+str(cycle)+"&type=C")
        #print "Tree"
        #print tostring(self.tree)
        individuals = self.find("//body/div/div/div/div/div/div[3]/div[2]/table/tbody/tr") #top indiv
        industries = self.find("//body/div/div/div/div/div/div[3]/div[4]/table/tbody/tr") #top indus
        for x in range(0,len(individuals)):
            individual = individuals[x].xpath('td')
            #print individual[0].text
            conID = self.populator.getContributor(individual[0].text, 0)
            self.populator.insertContribution(legID, conID, ''.join(individual[1].text[1:].split(',')), 0, cycle)
            self.populator.insertContribution(legID, conID, ''.join(individual[2].text[1:].split(',')), 1, cycle)
            self.populator.insertContribution(legID, conID, ''.join(individual[3].text[1:].split(',')), 2, cycle)
        for x in range(0,len(industries)):
            industry = industries[x].xpath('td')
            #print industry[0].text
            conID = self.populator.getContributor(industry[0].text, 1)
            self.populator.insertContribution(legID, conID, ''.join(industry[1].text[1:].split(',')), 0, cycle)
            self.populator.insertContribution(legID, conID, ''.join(industry[2].text[1:].split(',')), 1, cycle)
            self.populator.insertContribution(legID, conID, ''.join(industry[3].text[1:].split(',')), 2, cycle)

    def getMoney(self):
        print "Getting contributions"
        #select legID, CID from legislator where not isnull(cid);
        legData = self.populator.getContInfo()
        for datum in legData:
            #print datum
            self.getContributors(datum[0], datum[1], 2018)
        print "Contributions finished"


    def runTest(self):
        self.addCID()

    def close(self):
        self.populator.close()
        self.driver.quit()

#test = CongressScraper()
#run = time.time()
#test.getMoney()
#end = time.time()
#print "Test completed in %0.3f seconds." % ((end-run))
#test.close()
#print "Exiting"
#print "Closed"
