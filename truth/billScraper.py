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

    def getConth(self, con):
        if (con%10 == 1): return str(con)+"st"
        if (con%10 == 2): return str(con)+"nd"
        if (con%10 == 3): return str(con)+"rd"
        else: return str(con)+"th"

    def getCongressFile2(self, fcon, lcon):
        t_index = {0:'bill',1:'amendment',2:'resolution',3:'concurrent-resolution',4:'joint-resolution'}
        i = 0
        totTime = 0.0
        with open("conr"+str(fcon)+"-"+str(lcon)+".csv", "rb") as condat:
            conrows = csv.reader(condat)#, delimiter=' ', quotechar='|')
            for row in conrows:
                self.tdex = 0
                for cell in row:
                    m = int(cell)
                    if self.tdex > 4:
                        chamber = "house-"
                        b=1
                    else:
                        chamber = "senate-"
                        b=0
                    t = t_index[self.tdex-5*b]
                    if t == "amendment": billType = "amendment"
                    else: billType = "bill"
                    t = chamber + t
                    billID = (fcon+i)*100000+self.tdex*10000
                    n=1
                    currentBill = 1.0
                    for x in range(1,(m+1)):
                        if self.tdex == 9 and n == 1:
                            n = 34
                            currentBill = n*1.0
                        start = time.time()
                        self.billFromLink2("https://www.congress.gov/"+billType+"/"+self.getConth(fcon+i)+"-congress/"+t+"/"+str(n)+"/all-info",fcon+i,billID+n)
                        end = time.time()
                        currentBill += 1
                        totTime += end-start
                        avgTime = totTime/(currentBill)#*1.0)
                        sys.stdout.write("\rProgress: [\%{0:2.1f}] {1}:{2} {3:4.2f}>\r".format(100*currentBill/m, str(self.tdex), str(currentBill), avgTime))
                        sys.stdout.flush()
                        n += 1
                    self.tdex += 1
                i += 1

    def billFromLink2(self, billLink, conNum, billID):#Takes simple link to bill
        self.fetch(billLink)
        #print billLink
        billName = self.getType(billLink.split('/')[5])+billLink.split('/')[6]
        latest = ''
        fname = ''
        lname = ''
        title = ''
        headers = self.find('//div[@id="content"]/div/div/div[@class="overview"]/table/tbody/tr')
        for head in headers:
            h = head.xpath('th')[0].text
            if 'Latest Action' in h:
                latest = head.xpath('td')[0].text[:60]
                if ' - ' in latest: latest = latest.split()[2].split('/')
                else: latest = latest.split()[0].split('/')
                latest = '-'.join([latest[2],latest[0],latest[1]])
            elif 'Sponsor' in h:
                try:
                    sponsor = head.xpath('td/a')[0].text[5:].split(' [')[0]
                except:
                    sponsor = head.xpath('td')[0].text
                    break
                name = sponsor.split(', ')[1]+" "+sponsor.split(', ')[0]
                fname = name.split()[0]
                lname = sanitize(' '.join(name.split()[1:]))
        try:
            title = self.find('//div[@id="titles_main"]/div/div/div/p')[0].text
        except:
            try: title = self.find('//div[@id="content"]/div[@id="main"]/p')[0].text
            except: return
        try:
            title = sanitize(title.strip())
            if len(title) >= 255: title = title[0:253]
            #print billID, billName, fname, lname, latest
            #print title
            if sponsor == '' and latest == '': return
            self.populator.insertBill(billID, billName, conNum, fname, lname, title, latest)
            #billID = self.populator.getBillID(billName, conNum)
            self.getBillDetails(billID, conNum)
        except UnboundLocalError as e:
            print "Bill: "+billLink+" Error: "+str(e)

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
        self.getCongressFile2(114,114)

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
