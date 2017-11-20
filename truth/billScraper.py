import os
import sys
#import urllib

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from dbPopulate import DBPopulate

def sanitize(text):
    if '"' in text:
        text = ''.join(text.split('"'))
    #if "'" in text:
    #    text = '\''.join(text.split("'"))
    return text 
    
        

class BillScraper:
    def __init__(self, firstCon):
        self.firstCongress = firstCon
        self.populator = DBPopulate()
        self.allBills = []
        print "BillScraper Initializing"
        os.environ['MOZ_HEADLESS'] = '1'
        print "os.environ['MOZ_HEADLESS'] = '1'"
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        print "binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)"
        self.driver = webdriver.Firefox(firefox_binary=binary)

    def fetch(self, string):
        print "Retrieving: "+string
        self.driver.get(string)

    def findElements(self, code, search):
        return self.driver.find_elements(code, search)

    def getText(self, elem):
        return ''.join(elem.get_property('textContent').strip('[]').split(','))

    def correlate(self, numBills):#craetes Dict of Congress # to # of bills
        x = 0
        vals = {}
        while(115-x >= self.firstCongress):
            vals[115-x] = int(self.getText(numBills[x]))
            x += 1
        return vals

    def getBill(self, billNum, congNum, billType):
        if congNum % 10 == 1: congNum = str(congNum)+'st'
        elif congNum % 10 == 2: congNum = str(congNum)+'ns'
        elif congNum % 10 == 3: congNum = str(congNum)+'rd'
        else: congNum = str(congNum)+'th'
        self.fetch("https://www.congress.gov/bill/%s-congress/%s/%s/all-info"%(str(congNum), billType, billNum))

    def getBillsForCongress(self, congNum, numBills):
        pages = numBills/250 + 1
        for p in range(1, pages+1):
            self.scrapeForBills(congNum, p)

    def printInfo(self, ans):
        for x in ans:
            print ans[x]
            print x
            
    def getType(self, bid):
        if 'house-bill' in bid: return 'H.R.'
        elif 'house-amendment' in bid: return 'H.Amdt.'
        elif 'house-resolution' in bid: return 'H.Res.'
        elif 'house-joint-resolution' in bid: return 'H.J.Res.'
        elif 'house-concurrent-resolution' in bid: return 'H.Con.Res.'
        elif 'senate-bill' in bid: return 'S.R.'
        elif 'senate-amendment' in bid: return 'S.Amdt.'
        elif 'senate-resolution' in bid: return 'S.Res.'
        elif 'senate-joint-resolution' in bid: return 'S.J.Res.'
        elif 'senate-concurrent-resolution' in bid: return 'S.Con.Res.'
        else: print("Can't find type for :"+bid)
        
    def getBillDetails(self, billLink, billID, conNum):
        self.fetch(billLink)
        actions = self.findElements('xpath', '//div[@id="allActions-content"]/div/table/tbody/tr/td') # AllActions (date and action, drop 'Action By:'
        cosponsors = self.findElements('xpath', '//div[@id="cosponsors-content"]/div/table/tbody/tr/td/a') # Cosponsors
        committees = self.findElements('xpath', '//div[@id="committees-content"]/div/div/table/tbody/tr[@class="committee"]/th') # Committees
        realatedBills = self.findElements('xpath', '//div[@id="relatedBills-content"]/div/div/table/tbody/tr/td/a') # RelatedBills
        subjects = self.findElements('xpath', '//div[@id="subjects-content"]/div/ul/li/a') # Policy Area
        for act in range(0,len(actions)/2):
            date = actions[act*2].text
            action = sanitize(actions[act*2+1].text.split('\n')[0]) 
            actBy = actions[act*2+1].text.split('\n')[1][11:]
            self.populator.insertAction(billID,date,action,actBy)
        for spon in cosponsors:
            leg = spon.text[5:].split(' [')[0]
            leg = leg.split(', ')[1]+" "+leg.split(', ')[0]
            fname = leg.split()[0]
            lname = sanitize(' '.join(leg.split()[1:]))
            self.populator.insertCosponsor(fname, lname, billID)
        for comm in committees:#TODO: Deal with ()
            comm = comm.text
            if 'House ' in comm:
                comm = comm[6:]
            elif 'Senate ' in comm:
                comm = comm[7:]
            if '(' in comm:
                comm = comm.split(' (')[0]
            self.populator.insertComboBill(billID, comm.strip())
        for bill in realatedBills:
            self.populator.insertRelatedBill(billID, bill.text.strip(), conNum) 
        for subject in subjects:
            self.populator.insertBillPolicy(billID, subject.text.strip())
        
            
    def scrapeForBills(self, congNum, pageNum):
        self.fetch("https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22"+(str(congNum))+"%22%7D&pageSize=250&page="+str(pageNum))
        links = [ x.get_attribute('href') for x in self.findElements('xpath', '//div[@id="main"]/ol/li[@class="expanded"]/span[1]/a')]
        sponsors = [x.text[9:] for x in self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[3]')] # Sponsor + Cosponsor
        brief = [x.text.strip() for x in self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[2]')] # Brief
        for link in range(0,len(links)):
            billLink = links[link].split('?')[0]+'/all-info'
            billName = self.getType(billLink.split('/')[5])+billLink.split('/')[6]
            conNum = int(filter(str.isdigit, str(billLink.split('/')[4])))
            sponsor = ' '.join(sponsors[link].split(' [')[0].split()[1:])
            name = sponsor.split(', ')[1]+" "+sponsor.split(', ')[0]
            fname = name.split()[0]
            lname = sanitize(' '.join(name.split()[1:]))
            title = sanitize(brief[link])
            if len(title) > 255: title = title[0:254]
            
            self.populator.insertBill(billName, conNum, fname, lname, title)
            billID = self.populator.getBillID(billName, conNum)
            self.getBillDetails(billLink, billID, conNum)



    def getAllBills(self):
        self.fetch("https://www.congress.gov/search?q")
        numBills = self.findElements("xpath", '//div[@id="facetbox_congress"]/ul/li/label/a/span')
        congrVals = self.correlate(numBills)
        self.getBillsForCongress(115, 10)
        #for con in congrVals:
        #    self.getBillsForCongress(con, congrVals[con])

    def runTest(self):
        self.getAllBills()
        #self.scrapeForBills(115, 1)
        #self.printInfo(work)

    def close(self):
        self.driver.quit()

test = BillScraper(107)
test.runTest()
test.close()

'''
def scrapeForBills(self, congNum, pageNum):
    self.fetch("https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22"+(str(congNum))+"%22%7D&pageSize=250&page="+str(pageNum))
    ident = self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[1]') # Type and ID
    brief = self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[2]') # Brief
    sponsor = self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[3]') # Sponsor + Cosponsor
    committee = self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[4]') # Comittees
    action = self.findElements("xpath", '//div[@id="main"]/ol/li[@class="expanded"]/span[5]') # Latest Action
    for x in range(0, 3):#len(ident)):
        a = str(congNum)+'-'+ident[x].get_property('textContent').strip().split(' ')[0]
        b = brief[x].get_property('textContent').strip()
        c = sponsor[x].get_property('textContent').strip()[9:]
        d = committee[x].get_property('textContent').strip()[12:]
        e = action[x].get_property('textContent').strip()[14:-13].strip()
        self.allBills.append(Bill(a, b, c, d, e))
'''

print "Exiting"
print "Closed"
