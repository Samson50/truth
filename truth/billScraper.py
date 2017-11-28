import os
import sys
import time

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
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
        self.initDriver()
        self.congrVals = self.createBillsDict()
        self.maxBill = 0
        self.currentBill = 0
        
    def initDriver(self):
        print "WebDriver Initializing"
        os.environ['MOZ_HEADLESS'] = '1'
        print "os.environ['MOZ_HEADLESS'] = '1'"
        binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)
        print "binary = FirefoxBinary('C:\\Program Files\\Mozilla Firefox\\firefox.exe', log_file=sys.stdout)\n"
        self.driver = webdriver.Firefox(firefox_binary=binary)
        self.driver.implicitly_wait(3)
        
    def restartDriver(self):
        self.driver.quit()
        self.initDriver()

    def fetch(self, string):
        #print "Retrieving: "+string
        try: 
            self.driver.get(string)
        except TimeoutException as e:
            print "Web driver crashed on: "+string
            print e
            print "Restarting and retrying\n"
            self.restartDriver()
            try:
                self.driver.get(string)
            except:
                print "Too many things went wrong: "+string
                print str(sys.exc_info()[0])+"\n"
                self.driver.quit() 
                sys.exit(1) 

    def findElement(self, code, search):
        #print "Finding: "+search
        try:
            element_presence = EC.presence_of_element_located((By.XPATH, search))#.join(search.split('/')[:-1])))
            #myElem =
            WebDriverWait(self.driver, 3).until(element_presence)
            return self.driver.find_elements(code, search)
        except TimeoutException:
            print 'Loading took too much time!'

    def findElements(self, code, search):
        #print "Finding: "+search
        try:
            element_presence = EC.presence_of_element_located((By.XPATH, '//*'))#.join(search.split('/')[:-1])))
            #myElem =
            WebDriverWait(self.driver, 3).until(element_presence)
            return self.driver.find_elements(code, search)
        except TimeoutException:
            print 'Loading took too much time!'


    def getText(self, elem):
        return ''.join(elem.get_property('textContent').strip('[]').split(','))

    def correlate(self, numBills):#craetes Dict of Congress # to # of bills
        vals = {}
        for x in range(0, len(numBills)):
            vals[93+x] = int(self.getText(numBills[x]))
        return vals

    def createBillsDict(self):
        self.fetch("https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%7D")
        numBills = self.findElements("xpath", '//div[@id="facetbox_congress"]/ul/li/label/a/span')
        return self.correlate(numBills)

    def getAction(self, billID):
        actions = self.findElements('xpath', '//div[@id="allActions-content"]/div/table/tbody/tr/td') # AllActions (date and action, drop 'Action By:'
        if len(actions) >= 2:
            if actions[1].text == 'Senate' or actions[1].text == 'House' or actions[1].text.strip() == '':
                for act in range(0, len(actions)/3):
                    date = actions[act*3].text
                    actBy = actions[act*3+1].text.strip()
                    if actBy != '': actBy = actBy.split()[0]
                    action = sanitize(actions[act*3+2].text.strip())
                    if len(action) >= 255: action = action[:255]
                    self.populator.insertAction(billID,date,action,actBy)
            else:
                for act in range(0,len(actions)/2):
                    date = actions[act*2].text
                    action = sanitize(actions[act*2+1].text.split('\n')[0])
                    if len(action) >= 255: action = action[:255]
                    if (actions[act*2+1].text.strip().split('\n')) == 2:
                        actBy = actions[act*2+1].text.split('\n')[1].strip()
                    else: actBy = ''
                    self.populator.insertAction(billID,date,action,actBy)

    def getCosponsor(self, billID):
        cospons = self.findElements('xpath', '//div[@id="cosponsors-content"]/div/table[1]/tbody/tr/td/a') # Cosponsors
        if "Cosponsors Who Withdrew" in cospons:
            stopper = cospons.index("Cosponsors Who Withdrew")
            cospons = cospons[:stopper]
        for spon in cospons:
            leg = spon.text[5:].split(' [')[0]
            leg = leg.split(', ')[1]+" "+leg.split(', ')[0]
            fname = leg.split()[0]
            lname = sanitize(' '.join(leg.split()[1:]))
            self.populator.insertCosponsor(fname, lname, billID)

    def getCommittees(self, billID):
        committees = self.findElements('xpath', '//div[@id="committees-content"]/div/div/table/tbody/tr[@class="committee"]/th') # Committees
        for comm in committees:#TODO: Deal with ()
            comm = comm.text
            if 'House ' in comm:
                comm = comm[6:]
            elif 'Senate ' in comm:
                comm = comm[7:]
            if '(' in comm:
                comm = comm.split(' (')[0]
            self.populator.insertComboBill(billID, comm.strip())

    def getBillDetails(self, billID, conNum):
        realatedBills = self.findElements('xpath', '//div[@id="relatedBills-content"]/div/div/table/tbody/tr/td/a') # RelatedBills
        subjects = self.findElements('xpath', '//div[@id="subjects-content"]/div/ul/li/a') # Policy Area
        self.getAction(billID)
        self.getCosponsor(billID)
        self.getCommittees(billID)
        for bill in realatedBills:
            self.populator.insertRelatedBill(billID, bill.text.strip(), conNum)
        for subject in subjects:
            self.populator.insertBillPolicy(billID, subject.text.strip())

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

    def billFromLink(self, link):#Takes simple link to bill
        billLink = link.split('?')[0]+'/all-info'
        billName = self.getType(billLink.split('/')[5])+billLink.split('/')[6]
        conNum = int(filter(str.isdigit, str(billLink.split('/')[4])))
        self.fetch(billLink)
        try:
            sponsor = self.findElements('xpath', '//div[@id="content"]/div/div/div/table/tbody/tr/td/a')
            title = self.findElements('xpath', '//div[@id="titles_main"]/div/div/div/p')
            sponsor = sponsor[0].text
            sponsor = ' '.join(sponsor.split(' [')[0].split()[1:])
            name = sponsor.split(', ')[1]+" "+sponsor.split(', ')[0]
            fname = name.split()[0]
            lname = sanitize(' '.join(name.split()[1:]))
            title = sanitize(title[0].text.strip())
            if len(title) >= 255: title = title[0:253]
            self.populator.insertBill(billName, conNum, fname, lname, title)
            billID = self.populator.getBillID(billName, conNum)
            self.getBillDetails(billID, conNum)
        except UnboundLocalError as e:
            print "Bill: "+billLink+" Error: "+str(e)
        except:
            sys.stdout.write("\rIndex Error: {0}\n\r".format(billLink))
            sys.stdout.flush()

    def getBillText(self, billNum, congNum, billType):
        if congNum % 10 == 1: congNum = str(congNum)+'st'
        elif congNum % 10 == 2: congNum = str(congNum)+'nd'
        elif congNum % 10 == 3: congNum = str(congNum)+'rd'
        else: congNum = str(congNum)+'th'
        self.fetch("https://www.congress.gov/bill/%s-congress/%s/%s/text"%(str(congNum), billType, billNum))
        #text = self.findElements('xpath', '//div[@id="main"]/div/table[@class="lbexTableStyleEnr"]')[0]
        text = self.findElements('xpath', '//div[@id="main"]/div[2]')[0]
        print len(text.get_attribute('innerHTML'))
        
    def getDownTo(self, congStr, type, maxBill):
        for bill in range(maxBill,1,-1):
            billLink = "https://www.congress.gov/bill/"+congStr+"-congress/"+type+"/"+str(bill)+"/all-info"
            self.getBillFromLink(billLink)
    
    def getFromFile(self, fileName):
        bills = open(fileName, 'r').readlines
        for bill in bills:
            self.getBillFromLink(bill)
        
    def scrapeForBillsByType(self, congNum, pageNum, t):
        self.fetch("https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22"+str(congNum)+"%22%2C%22type%22%3A%5B%22"+t+"%22%5D%7D&pageSize=250&page="+str(pageNum))
        links = [ x.get_attribute('href') for x in self.findElements('xpath', '//div[@id="main"]/ol/li[@class="expanded"]/span[1]/a')]
        for link in links:
            self.billFromLink(link)
        
    def scrapeForBills(self, congNum, pageNum):
        self.fetch("https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22"+(str(congNum))+"%22%7D&pageSize=250&page="+str(pageNum))
        links = [ x.get_attribute('href') for x in self.findElements('xpath', '//div[@id="main"]/ol/li[@class="expanded"]/span[1]/a')]
        totTime = 0
        for link in links:
            start = time.time()
            self.billFromLink(link)
            end = time.time()
            self.currentBill += 1
            totTime += end-start
            avgTime = totTime/(self.currentBill*1.0)
            sys.stdout.write("\rProgress: [{0}{1}] {2}: {3:4.2f}>".format("="*(100*(self.currentBill/self.maxBill)), " "*(100*(1 - self.currentBill/self.maxBill)), str(self.currentBill), avgTime))
            sys.stdout.flush()
            
    def getBillsForCongressByType(self, congNum, numBills, t):
        pages = numBills/250 + 1
        for p in range(1, pages+1):
            self.scrapeForBillsByType(congNum, p, t)
    
    def getBillsForCongress(self, congNum, numBills):
        self.maxBill = numBills
        pages = numBills/250 + 1
        for p in range(1, pages+1):
            self.scrapeForBills(congNum, p)

    def getBillsByType(self, congNum, t):
        self.fetch('https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%22'+str(congNum)+'%22%7D')
        numBills = self.findElements("xpath", '//div[@id="facetbox_type"]/ul/li/label/a/span')
        vals = {}
        #for x in range(0, len(numBills)):
        vals['bills'] = int(self.getText(numBills[0]))
        vals['amendments'] = int(self.getText(numBills[1]))
        vals['resolutions'] = int(self.getText(numBills[2]))
        vals['joint-resolutions'] = int(self.getText(numBills[3]))
        vals['concurrent-resolutions'] = int(self.getText(numBills[4]))
        self.getBillsForCongressByType(congNum, vals[t], t)

    def getAllBills(self):
        lastCon = max(self.congrVals.keys())
        for con in range(lastCon,93,-1):
            self.getBillsForCongress(con, self.congrVals[con])

    def runTest(self):
        #self.getBillsByType(115, 'bills')
        #self.scrapeForBills1(115, 1)
        #print "No Test"
        self.getBillsForCongress(115, self.congrVals[115])
        #self.getAllBills()
        #self.billFromLink("https://www.congress.gov/bill/115th-congress/house-bill/4431?")


    def close(self):
        self.driver.quit()

test = BillScraper(107)
run = time.time()
test.runTest()
end = time.time()
print "Test completed in %0.3f seconds." % ((end-run))
test.close()

print "Exiting"
print "Closed"

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
