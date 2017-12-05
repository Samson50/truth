import sys
import time
import requests
import csv

from random import randint 
from lxml import html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dbPopulate import DBPopulate

def sanitize(text):
    if '"' in text:
        text = ''.join(text.split('"'))
    return text


class BillScraper:
    def __init__(self, firstCon):
        self.firstCongress = firstCon
        self.populator = DBPopulate()
        self.initDriver()
        self.testing = False
        self.maxBill = 0
        
    def initDriver(self):
        self.driver = webdriver.PhantomJS()
        
    def restartDriver(self):
        self.driver.quit()
        self.initDriver()

    def fetch(self, string):
        time.sleep(1.4)
        self.driver.get(string)
        self.tree = html.fromstring(self.driver.page_source)

    def findElement(self, code, search):
        try:
            element_presence = EC.presence_of_element_located((By.XPATH, search))#.join(search.split('/')[:-1])))
            WebDriverWait(self.driver, 3).until(element_presence)
            return self.driver.find_elements(code, search)
        except TimeoutException:
            print 'Loading took too much time!'

    def findElements(self, code, search):
        try:
            return self.driver.find_elements(code, search)
        except TimeoutException:
            print 'Loading took too much time!'
            
    def get(self, string):
        page = requests.get(string)#, header)
        self.tree = html.fromstring(page.content)
        time.sleep(1.2)
    
    def find(self, string):
        return self.tree.xpath(string)

    def getText(self, elem):
        return ''.join(elem.get_property('textContent').strip('[]').split(','))

    def getAction(self, billID):
        actions = self.find('//div[@id="allActions-content"]/div/table/tbody/tr/td') # AllActions (date and action, drop 'Action By:'
        if len(actions) >= 2:
            if actions[1].text == 'Senate' or actions[1].text == 'House' or actions[1].text is None:
                for act in range(0, len(actions)/3):
                    date = actions[act*3].text
                    actBy = actions[act*3+1].text
                    if actBy is not None: actBy = actBy.split()[0]
                    else: actBy = ''
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
        cospons = self.find('//div[@id="cosponsors-content"]/div/table[1]/tbody/tr/td/a') # Cosponsors
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
        committees = self.find('//div[@id="committees-content"]/div/div/table/tbody/tr[@class="committee"]/th') # Committees
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
        realatedBills = self.find('//div[@id="relatedBills-content"]/div/div/table/tbody/tr/td[1]/a') # RelatedBills
        subjects = self.find('//div[@id="subjects-content"]/div/ul/li/a') # Policy Area
        self.getAction(billID)
        self.getCosponsor(billID)
        self.getCommittees(billID)
        for bill in realatedBills:
            self.populator.insertRelatedBill(billID, bill.text.strip())
        for subject in subjects:
            self.populator.insertBillPolicy(billID, subject.text.strip())

    def getType(self, bid):
        if 'house-bill' in bid: return 'H.R.'
        elif 'house-amendment' in bid: return 'H.Amdt.'
        elif 'house-resolution' in bid: return 'H.Res.'
        elif 'house-joint-resolution' in bid: return 'H.J.Res.'
        elif 'house-concurrent-resolution' in bid: return 'H.Con.Res.'
        elif 'senate-bill' in bid: return 'S.'
        elif 'senate-amendment' in bid: return 'S.Amdt.'
        elif 'senate-resolution' in bid: return 'S.Res.'
        elif 'senate-joint-resolution' in bid: return 'S.J.Res.'
        elif 'senate-concurrent-resolution' in bid: return 'S.Con.Res.'
        else: print("Can't find type for :"+bid)

    def billFromLink(self, sponsor, link, title):#Takes simple link to bill
        billLink = link.split('?')[0]+'/all-info'
        billName = self.getType(billLink.split('/')[5])+billLink.split('/')[6]
        conNum = int(filter(str.isdigit, str(billLink.split('/')[4])))
        self.fetch(billLink)
        if len(sponsor) == 0:
            sponsor = "Gai, Nun"
        else:
            sponsor = sponsor.split(' [')[0][5:]
        try:
            name = sponsor.split(', ')[1]+" "+sponsor.split(', ')[0]
            fname = name.split()[0]
            lname = sanitize(' '.join(name.split()[1:]))
            title = sanitize(title)# [0].text.strip())
            if len(title) >= 255: title = title[0:253]
            self.populator.insertBill(billName, conNum, fname, lname, title)
            billID = self.populator.getBillID(billName, conNum)
            self.getBillDetails(billID, conNum)
        except UnboundLocalError as e:
            print "Bill: "+billLink+" Error: "+str(e)
            
    def scrapeCongress(self, congNum, chamber, t, m):
        if m == 0: return
        currentBill = 0
        totTime = 0
        for page in range(1,m/250+2):
            m = m*1.0
            search = 'https://www.congress.gov/search?pageSize=250&page='+str(page)+'&q={%22source%22:%22legislation%22,%22type%22:%22'+t+'s%22,%22congress%22:%22'+str(congNum)+'%22,%22chamber%22:%22'+chamber+'%22}'
            self.fetch(search)
            if t == "amendment": 
                datas = self.find('//div[@id="main"]/ol/li[@class="expanded"]')
                for dat in datas:
                    link = dat.xpath('span[@class="result-heading amendment-heading"]/a[1]')[0].attrib['href']
                    things = dat.xpath('span[@class="result-item"]')
                    spon = ''
                    title = ''
                    for thing in things:
                        idee = thing.xpath('strong')[0].text
                        if 'Sponsor' in idee:
                            spon = thing.xpath('a[1]')[0].text
                        elif 'Amends Bill:' in things: 
                            title = thing.xpath('a[1]')[0].text
                    start = time.time()
                    self.billFromLink(spon, link, title)
                    end = time.time()
                    currentBill += 1
                    totTime += end-start
                    avgTime = totTime/(currentBill*1.0)
                    sys.stdout.write("\rProgress: [\%{0:2.1f}] {1}:{2} {3:4.2f}>\r".format(100*currentBill/m, str(self.tdex), str(currentBill), avgTime))
                    # "="*(int(80*(self.currentBill/m))), " "*(int(80*(1 - self.currentBill/m)))
                    sys.stdout.flush()
            else: 
                datas = self.find('//div[@id="main"]/ol/li[@class="expanded"]')
                for dat in datas:
                    link  = dat.xpath('span[@class="result-heading"]/a[1]')[0].attrib['href']
                    title = dat.xpath('span[@class="result-title"]')[0].text
                    spon = ''
                    for deet in dat.xpath('span[@class="result-item"]'):
                        idee = deet.xpath('strong')[0].text
                        if 'Sponsor' in idee: spon = deet.xpath('a[1]')[0].text
                    start = time.time()
                    self.billFromLink(spon, link, title)
                    end = time.time()
                    currentBill += 1
                    totTime += end-start
                    avgTime = totTime/(currentBill*1.0)
                    sys.stdout.write("\rProgress: [\%{0:2.1f}] {1}:{2} {3:4.2f}>\r".format(100*currentBill/m, str(self.tdex), str(currentBill), avgTime))
                    # "="*(int(80*(self.currentBill/m))), " "*(int(80*(1 - self.currentBill/m)))
                    sys.stdout.flush()

            
    def getCongressFile(self, fcon, lcon):
        t_index = {0:'bill',1:'amendment',2:'resolution',3:'concurrent-resolution',4:'joint-resolution'}
        i = 0
        with open("conr"+str(fcon)+"-"+str(lcon)+".csv", "rb") as condat:
            conrows = csv.reader(condat)#, delimiter=' ', quotechar='|')
            for row in conrows:
                self.tdex = 0
                for cell in row:
                    m = int(cell)
                    if self.tdex > 4:
                        chamber = "House"
                        b=1
                    else: 
                        chamber = "Senate"
                        b=0
                    t = t_index[self.tdex-5*b]
                    self.scrapeCongress(fcon+i, chamber, t, m)
                    self.tdex += 1
                i += 1
            
    def getOneMax(self, congNum, chamber, t):
        if chamber: chamber = 'House'
        else: chamber = 'Senate'
        search = 'https://www.congress.gov/search?q=%7B%22source%22%3A%22legislation%22%2C%22congress%22%3A%5B%22'+str(congNum)+'%22%5D%2C%22chamber%22%3A%22'+chamber+'%22%2C%22type%22%3A%22'+t+'%22%7D'
        if self.testing: print search
        self.fetch(search)
        try:
            ans = int(self.find('//div[@id="main"]/ol/li/span/a')[0].text.split('.')[-1])
        except:
            ans = 0
        return ans
        
    def getMaxes(self, fcon, lcon): #should only need to run fully once
        types = [
                ['bills','amendments','resolutions','concurrent-resolutions','joint-resolutions'],
                ['bills','amendments','resolutions','concurrent-resolutions','joint-resolutions']
                ]
        t_index = {'bills':0,'amendments':1,'resolutions':2,'concurrent-resolutions':3,'joint-resolutions':4}
        vals = {i : list(types) for i in range(lcon,fcon-1,-1)}
        mat = [[0 for x in range(10)] for y in range(lcon-fcon+1)]
        while len(vals.keys()) != 0 :
            k = vals.keys()[randint(0,len(vals.keys())-1)]
            if len(vals[k][0]) != 0 and len(vals[k][1]) != 0: c = randint(0,1)
            elif len(vals[k][1]) == 0: c = 0
            else: c = 1
            try:
                i = randint(0,len(vals[k][c])-1)
            except:
                i = 0
            mat[lcon-k][t_index[vals[k][c][i]]+5*c] = self.getOneMax(k,c,vals[k][c][i])
            w = list(vals[k][c])
            del w[i]
            vals[k][c] = w
            if len(vals[k][0]) == 0 and len(vals[k][1]) == 0:
                del vals[k]
        with open("conr"+str(fcon)+"-"+str(lcon)+".csv", "wb") as f:
            writer = csv.writer(f)
            writer.writerows(mat)


    def runTest(self):
        self.getCongressFile(114,114)

    def close(self):
        self.driver.quit()

test = BillScraper(107)
test.testing = True
run = time.time()
test.runTest()
end = time.time()
print "Test completed in %0.3f seconds." % ((end-run))
test.close()

print "Exiting"
print "Closed"
