import time, sys
from dbPopulate import DBPopulate
import requests

from webDriver import Driver
#107.134.155.108
class CongressScraper:
    def __init__(self):
        self.populator = DBPopulate()
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
        self.driver = Driver()

    def addCongress(self, person):
        vals = {}
        data = person.xpath('div[2]/div/span')
        name = person.xpath('span/a')[0].text
        name = name.split(', ')[1]+' '+ ' '.join(name.split(', ')[0].split()[1:])
        link = person.xpath('span/a')[0].attrib['href']
        vals['link'] = link
        try:
            pic = "https://www.congress.gov/" + str(person.xpath('div/div/img')[0].attrib['src'])
        except:
            pic = "none"
        vals['pic'] = pic
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
                vals[da[0].text.strip().lower()[:-1]] = da[1].text.strip()
        self.congr[name] = vals

    def scrapePage(self, target):
        m = 550
        self.driver.fetch(target)
        people = self.driver.find('//li[@class="expanded"]')#//div[@class="quick-search-member"]')
        for x in range(0, len(people)):
            currentItem = len(self.congr.keys())*1.0
            sys.stdout.write("\rProgress: [\%{0:2.1f}]\r".format(100*currentItem/m))
            sys.stdout.flush()
            self.addCongress(people[x])

    def addCommittee(self):
        errs = 0
        self.driver.fetch('http://clerk.house.gov/committee_info/oal.aspx')
        committees = self.driver.find('//div/table/tbody/tr')[1:]#[0].text.split('\n')
        for c in committees:
            try:
                names = c.xpath('td[1]')[0].text.split(', ')
                if len(names) == 1: names = c.xpath('td[1]/em')[0].text.split(', ')
                fname = names[1]
                lname = names[0]
                comms = [com.strip()[:-1] for com in c.xpath('td[2]/text()')]
                name = fname + ' ' + lname
                if name in self.congr.keys() and '' not in comms:
                    self.congr[name]['committees'] = comms
            except:
                errs+=1
                sys.stderr.write('Delegates ignored: '+str(errs)+'\r')
        sys.stdout.write("\n")
        sys.stdout.flush()

    def getCongress(self):
        print "Requesting Legislator Data"
        self.scrapePage("https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D&pageSize=250&page=1")
        self.scrapePage("https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D&pageSize=250&page=2")
        self.scrapePage("https://www.congress.gov/members?q=%7B%22congress%22%3A%22115%22%7D&pageSize=250&page=3")
        sys.stdout.write("\n")
        sys.stdout.flush()
        self.addCommittee()

    def addCID(self):
        print "Getting Legislator CID"
        self.driver.fetch("https://www.opensecrets.org/members-of-congress/members-list?cong_no=115&cycle=2018")
        m = 536
        currentItem = 1.0
        for p in range(0,11):
            persons = self.driver.find('//table[@id="DataTables_Table_0"]/tbody/tr')
            for person in persons:
                sys.stdout.write("\rProgress: [\%{0:2.1f}]\r".format(100*currentItem/m))
                sys.stdout.flush()
                currentItem+=1
                cid = int(person.xpath('td[1]/a/@href')[0].split('=')[1][1:].split('&')[0])
                name = person.xpath('td[1]/a/text()')[0].strip()
                name = name.split(', ')[1]+" "+name.split(', ')[0]
                fname = name.split()[0]
                lname = ' '.join(name.split()[1:])
                if len(lname.split()) > 1 and len(lname.split()[0]) == 1:
                    lname = lname.split()[0]+". "+' '.join(lname.split()[1:])
                state = self.stateDict[person.xpath('td[2]/text()')[0].strip().upper()]
                party = person.xpath('td[3]/text()')[0].strip()
                self.populator.addCID(fname, lname, cid, state, party)
            self.driver.click('//div[@id="DataTables_Table_0_paginate"]/a[2]')
        sys.stdout.write("\n")
        sys.stdout.flush()

    def getContributors(self, legID, cid, cycle): #padd cid string as necessary
        self.driver.fetch("https://www.opensecrets.org/members-of-congress/summary?cid=N"+str(cid).zfill(8)+"&cycle="+str(cycle)+"&type=C")
        individuals = self.driver.find("//body/div/div/div/div/div/div[3]/div[2]/table/tbody/tr") #top indiv
        industries = self.driver.find("//body/div/div/div/div/div/div[3]/div[4]/table/tbody/tr") #top indus
        for x in range(0,len(individuals)):
            individual = individuals[x].xpath('td')
            conID = self.populator.getContributor(individual[0].text, 0)
            self.populator.insertContribution(legID, conID, ''.join(individual[1].text[1:].split(',')), 0, cycle)
            self.populator.insertContribution(legID, conID, ''.join(individual[2].text[1:].split(',')), 1, cycle)
            self.populator.insertContribution(legID, conID, ''.join(individual[3].text[1:].split(',')), 2, cycle)
        for x in range(0,len(industries)):
            industry = industries[x].xpath('td')
            conID = self.populator.getContributor(industry[0].text, 1)
            self.populator.insertContribution(legID, conID, ''.join(industry[1].text[1:].split(',')), 0, cycle)
            self.populator.insertContribution(legID, conID, ''.join(industry[2].text[1:].split(',')), 1, cycle)
            self.populator.insertContribution(legID, conID, ''.join(industry[3].text[1:].split(',')), 2, cycle)

    def getMoney(self):
        print "Getting contributions"
        #select legID, CID from legislator where not isnull(cid);
        legData = self.populator.getContInfo()
        m = len(legData)
        currentItem = 1.0
        for datum in legData:
            #print datum
            sys.stdout.write("\rProgress: [\%{0:2.1f}]\r".format(100*currentItem/m))
            sys.stdout.flush()
            self.getContributors(datum[0], datum[1], 2018)
            currentItem+=1
        sys.stdout.write("\n")
        sys.stdout.flush()
        print "Contributions finished"

    def populateDB(self):
        self.getCongress()
        print "Populating Legislator table"
        m = len(self.congr)
        currentItem = 1.0

        for name in self.congr:

            sys.stdout.write("\rProgress: [\%{0:2.1f}]\r".format(100*currentItem/m))
            sys.stdout.flush()
            currentItem += 1

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
        sys.stdout.write("\n")
        sys.stdout.flush()
        self.addCID()
        self.getMoney()
        print "Legilator table populated"

    def runTest(self):
        self.addCID()

    def close(self):
        self.populator.close()
        self.driver.quit()

#test = CongressScraper()
#run = time.time()
#test.runTest()
#end = time.time()
#print "Test completed in %0.3f seconds." % ((end-run))
#test.close()
#print "Exiting"
#print "Closed"
